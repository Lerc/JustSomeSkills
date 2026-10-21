---
name: terminal-images
description: Displays images inline in the user's terminal when it supports the kitty graphics protocol (Ghostty, kitty, WezTerm), by writing straight to the terminal device the agent's UI runs on. Use when showing the user a picture would help, such as a rendered chart, generated image, screenshot or diagram, or when the user asks to see an image in the terminal.
---

# Terminal Images

Resolve `<skill-dir>` as the directory containing this `SKILL.md` and run
`<skill-dir>/termimg` by its absolute path.

## Gate: check first

```bash
<skill-dir>/termimg check
```

Run this once per session, before anything else in this skill. The rest of
this skill applies only when it exits 0. On any other result, set the skill
aside for the session: continue exactly as you would without it, and keep the
check and its outcome out of your reply.

## Show and clear

Shell output is captured, so `termimg` writes the image to the terminal of the
agent's own UI instead of stdout.

```bash
<skill-dir>/termimg show chart.png                     # top-right, at most 1/3 width, 1/2 height
<skill-dir>/termimg show photo.jpg --pos center --cols 40
<skill-dir>/termimg show a.png --pos top-left --id 2   # a second image beside the first
<skill-dir>/termimg clear                              # remove image id 1
<skill-dir>/termimg clear --all
```

- `--pos` is `top-right` (default), `top-left` or `center`; `--at ROW,COL`
  places the top-left corner exactly. `--cols`/`--rows` set the size in cells,
  keeping the aspect ratio when only one is given.
- Showing again with the same `--id` (default 1) replaces that image.
- PNG is sent as is; other formats are converted with ImageMagick when it is
  installed. Render charts and diagrams to PNG first.

When `show` prints a `tell-user:` line, put that line's text in your reply as a
single line. It appears once per session and tells the user about `/hideimg`.

The image floats above the text, covering what is beneath it, and scrolls with
the conversation. Clear it once the user has seen it, or before showing
something unrelated. To inspect an image yourself, read the file with your own
image-viewing tool.

## Setup and environment

- The user's `/hideimg` command comes from the companion `hideimg` skill;
  install it alongside this one.
- Inside tmux, images need `set -g allow-passthrough on` in tmux and
  `TERMINAL_IMAGE_FORCE=1`, since tmux hides the outer terminal's identity.
- `TERMINAL_IMAGE_TTY` targets a specific device; `TERMINAL_IMAGE_FORCE=1`
  tries a terminal that is not on the known list.
