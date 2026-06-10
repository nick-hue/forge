#!/usr/bin/env zsh
#
# build-session.zsh — spin up the Forge dev workspace in tmux.
#
#   Window "code": vim 65% (left) | claude 35% (right)
#   Window "run" : uvicorn        | scratch shell (workers / docker / etc.)
#
# Usage:
#   ./build-session.zsh        # claude
#   ./build-session.zsh c      # claude --continue
#
set -euo pipefail

SESSION="forge"
PROJECT_DIR="${PROJECT_DIR:-$PWD}"

# Optional "c" arg → resume the previous Claude conversation.
CLAUDE_CMD="claude"
if [[ "${1:-}" == "c" ]]; then
  CLAUDE_CMD="claude --continue"
fi

# Already running? Just attach instead of building a second one.
if tmux has-session -t "$SESSION" 2>/dev/null; then
  exec tmux attach -t "$SESSION"
fi

# ── Window 1: "code" ──────────────────────────────────────────────
# Start detached (-d) so we can script the layout before attaching.
tmux new-session -d -s "$SESSION" -n code -c "$PROJECT_DIR"

# Grab the pane IDs instead of trusting index numbers (survives
# pane-base-index settings). split-window -P -F prints the new pane's id.
code_left=$(tmux list-panes -t "${SESSION}:code" -F '#{pane_id}')
code_right=$(tmux split-window -h -t "$code_left" -c "$PROJECT_DIR" -l 35% -P -F '#{pane_id}')

tmux send-keys -t "$code_left"  "vim ."        C-m
tmux send-keys -t "$code_right" "$CLAUDE_CMD"  C-m

# ── Window 2: "run" ───────────────────────────────────────────────
tmux new-window -t "$SESSION" -n run -c "$PROJECT_DIR"

run_left=$(tmux list-panes -t "${SESSION}:run" -F '#{pane_id}')
run_right=$(tmux split-window -h -t "$run_left" -c "$PROJECT_DIR" -P -F '#{pane_id}')

# uvicorn is pre-typed but NOT executed (no C-m): api.main doesn't exist
# until Phase 1. Hit Enter in the pane once it does. Swap to send-keys
# "... C-m" if you'd rather it auto-start.
tmux send-keys -t "$run_left" "uv run uvicorn api.main:app --reload"
# run_right is left as a plain shell for workers / docker / one-off commands.

# Land on the code window, cursor in vim.
tmux select-window -t "${SESSION}:code"
tmux select-pane -t "$code_left"

exec tmux attach -t "$SESSION"
