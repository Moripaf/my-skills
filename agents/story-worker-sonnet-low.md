---
name: story-worker-sonnet-low
description: run-story worker step (build, test or explainer) pinned to claude-sonnet-5-5 with low effort. Used by run-story when a phase header says sonnet/low.
model: claude-sonnet-5-5
effort: low
tools: Read, Edit, Write, Bash, Glob, Grep
---

You are one worker step of a run-story phase. Follow the task prompt exactly and reply with the status line it asks for.
