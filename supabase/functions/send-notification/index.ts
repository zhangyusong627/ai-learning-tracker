// Supabase Edge Function: send-notification
// 发送飞书或微信通知

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// 发送飞书消息
async function sendFeishu(webhookUrl: string, title: string, message: string) {
  const payload = {
    msg_type: "interactive",
    card: {
      header: {
        title: { tag: "plain_text", content: title },
        template: "blue",
      },
      elements: [
        {
          tag: "markdown",
          content: message,
        },
      ],
    },
  };

  const response = await fetch(webhookUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Feishu API error: ${response.status}`);
  }

  return await response.json();
}

// 发送企业微信消息
async function sendWechat(webhookUrl: string, title: string, message: string) {
  const payload = {
    msgtype: "markdown",
    markdown: {
      content: `### ${title}\n${message}`,
    },
  };

  const response = await fetch(webhookUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`WeChat API error: ${response.status}`);
  }

  return await response.json();
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { channel_id, title, message } = await req.json();

    // 获取通知渠道信息
    const { data: channel, error: channelError } = await supabase
      .from("notification_channels")
      .select("*")
      .eq("id", channel_id)
      .single();

    if (channelError || !channel) {
      throw new Error("Notification channel not found");
    }

    // 发送通知
    let result;
    if (channel.type === "feishu") {
      result = await sendFeishu(channel.webhook_url, title, message);
    } else if (channel.type === "wechat") {
      result = await sendWechat(channel.webhook_url, title, message);
    } else {
      throw new Error(`Unsupported channel type: ${channel.type}`);
    }

    return new Response(
      JSON.stringify({ success: true, result }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 200 }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 400 }
    );
  }
});
