-- 提醒功能数据库迁移
-- 在 Supabase Dashboard 的 SQL Editor 中执行此脚本

-- 通知渠道表
CREATE TABLE IF NOT EXISTS notification_channels (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL DEFAULT 'default',
  type TEXT NOT NULL CHECK (type IN ('feishu', 'wechat')),
  webhook_url TEXT NOT NULL,
  enabled BOOLEAN DEFAULT true,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 提醒规则表
CREATE TABLE IF NOT EXISTS reminders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL DEFAULT 'default',
  type TEXT NOT NULL CHECK (type IN ('daily', 'weekly', 'deadline', 'custom')),
  enabled BOOLEAN DEFAULT true,
  title TEXT NOT NULL,
  message TEXT,
  config JSONB NOT NULL DEFAULT '{}',
  channel_id UUID REFERENCES notification_channels(id) ON DELETE SET NULL,
  last_sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 提醒发送记录表
CREATE TABLE IF NOT EXISTS reminder_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  reminder_id UUID REFERENCES reminders(id) ON DELETE CASCADE,
  channel_id UUID REFERENCES notification_channels(id) ON DELETE SET NULL,
  status TEXT NOT NULL CHECK (status IN ('success', 'failed')),
  error_message TEXT,
  sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_reminders_user_enabled ON reminders(user_id, enabled);
CREATE INDEX IF NOT EXISTS idx_reminder_logs_reminder_id ON reminder_logs(reminder_id);
CREATE INDEX IF NOT EXISTS idx_notification_channels_user ON notification_channels(user_id);

-- RLS 策略（简化版，单用户场景）
ALTER TABLE notification_channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminder_logs ENABLE ROW LEVEL SECURITY;

-- 允许所有操作（单用户应用，使用 IF NOT EXISTS 避免重复创建）
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all for notification_channels' AND tablename = 'notification_channels') THEN
    CREATE POLICY "Allow all for notification_channels" ON notification_channels FOR ALL USING (true);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all for reminders' AND tablename = 'reminders') THEN
    CREATE POLICY "Allow all for reminders" ON reminders FOR ALL USING (true);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all for reminder_logs' AND tablename = 'reminder_logs') THEN
    CREATE POLICY "Allow all for reminder_logs" ON reminder_logs FOR ALL USING (true);
  END IF;
END $$;
