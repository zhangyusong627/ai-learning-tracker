# 提醒功能配置指南（Edge Functions 版本）

## 功能概述

提醒功能支持通过飞书或企业微信发送学习提醒，包括：
- 每日定时提醒
- 每周进度提醒
- 截止日期提醒

## 配置步骤

### 1. 数据库迁移

在 Supabase Dashboard 的 SQL Editor 中执行：

```sql
-- 执行 supabase/setup.sql
```

### 2. 部署 Edge Functions

```bash
# 进入项目目录
cd ai-learning-tracker

# 登录 Supabase CLI
supabase login

# 部署 Edge Functions
supabase functions deploy send-notification
supabase functions deploy check-reminders
```

### 3. 配置 pg_cron 定时任务

1. 在 Supabase Dashboard > Database > Extensions 中启用 `pg_cron`
2. 在 Supabase Dashboard > Database > Extensions 中启用 `http`
3. 配置 app.settings（在 SQL Editor 中执行）：

```sql
-- 替换为你的实际值
ALTER DATABASE SET "app.settings.supabase_url" = 'https://your-project.supabase.co';
ALTER DATABASE SET "app.settings.supabase_service_role_key" = 'your-service-role-key';
```

4. 创建定时任务：

```sql
SELECT cron.schedule(
  'check-reminders',
  '* * * * *',
  $$
  SELECT net.http_post(
    url := current_setting('app.settings.supabase_url') || '/functions/v1/check-reminders',
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || current_setting('app.settings.supabase_service_role_key'),
      'Content-Type', 'application/json'
    )
  );
  $$
);
```

### 4. 配置飞书机器人

1. 在飞书中创建一个群组
2. 添加自定义机器人
3. 复制 Webhook URL（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）
4. 在应用中点击左下角 🔔 按钮，粘贴 Webhook URL

### 5. 配置企业微信机器人

1. 在企业微信群中添加机器人
2. 复制 Webhook URL（格式：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx`）
3. 在应用中点击左下角 🔔 按钮，粘贴 Webhook URL

## 使用说明

1. 打开应用，点击左下角 🔔 按钮
2. 在「通知渠道」中配置飞书或企业微信的 Webhook URL
3. 在「提醒规则」中启用/禁用各种提醒
4. 点击「测试通知」验证配置是否正确
5. 点击「保存设置」完成配置

## 提醒规则说明

| 类型 | 说明 | 默认配置 |
|------|------|----------|
| 每日提醒 | 每天固定时间提醒学习 | 每天 09:00 |
| 每周提醒 | 每周固定时间提醒进度 | 每周一 09:00 |
| 截止提醒 | 课程截止前 N 天提醒 | 7天、3天、1天 |

## 工作原理

- pg_cron 每分钟触发一次 check-reminders 函数
- 函数检查所有启用的提醒规则，判断是否满足触发条件
- 如果满足条件，调用 send-notification 函数发送飞书/微信消息
- 发送记录存储在 reminder_logs 表中

## 注意事项

- 免费版 Supabase 的 Edge Functions 有调用次数限制
- 飞书和企业微信的 Webhook URL 需要妥善保管
- 提醒消息格式会根据渠道自动适配（飞书使用卡片消息，企业微信使用 Markdown）
