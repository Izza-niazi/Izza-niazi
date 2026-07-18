#!/usr/bin/env python3
"""Terminal Quest — a choose-your-path game for your GitHub profile README.

Renders a branching text adventure as nested <details> blocks (GitHub's only
real interactive primitive — click to expand, no JS). Tracks HP + score along
each path, with WIN / GAME OVER endings and ASCII pixel art per scene.

Reusable component: edit STORY / ART / CONFIG below (or import and pass your
own), then run. It injects the markup into README.md between the markers:
    <!-- QUEST:START -->  ...  <!-- QUEST:END -->

    python scripts/make_terminal_quest.py            # inject into README.md
    python scripts/make_terminal_quest.py --print    # print markup to stdout

MIT-friendly: no dependencies, pure stdlib. Fork the STORY and it's your game.
"""
import sys
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# CONFIG — tune the feel.
# --------------------------------------------------------------------------
START = "start"
START_HP = 100
WIN_TAG = "◆ YOU WIN ◆"
OVER_TAG = "▚ GAME OVER ▚"
REPLAY_HINT = "▸ scroll up and pick a different path to play again"

# --------------------------------------------------------------------------
# ART — small ASCII pixel scenes (no blank lines!). Keyed by name.
# --------------------------------------------------------------------------
ART = {
    "boot":   "╔════════════════════╗\n║  PROD  ●  OFFLINE  ║\n║  pager:  RINGING   ║\n╚════════════════════╝",
    "bug":    " ▄▄      ▄▄\n▐░░▌    ▐░░▌\n ▜██████████▛\n    ▀ BUG ▀",
    "trophy": "    ___________\n   |  WIN!!!  |\n   |___   ___|\n       |_|_|",
    "skull":  "  .----------.\n  | ✕      ✕ |\n  |    ▁▁    |\n  |  \\____/  |\n  '----------'",
    "team":   " o   o   o\n/|\\ /|\\ /|\\\n/ \\ / \\ / \\\n one screen, three devs",
    "save":   " [====> 100% ]\n  prod restored\n  ☕ back to bed",
}

# --------------------------------------------------------------------------
# STORY — a scene graph. Each scene: art?, text, hp?, score? (deltas),
# and either `choices` [(label, target_id), ...] or `ending` "WIN"/"OVER".
# Fork this to make your own adventure — the renderer handles the rest.
# --------------------------------------------------------------------------
STORY = {
    "start": {
        "art": "boot",
        "text": "🌙 2:04 AM. PagerDuty is screaming. Production is DOWN. You open your laptop, one eye still asleep.",
        "choices": [
            ("🔍 tail the logs", "logs"),
            ("⏪ roll back the last deploy", "rollback"),
            ("😴 silence the pager, go back to bed", "sleep"),
        ],
    },
    "logs": {
        "art": "bug",
        "text": "The logs scroll past... there it is: a null pointer in the payments service. Classic.",
        "score": 20,
        "choices": [
            ("🩹 write a hotfix yourself", "hotfix"),
            ("📣 wake the on-call team", "team"),
        ],
    },
    "hotfix": {
        "text": "Hotfix ready. Your cursor hovers over the deploy button.",
        "score": 10,
        "choices": [
            ("✅ run the test suite first", "tests_win"),
            ("🚀 YOLO deploy, no tests", "yolo_over"),
        ],
    },
    "tests_win": {
        "art": "trophy",
        "text": "Green across the board. You deploy. Prod recovers. You go back to bed a legend.",
        "score": 50,
        "ending": "WIN",
    },
    "yolo_over": {
        "art": "skull",
        "text": "The hotfix had a typo. Prod is now double-down and the whole team is very awake.",
        "hp": -70, "score": -30,
        "ending": "OVER",
    },
    "team": {
        "art": "team",
        "text": "The team rallies — three sleepy engineers, one shared screen.",
        "score": 15,
        "choices": [
            ("🤝 pair on the fix", "pair_win"),
            ("😤 argue about whose fault it is", "blame_over"),
        ],
    },
    "pair_win": {
        "art": "trophy",
        "text": "Pair Extraordinaire! You squash the bug together and ship. Donuts in the morning. 🍩",
        "score": 40,
        "ending": "WIN",
    },
    "blame_over": {
        "art": "skull",
        "text": "45 minutes of finger-pointing later, prod is still down and morale is lower.",
        "hp": -50,
        "ending": "OVER",
    },
    "rollback": {
        "art": "save",
        "text": "Rollback initiated... prod stabilizes. Breathing room at last.",
        "score": 25,
        "choices": [
            ("📝 write the blameless postmortem", "postmortem_win"),
            ("🙈 pretend it never happened", "debt_over"),
        ],
    },
    "postmortem_win": {
        "art": "trophy",
        "text": "Postmortem filed, root cause fixed for good. You leveled up. 📈",
        "score": 45,
        "ending": "WIN",
    },
    "debt_over": {
        "art": "skull",
        "text": "The bug returns next week. And the week after. Tech-Debt Boss unlocked.",
        "hp": -40,
        "ending": "OVER",
    },
    "sleep": {
        "art": "skull",
        "text": "You wake to 200 Slack messages and a very calm calendar invite titled 'quick chat'.",
        "hp": -100,
        "ending": "OVER",
    },
}


def hp_bar(hp: int) -> str:
    filled = max(0, min(10, round(hp / 10)))
    return "█" * filled + "░" * (10 - filled)


def state_line(hp: int, score: int) -> str:
    return f'<code>HP [{hp_bar(hp)}] {hp:>3}  ·  SCORE {score}</code>'


def render_scene(sid: str, hp: int, score: int, path: list) -> str:
    sc = STORY[sid]
    hp += sc.get("hp", 0)
    score += sc.get("score", 0)
    out = []
    art = ART.get(sc.get("art", ""))
    if art:
        out.append(f"<pre>{escape(art)}</pre>")
    out.append(f'<p>{escape(sc["text"])}</p>')
    out.append(f"<p>{state_line(hp, score)}</p>")

    if sc.get("ending"):
        tag = WIN_TAG if sc["ending"] == "WIN" else OVER_TAG
        out.append(
            f"<p><b>{escape(tag)}</b> — final score <b>{score}</b>. "
            f"<i>{escape(REPLAY_HINT)}</i></p>"
        )
    else:
        for label, target in sc["choices"]:
            if target in path:      # cycle guard for reusable stories
                out.append(f"<p>↺ <i>{escape(label)} — you've looped back here.</i></p>")
                continue
            child = render_scene(target, hp, score, path + [sid])
            out.append(f"<details><summary>{escape(label)}</summary>{child}</details>")
    return "".join(out)


def build() -> str:
    return render_scene(START, START_HP, 0, [])


def inject(readme: str = "README.md",
           a: str = "<!-- QUEST:START -->", b: str = "<!-- QUEST:END -->") -> None:
    html = build()
    with open(readme, encoding="utf-8") as f:
        content = f.read()
    if a not in content or b not in content:
        raise SystemExit(f"Markers {a} / {b} not found in {readme}.")
    i = content.index(a) + len(a)
    j = content.index(b)
    with open(readme, "w", encoding="utf-8") as f:
        f.write(content[:i] + "\n" + html + "\n" + content[j:])
    print(f"injected Terminal Quest into {readme}  ({len(STORY)} scenes)")


if __name__ == "__main__":
    if "--print" in sys.argv:
        print(build())
    else:
        inject()
