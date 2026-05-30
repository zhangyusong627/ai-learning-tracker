// Supabase Edge Function: check-reminders
// 定时检查并触发提醒（由 pg_cron 调用）

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// 检查每日提醒是否应该触发
function shouldTriggerDaily(config: Record<string, unknown>, lastSentAt: string | null): boolean {
  const targetTime = (config.time as string) || "09:00";
  const [hours, minutes] = targetTime.split(":").map(Number);

  const now = new Date();
  const target = new Date();
  target.setHours(hours, minutes, 0, 0);

  if (now < target) return false;

  if (lastSentAt) {
    const lastSent = new Date(lastSentAt);
    if (lastSent.toDateString() === now.toDateString()) {
      return false;
    }
  }

  return true;
}

// 检查每周提醒是否应该触发
function shouldTriggerWeekly(config: Record<string, unknown>, lastSentAt: string | null): boolean {
  const targetDay = (config.day as string) || "monday";
  const targetTime = (config.time as string) || "09:00";

  const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
  const [hours, minutes] = targetTime.split(":").map(Number);

  const now = new Date();
  const currentDay = days[now.getDay()];
  const target = new Date();
  target.setHours(hours, minutes, 0, 0);

  if (currentDay !== targetDay) return false;
  if (now < target) return false;

  if (lastSentAt) {
    const lastSent = new Date(lastSentAt);
    if (lastSent.toDateString() === now.toDateString()) {
      return false;
    }
  }

  return true;
}

// 检查截止日期提醒是否应该触发
function shouldTriggerDeadline(config: Record<string, unknown>, lastSentAt: string | null): boolean {
  const daysBefore = (config.days_before as number[]) || [7, 3, 1];

  const PLAN_END = new Date("2026-08-23");
  const now = new Date();
  now.setHours(0, 0, 0, 0);

  const daysUntilEnd = Math.ceil((PLAN_END.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

  if (!daysBefore.includes(daysUntilEnd)) return false;

  if (lastSentAt) {
    const lastSent = new Date(lastSentAt);
    if (lastSent.toDateString() === now.toDateString()) {
      return false;
    }
  }

  return true;
}

// 获取默认消息
function getDefaultMessage(type: string): string {
  const PLAN_END = new Date("2026-08-23");
  const now = new Date();

  switch (type) {
    case "daily":
      return "📅 每日学习提醒\n今天也要继续加油哦！";
    case "weekly":
      return "📊 每周进度提醒\n回顾一下本周的学习情况吧！";
    case "deadline": {
      const daysUntilEnd = Math.ceil((PLAN_END.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      return `⏰ 截止日期提醒\n距离课程结束还有 ${daysUntilEnd} 天，加油！`;
    }
    default:
      return "学习提醒";
  }
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // 获取所有启用的提醒
    const { data: reminders, error: remindersError } = await supabase
      .from("reminders")
      .select("*")
      .eq("enabled", true);

    if (remindersError) {
      throw new Error("Failed to fetch reminders");
    }

    const results = [];

    for (const reminder of reminders || []) {
      let shouldTrigger = false;

      switch (reminder.type) {
        case "daily":
          shouldTrigger = shouldTriggerDaily(reminder.config, reminder.last_sent_at);
          break;
        case "weekly":
          shouldTrigger = shouldTriggerWeekly(reminder.config, reminder.last_sent_at);
          break;
        case "deadline":
          shouldTrigger = shouldTriggerDeadline(reminder.config, reminder.last_sent_at);
          break;
      }

      if (shouldTrigger && reminder.channel_id) {
        // 获取通知渠道
        const { data: channel } = await supabase
          .from("notification_channels")
          .select("*")
          .eq("id", reminder.channel_id)
          .single();

        if (channel && channel.enabled) {
          const title = reminder.title;
          const message = reminder.message || getDefaultMessage(reminder.type);

          try {
            const response = await fetch(`${supabaseUrl}/functions/v1/send-notification`, {
              method: "POST",
              headers: {
                Authorization: `Bearer ${supabaseKey}`,
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                channel_id: reminder.channel_id,
                title,
                message,
              }),
            });

            const result = await response.json();

            // 记录发送结果
            await supabase.from("reminder_logs").insert({
              reminder_id: reminder.id,
              channel_id: reminder.channel_id,
              status: result.success ? "success" : "failed",
              error_message: result.error || null,
            });

            // 更新最后发送时间
            if (result.success) {
              await supabase
                .from("reminders")
                .update({ last_sent_at: new Date().toISOString() })
                .eq("id", reminder.id);
            }

            results.push({ reminder_id: reminder.id, success: result.success });
          } catch (error) {
            await supabase.from("reminder_logs").insert({
              reminder_id: reminder.id,
              channel_id: reminder.channel_id,
              status: "failed",
              error_message: error.message,
            });
          }
        }
      }
    }

    return new Response(
      JSON.stringify({ success: true, processed: results.length, results }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 200 }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 400 }
    );
  }
});
