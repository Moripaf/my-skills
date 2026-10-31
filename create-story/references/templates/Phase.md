# Story {{NNN}} / Phase {{NN}} — {{Title}}

Mode: {{worker|interactive}}
Depends on: {{none|02, 03}}
Attended: {{no|yes}}
Builder: {{haiku/low|haiku/medium|haiku/high|sonnet/low|sonnet/medium|none}}
Tester: {{haiku/low|haiku/medium|haiku/high|sonnet/low|sonnet/medium|none}}

## Goal

{{One or two sentences: the state of the code when this phase is done.}}

## Implementation

{{For the build agent. Numbered, concrete steps it can follow without design judgement.}}

1. {{What to change, naming the real file and type (roughly where, no line numbers), the pattern to copy, and the decision it relies on.}}
2. {{Next step.}}

## Tests

{{For the build agent. The tests to write: test project, class name, and the behaviour each test proves.}}

## Verification

{{For the test agent, which sees only the diff, this guide and the script output.}}

Commands:

- `{{test <dir>: <test command narrowed to this phase, e.g. uv run pytest tests/test_<area>.py>}}`
- `{{lint <dir>: <lint command from settings>}}`

Review points:

1. {{Something the tester can confirm or refute from the diff alone.}}

## Exit criteria

{{What must be true before the test agent may return PASS.}}

## Phase prompt

> Run only Phase {{NN}} of Story {{NNN}}. {{One or two sentences on what to do.}} Write the phase report.
