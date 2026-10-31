# Story skills

دو skill برای Claude Code که یک فیچر را برنامه‌ریزی و بعد فاز به فاز با agentهای ارزان پیاده‌سازی و تست می‌کنند. بر پایه [Moripaf/my-skills](https://github.com/Moripaf/my-skills)، عمومی‌شده برای هر پروژه (نه فقط .NET).

## محتوای پوشه

| مسیر | چیست |
|---|---|
| `create-story/` | skill برنامه‌ریزی: کشف کد، سؤال از کاربر، ساخت Prompt، Plan، CheckList و راهنمای فازها در `docs/stories/Story-NNN-*` |
| `create-story/scripts/check_story.py` | چک ساختار استوری (هدرها، موج‌ها، وابستگی‌ها، حلقه) |
| `create-story/scripts/detect_project.py` | تشخیص زبان، runner و دستورهای تست پروژه برای `settings.md` |
| `create-story/references/` | قرارداد استوری و قالب فایل‌ها |
| `run-story/` | skill اجرا: هر موج، builder ← tester ← ادغام ← سند آموزشی |
| `run-story/scripts/verify_phase.py` | چک مکانیکی هر فاز: lint، تست، قانون‌ها (skip، noqa، migration، وابستگی جدید) |
| `run-story/scripts/learn_doc.py` | بسته‌بندی سند آموزشی در استایل خانه و چک آن |
| `run-story/scripts/check_models.py` | بعد از هر موج از transcript چک می‌کند هر agent روی مدل و effort درست اجرا شده |
| `run-story/references/` | دستور explainer و هدر استایل |
| `agents/story-worker-*.md` | شش agent با مدل و effort قفل‌شده (haiku/sonnet × low/medium/high) |
| `run-story-auto.sh` | اجرای خودکار: یک `claude -p` تازه برای هر موج، با orchestrator روی `opus-5.5/medium` |
| `FLOW.md` | نمودار گردش کار |
| `EXPERIMENTS.md` | آزمایش‌ها و نتایج هزینه و کیفیت |

## نصب

```bash
cp -r create-story run-story ~/.claude/skills/
cp agents/*.md ~/.claude/agents/
```

نیاز به Claude Code نسخه 2.1.280 یا بالاتر (برای `claude-opus-5-5`).

## استفاده

- تعاملی: `/create-story <ایده>` و بعد `/run-story 001`
- خودکار (از ریشه پروژه، در Git Bash): `bash run-story-auto.sh 001 [حداکثر موج]`
  - اگر سؤالی پیش بیاید در `NEEDS-USER.md` نوشته می‌شود و اجرا می‌ایستد؛ جواب بده و دوباره اجرا کن.
  - گزارش هر موج در `docs/stories/run-001.log`.

## نتایج تا امروز

- استوری کوچک یک‌فازی: از ۱٫۵۲ به ۰٫۷۴ دلار (۶۲٪ توکن کمتر)، PASS در دور اول.
- استوری واقعی (موج ۳ kb-pipeline): ۱٫۰۸ دلار، همه مدل‌ها درست، بعد از ۲ دور به درستی برای سؤال کاربر ایستاد.

## مشکل باز

دستورهای تست docker در استوری‌ها نباید مسیر مطلق ریپو را mount کنند؛ در worktreeها کد اشتباه تست می‌شود. راه حل برنامه‌ریزی‌شده: placeholder `{repo}` در `verify_phase.py`.
