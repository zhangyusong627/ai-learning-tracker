# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

## Project Overview

AI 学习计划追踪 (AI Learning Tracker) — a standalone single-page web app that tracks a 12-stage AI learning and career sprint curriculum. Built with vanilla HTML/CSS/JS, no build tools or framework.

The app was originally a 90-day learning tracker and has been extended through 2026-09-15.
The local `COURSE_DATA`, weekly plans, and `seed.sql` are synchronized. Supabase stores
checkbox progress and notes; its Week 7 completion status is current, while the older database
title is intentionally overlaid by `applyLocalCoursePlan()` until a separately approved data
update is performed.

The repository now primarily serves as a learning journal, job-hunting evidence hub, and portfolio verification link store.

## Architecture

**Single file app**: All application logic lives in `index.html` (~1000 lines of inline `<script>`). There is no bundler, transpiler, or package manager.

**Backend**: Supabase (client-side only). The Supabase JS SDK is vendored at `lib/supabase.min.js`. The client is configured inline in the `<script>` block with `SUPABASE_URL` and `SUPABASE_KEY`.

**Database tables** (managed via Supabase):
- `weeks` — 12 weekly entries with module assignment and status (pending/active/done)
- `topics` — daily sub-items under each week (checkbox-completed)
- `notes` — Markdown notes attached to weeks or individual topics
- `notification_channels` / `reminders` / `reminder_logs` — 已停用提醒功能的遗留表；暂时保留以便回滚，不再由前端访问

**Data seeding**: `seed.sql` truncates and re-inserts all weeks/topics. Use it to reset the database to initial state.

**Vendored libraries** (`lib/`): marked.js (Markdown rendering), Prism.js (syntax highlighting), Supabase JS SDK.

**Course data**: Hardcoded in `COURSE_DATA` array inside `index.html` (~470–640). This defines the curriculum structure, date ranges, materials, and tasks. The `MODULES` array (~647) maps module IDs to display names and week ranges.

## Learning Materials Structure

All course notes, practice code, sample inputs, and per-week dependency files live under the single top-level `learning/` directory.

```text
learning/
├── README.md                              # Learning-material index and structure rules
├── FULL_TIME_AI_CAREER_SPRINT.md          # Full sprint plan (7.27–9.15)
├── LEARNING_WORKFLOW.md                   # Nine-stage learning workflow
├── week1-python/                          # Legacy name retained
├── week2/
├── week3/
├── week4/
├── week5/                                 # RAG engineering base (completed)
├── week6/                                 # Skill minimum vertical slice (current)
├── week7/                                 # RAG Demo 量化评测与收尾
├── week8/                                 # Agent 最小闭环 + 首批投递
├── week9/                                 # Guardian V0.1
├── week10/                                # Guardian V1
├── week11/                                # Java + AI interview sprint
└── week12/                                # Offer finalization
```

Rules:

- New weekly material must be created under `learning/weekN/`; do not create new `week*` directories at repository root.
- Keep source code, Markdown notes, safe `.env.example` files, dependency manifests, and small reproducible fixtures in Git.
- Never commit virtual environments, `.env` files, API keys, caches, chat histories, local vector databases, or generated runtime data.
- A day directory should contain `notes.md` plus its practice source files. Generated output belongs in an ignored runtime directory.
- When moving learning material, update commands and cross-links that assume repository-root `week*` paths.
- Portfolio code lives in separate repositories (`financial-institution-integration-skill/`, `funding-gateway-ai-guardian/`). This repo stores links, commit hashes, verification commands, and evidence, not source code.

## Current Progress Source

`learning/PROGRESS.md` is the current progress snapshot. Verify it together with the active
week README and the latest portfolio repository commit before stating current status.
Week 6 is complete; Week 7 has closed the portfolio as a RAG engineering Demo with
multi-format parsing, hybrid retrieval, accepted-evidence gates, quantitative evaluation,
and traceable generation evidence. The Java generation path is only a known-pattern,
method-body experiment and must not be described as generic full SPI project generation.
Week 8 starts the Agent minimum loop and first job applications. Historical daily notes
remain snapshots of what was true at that learning stage and must not override newer evidence.

RAG delayed review is limited to the daily 0.5-hour review slot. Do not recreate full-day
“end-to-end retrieval” or Day 31–33 review courses.

## Mandatory Learning Workflow

All current and future course sessions under `learning/` must follow the project learning workflow defined in [`learning/LEARNING_WORKFLOW.md`](learning/LEARNING_WORKFLOW.md). It applies to every subject and is not limited to a specific day or technical domain.

Core requirements:

- Use a complete learning loop: goals and boundaries, prerequisite diagnosis, theory model, minimal practice, engineering extension, three-level assessment, independent decision task, notes and evidence-based evaluation, delayed review.
- Teach required knowledge before testing it. Ask one clearly scoped question at a time; do not combine unrelated questions.
- Keep learning mode distinct from task-completion mode. Limit each teaching step to one main concept, adapt from the learner's response, and switch to direct explanation instead of repeated questioning when confusion persists.
- Distinguish an incorrect answer from an incomplete answer or an ambiguous question.
- Do not treat successful execution or recall of practiced code as proof of mastery.
- Let Codex handle repetitive mechanical edits; require the learner to explain predictions, architecture, boundaries, trade-offs, debugging conclusions, and transfer to new scenarios.
- End every day with a retrospective. Record what worked, what failed, and one or more concrete workflow adjustments for subsequent days.
- Evaluate mastery from observable evidence using the rubric in the workflow document; do not assign stars from intuition.
- Schedule delayed review checkpoints for Day +1, Day +7, and Day +30.
- Evolve the workflow from real course evidence. After enough diverse sessions have validated it, extract it into a reusable learning Skill following the Skill creation and validation process.

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

Learning examples use project-local Python virtual environments. Recreate them from the relevant dependency manifest; never commit the environment directory itself.

**Data sync boundary**: Without explicit user approval, only update local course definitions and documentation. Supabase schema changes, data migrations, destructive resets, and production deployments require separate approval and post-change verification.

## Conventions

- All UI text is in Chinese (zh-CN).
- Date range header: `2026.6.1 – 9.15`.
- Five modules: `python-llm`, `rag`, `skill`, `guardian`, `career`.
- Status values: `pending`, `active`, `done`.
- Notes use Markdown with preset tags: 重点, 待复习, 已掌握, 疑问.
- Images are uploaded to Supabase Storage bucket `note-images` and inserted as Markdown `![](url)`.
- 提醒入口与前端逻辑已移除；数据库规则、通知渠道和 `check-reminders` Cron 均已停用。
- API keys and secrets never committed to code, commits, or logs.
- Interview preparation runs 1.5h daily from 7.28; do not compress it for project scope.
