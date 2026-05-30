-- pg_cron 定时任务配置
-- 在 Supabase Dashboard 的 SQL Editor 中执行此脚本

-- 1. 确保已启用 pg_cron 扩展
-- 在 Supabase Dashboard > Database > Extensions 中启用 pg_cron

-- 2. 确保已启用 http 扩展
-- 在 Supabase Dashboard > Database > Extensions 中启用 http

-- 3. 获取项目配置（需要替换为你的实际值）
-- 在 Supabase Dashboard > Settings > API 中获取：
-- SUPABASE_URL: 项目 URL（如 https://xxxx.supabase.co）
-- SUPABASE_SERVICE_ROLE_KEY: Service Role Key

-- 4. 配置 app.settings（在 SQL Editor 中执行）
-- 注意：这些设置需要在数据库级别配置
-- ALTER DATABASE SET "app.settings.supabase_url" = 'https://your-project.supabase.co';
-- ALTER DATABASE SET "app.settings.supabase_service_role_key" = 'your-service-role-key';

-- 5. 创建定时任务：每分钟检查一次提醒
-- 注意：需要先完成步骤 3 和 4 的配置

/*
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
*/

-- 6. 查看已创建的定时任务
-- SELECT * FROM cron.job;

-- 7. 查看任务执行历史
-- SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 10;

-- 8. 删除定时任务（如果需要）
-- SELECT cron.unschedule('check-reminders');
