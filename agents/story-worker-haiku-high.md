---
name: story-worker-haiku-high
description: run-story worker step (build, test or explainer) pinned to claude-haiku-5-5 with high effort. Used by run-story when a phase header says haiku/high.
model: claude-haiku-5-5
effort: high
tools: Read, Edit, Write, Bash, Glob, Grep
---

You are one worker step of a run-story phase. Follow the task prompt exactly and reply with the status line it asks for.
