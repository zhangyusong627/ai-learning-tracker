# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI 学习计划追踪 (AI Learning Tracker) — a standalone single-page web app that tracks a 90-day AI learning curriculum (12 weeks, 4 modules). Built with vanilla HTML/CSS/JS, no build tools or framework.

## Architecture

**Single file app**: All application logic lives in `index.html` (~1000 lines of inline `<script>`). There is no bundler, transpiler, or package manager.

**Backend**: Supabase (client-side only). The Supabase JS SDK is vendored at `lib/supabase.min.js`. The client is configured inline in the `<script>` block with `SUPABASE_URL` and `SUPABASE_KEY`.

**Database tables** (managed via Supabase):
- `weeks` — 12 weekly entries with module assignment and status (pending/active/done)
- `topics` — daily sub-items under each week (checkbox-completed)
- `notes` — Markdown notes attached to weeks or individual topics
- `notification_channels` — 飞书/微信通知渠道配置
- `reminders` — 提醒规则配置
- `reminder_logs` — 提醒发送记录

**Data seeding**: `seed.sql` truncates and re-inserts all weeks/topics. Use it to reset the database to initial state.

**Vendored libraries** (`lib/`): marked.js (Markdown rendering), Prism.js (syntax highlighting), Supabase JS SDK.

**Course data**: Hardcoded in `COURSE_DATA` array inside `index.html` (~470–640). This defines the curriculum structure, date ranges, materials, and tasks. The `MODULES` array (~647) maps module IDs to display names and week ranges.

## Key Code Sections in index.html

- `initDatabase()` (line ~655) — Seeds Supabase if empty, using `COURSE_DATA`
- `loadData()` (line ~696) — Fetches weeks/topics/notes from Supabase
- `renderModuleTabs()` / `renderTimeline()` — UI rendering
- `renderWeekDetail()` (line ~823) — Expanded week view with topic checkboxes and note editors
- `renderNoteEditor()` (line ~893) — Markdown editor with toolbar, tags, image upload, auto-save (500ms debounce)
- `toggleTopic()` / `updateWeekStatus()` — Checkbox logic that cascades week status (pending→active→done)
- `getTodayWeekNumber()` (line ~686) — Calculates which week the current date falls in, based on `PLAN_START = 2026-06-01`
- `loadReminderSettings()` — 加载通知渠道和提醒规则
- `openReminderPanel()` — 打开提醒设置面板
- `testNotification()` — 测试发送通知

## Development

To run locally, open `index.html` in a browser (or use a static server like `python -m http.server`). No build step required.

To reset the database, run `seed.sql` against the Supabase SQL editor.

To change the curriculum, edit the `COURSE_DATA` array in `index.html` and run `seed.sql` to resync the database.

To setup reminders, run `supabase/setup.sql` against the Supabase SQL editor.

## Conventions

- All UI text is in Chinese (zh-CN).
- Date range header: `2026.6.1 – 8.23` (90 days).
- Four modules: `python-llm`, `rag`, `agent`, `deploy`.
- Status values: `pending`, `active`, `done`.
- Notes use Markdown with preset tags: 重点, 待复习, 已掌握, 疑问.
- Images are uploaded to Supabase Storage bucket `note-images` and inserted as Markdown `![](url)`.
- 提醒功能使用纯前端方案，直接调用飞书/微信 Webhook API。
