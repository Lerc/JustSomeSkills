---
name: hideimg
description: Hide the images terminal-images drew in the terminal.
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/hide)
---

Run `<skill-dir>/hide`, where `<skill-dir>` is the directory containing this
`SKILL.md`, and start your reply with its one line of output.

`/hideimg` takes no arguments. Any text after it is a separate message from the
user: carry it out as if they had sent it on its own. With no text after it,
the output line is the whole reply.
