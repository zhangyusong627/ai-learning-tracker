# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

AI 学习计划追踪 (AI Learning Tracker) — a standalone single-page web app that tracks a 12-stage AI learning and career sprint curriculum (Week 1-12). Built with vanilla HTML/CSS/JS, no build tools or framework.

The app was originally a 90-day learning tracker and has been extended through 2026-09-15. The local `COURSE_DATA`, weekly plans, and Supabase curriculum records are currently synchronized; Supabase additionally stores checkbox progress and notes.

## Architecture

**Single file app**: All application logic lives in `index.html` (~1000 lines of inline `<script>`). There is no bundler, transpiler, or package manager.

**Backend**: Supabase (client-side only). The Supabase JS SDK is vendored at `lib/supabase.min.js`. The client is configured inline in the `<script>` block with `SUPABASE_URL` and `SUPABASE_KEY`.

**Database tables** (managed via Supabase):
- `weeks` — 12 weekly entries with module assignment and status
- `topics` — daily sub-items under each week (checkbox-completed)
- `notes` — Markdown notes attached to weeks or individual topics
- `notification_channels` / `reminders` / `reminder_logs` — 已停用提醒功能的遗留表；暂时保留以便回滚，不再由前端访问

**Data seeding**: `seed.sql` truncates and re-inserts all weeks/topics. Use it to reset the database to initial state.

**Vendored libraries** (`lib/`): marked.js (Markdown rendering), Prism.js (syntax highlighting), Supabase JS SDK.

**Course data**: `COURSE_DATA` in `index.html` is the runtime curriculum structure. Weekly README files provide detailed teaching and acceptance requirements. Supabase stores the synchronized curriculum plus checkbox progress and notes. `seed.sql` is only a destructive full-reset snapshot, not the routine synchronization mechanism.

## Current Status: Full-Time AI Career Sprint (2026.7.27 – 9.15)

The project has entered a full-time AI career transformation and job-hunting sprint. Three parallel tracks:

| Track | Priority | Key Output |
|-------|----------|-----------|
| **Portfolio** (作品集) | Highest | Two independent GitHub projects (金融机构接入 Skill, AI 智能守护) |
| **Learning** (学习) | High | RAG, structured output, Tool Calling, LangGraph, evaluation & safety gates |
| **Job Hunting** (求职) | High | Java + AI interview prep, resume tuning, applications starting 8.12 |

### Week 6-12 Schedule

Current status is maintained in `learning/PROGRESS.md`; this table is the planned schedule,
not a live completion snapshot.

| Week | Dates | Primary Delivery |
|------|-------|-----------------|
| Week 6 | 7.27–8.2 | Day 36 complete; Skill synthetic documents, unified parsing, structured extraction, minimum vertical slice |
| Week 7 | 8.3–8.9 | Skill: three-mode LLM-written Java SPI, human approval, traceability, compile/contract/golden tests |
| Week 8 | 8.10–8.16 | Skill V1: integration, evaluation, recovery, release materials; start applying 8.12 |
| Week 9 | 8.17–8.23 | Guardian V0.1: independent repo, metric simulation, event replay, expert rules, safety validation, audit |
| Week 10 | 8.24–8.30 | Guardian V1: Agent state flow, read-only tools, governance RAG, recommendations, hard gates, approval, rollback |
| Week 11 | 8.31–9.6 | Intensive Java + AI interview preparation built on the daily interview track |
| Week 12 | 9.7–9.15 | Targeted gap-filling from real feedback, continuous applications, Offer finalization |

Timeline and scope-control rules are defined in `learning/FULL_TIME_AI_CAREER_SPRINT.md`.

### Daily Time Allocation

| Duration | Activity |
|----------|----------|
| 3h | Current week's portfolio core implementation |
| 1.5h | New knowledge learning tied to portfolio needs |
| 1.5h | Java / AI interview preparation (must include oral or written practice) |
| 0.5h | Review Day +1 / +7 / +30 |
| 0.5h | Testing, evidence submission, daily retrospective |

### Interview Prep Schedule

From 7.28, fixed 1.5h daily:
- 7.28～8.2: Collections, concurrency, thread pool, JVM, payment gateway project walkthrough
- 8.3～8.9: Spring, transactions, MySQL, Redis, message queues
- 8.10～8.16: Portfolio 1, RAG, structured output, Java code generation & validation
- 8.17～8.23: High concurrency, rate limiting, circuit breaker, dynamic thread pool, guardian baseline
- 8.24～8.30: Agent, tool calling, safety gates, evaluation, system design
- 8.31～9.15: Real-feedback-driven mock interviews & targeted gap-filling

## Key Code Sections in index.html

- `initDatabase()` — Seeds Supabase only when the database is empty, using `COURSE_DATA`
- `applyLocalCoursePlan()` — Overlays local curriculum names while preserving database IDs and progress
- `loadData()` — Fetches weeks/topics/notes from Supabase and applies the local curriculum overlay
- `renderModuleTabs()` / `renderTimeline()` — UI rendering
- `renderWeekDetail()` — Expanded week view with topic checkboxes and note editors
- `renderNoteEditor()` — Markdown editor with toolbar, tags, image upload, auto-save (500ms debounce)
- `toggleTopic()` / `updateWeekStatus()` — Checkbox logic that cascades week status (pending→active→done)
- `getTodayWeekNumber()` — Matches today's date against each `COURSE_DATA` start/end range

## Development

To run locally, open `index.html` in a browser (or use a static server like `python -m http.server`). No build step required.

`seed.sql` is destructive: it truncates weeks, topics, and notes before recreating the curriculum. Use it only for an explicitly approved full reset, never for routine curriculum synchronization.

To change the curriculum, update `COURSE_DATA`, the matching weekly README files, and the reset snapshot in `seed.sql`. Synchronize an existing database with a separate data migration that preserves IDs, completion state, and note relationships.

提醒功能已于 2026-07-27 停用。`supabase/setup.sql`、`supabase/cron-setup.sql` 和相关 Edge Functions 仅作为遗留实现保留，不得重新部署或执行。

**数据同步边界**：没有用户明确授权时，只更新本地课程定义和文档。Supabase 表结构变更、数据迁移、破坏性重置和生产部署必须单独授权并在执行后校验。

## Conventions

- All UI text is in Chinese (zh-CN).
- Date range header: `2026.6.1 – 9.15`.
- Five modules: `python-llm`, `rag`, `skill`, `guardian`, `career`.
- Status values: `pending`, `active`, `done`.
- Notes use Markdown with preset tags: 重点, 待复习, 已掌握, 疑问.
- Images are uploaded to Supabase Storage bucket `note-images` and inserted as Markdown `![](url)`.
- 提醒入口与前端逻辑已移除；数据库规则、通知渠道和 `check-reminders` Cron 均已停用。
- Learning materials go under `learning/` with per-week subdirectories (`week1-python/` through `week12/`).
- API keys and secrets never committed to code, commits, or logs.
- Portfolio code lives in separate repositories; this repo only stores links, commit hashes, verification commands, and evidence.
