# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

AI 学习计划追踪 (AI Learning Tracker) — a standalone single-page web app that tracks a 90-day AI learning curriculum (12 weeks, 4 modules). Built with vanilla HTML/CSS/JS, no build tools or framework.

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
├── README.md       # Learning-material index and structure rules
├── week1-python/   # Legacy Week 1 name retained to avoid unnecessary churn
├── week2/
├── week3/
└── week4/
```

Rules:

- New weekly material must be created under `learning/weekN/`; do not create new `week*` directories at repository root.
- Keep source code, Markdown notes, safe `.env.example` files, dependency manifests, and small reproducible fixtures in Git.
- Never commit virtual environments, `.env` files, API keys, caches, chat histories, local vector databases, or generated runtime data.
- A day directory should contain `notes.md` plus its practice source/files. Generated output belongs in an ignored runtime directory.
- When moving learning material, update commands and cross-links that assume repository-root `week*` paths.

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

- `initDatabase()` (line ~655) — Seeds Supabase if empty, using `COURSE_DATA`
- `loadData()` (line ~696) — Fetches weeks/topics/notes from Supabase
- `renderModuleTabs()` / `renderTimeline()` — UI rendering
- `renderWeekDetail()` (line ~823) — Expanded week view with topic checkboxes and note editors
- `renderNoteEditor()` (line ~893) — Markdown editor with toolbar, tags, image upload, auto-save (500ms debounce)
- `toggleTopic()` / `updateWeekStatus()` — Checkbox logic that cascades week status (pending→active→done)
- `getTodayWeekNumber()` (line ~686) — Calculates which week the current date falls in, based on `PLAN_START = 2026-06-01`
- `testNotification()` — 测试发送通知

## Development

To run locally, open `index.html` in a browser (or use a static server like `python -m http.server`). No build step required.

To reset the database, run `seed.sql` against the Supabase SQL editor.

To change the curriculum, edit the `COURSE_DATA` array in `index.html` and run `seed.sql` to resync the database.

提醒功能已于 2026-07-27 停用。`supabase/setup.sql`、`supabase/cron-setup.sql` 和相关 Edge Functions 仅作为遗留实现保留，不得重新部署或执行。

Learning examples use project-local Python virtual environments. Recreate them from the relevant dependency manifest; never commit the environment directory itself.

## Conventions

- All UI text is in Chinese (zh-CN).
- Date range header: `2026.6.1 – 9.15`（基于实际进度延长到求职收口）。
- Four modules: `python-llm`, `rag`, `agent`, `deploy`.
- Status values: `pending`, `active`, `done`.
- Notes use Markdown with preset tags: 重点, 待复习, 已掌握, 疑问.
- Images are uploaded to Supabase Storage bucket `note-images` and inserted as Markdown `![](url)`.
- 提醒入口与前端逻辑已移除；数据库规则、通知渠道和 `check-reminders` Cron 均已停用。
