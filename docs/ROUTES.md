# Writing routes

A **route** is a JSON file that makes Mario play by himself. The mod reads it one step at a time and turns each step into
ordinary SM64 controller input (stick, A, B, Z) — the same buttons you'd press. Nothing teleports Mario or changes the game.

Start one from the launcher's **Routes** tab (pick it, then Play).

Routes live in the `routes/` folder. The ones shipped there cover the five 2019 quests room by room
(`<quest>-r<N>.json`) and whole quests (`<quest>-full.json`).

## The file

```json
{
  "schemaVersion": 1,
  "name": "my-first-route",
  "description": "Walk to the fountain, punch twice, wait.",
  "steps": [
    { "kind": "goto",  "x": -14.0, "z": -7.5 },
    { "kind": "face",  "yaw": 90 },
    { "kind": "punch" },
    { "kind": "punch" },
    { "kind": "wait",  "ticks": 60 }
  ]
}
```

| Top-level key | Required | Meaning |
|---|---|---|
| `schemaVersion` | yes | Always `1`. |
| `name` | yes | 1–64 characters: letters, digits, `.`, `_`, `-`. |
| `steps` | yes | 1–4096 steps. |
| `description`, `notes` | no | Free text / notes for people; ignored by the game. |
| `launch` | no | Read by the launcher, not the game: the quest, room and Mario features the route was written for. Without it the route starts in the quest chosen on the Map tab. A route's quest always starts by itself (even with `quest_autostart = no`), and a room beyond the quest's last one is refused with a message. |
| `style` | no | `"mayhem"` (default) or `"classic"`. See [Mayhem style](#mayhem-style-and-the-route-card). Every route in `routes/` says `"style": "mayhem"`; change it to `"classic"` for the behaviour from before the style existed. |
| `adaptive` | no | `true` (default): fights with `attack: "auto"`, the helpers around a `boss`, and the fight before a `use-door` use the adaptive hit-and-run fight. A plain `fight` (attack `punch`) is unaffected. |
| `engage` | no | Default for `goto`/`use-door`: `true` (default) lets Mario stop and fight when an enemy attacks him on the way. |

The parser is strict on purpose: an unknown key, an unknown step kind or an out-of-range number stops the route
before it starts, with a message naming the step. A file may be at most 256 KiB.

## Units and directions

- Positions are **world meters**: `x` and `z` are the floor plane, `y` is height.
- `yaw` is in **degrees**: `0` faces +Z, `90` faces +X.
- Time is in **ticks**: Mario runs at 30 ticks per second, so `30` = one second.
- Health is in **wedges** (SM64's power meter, 0–8).

## Keys every step accepts

| Key | Default | Meaning |
|---|---|---|
| `kind` | – | The step type (below). |
| `timeoutTicks` | depends on the step | Give up on the step after this many ticks (max 36000 = 20 min). A timed-out step is logged and the route moves on. |
| `note` | – | Free text for people reading the file. Ignored by the game. |
| `mayhem` | the route's `style` | `false` turns the mayhem style off for this one step (`true` turns it on in a classic route). |
| `guard` | `true` | The safety guard refuses input that would walk Mario into lava, a killzone or a deadly drop. Jumps, flips, dives and ground pounds always skip the guard. |

A direction can be given either as `x`,`z` (a point to face/head toward) **or** as `yaw` — not both. `x` and `z`
always go together.

---

## Moving

### `goto` — walk or run to a point
| Key | Default | Meaning |
|---|---|---|
| `x`, `z` (and optional `y`) | – | Where to go. Or use `target: "enemy"` to go to the nearest enemy. |
| `tolerance` | 0.35 | How close counts as "there" (m). |
| `run` | true | Run (full stick) or walk. |
| `stop` | false | Come to a full stop at the end. |
| `nav` | true | Use path-finding around walls and holes. |
| `stuckTicks` | 45 | Ticks without progress before Mario tries to get unstuck. |
| `unstickJumps` | 1 | Jumps to try when stuck (0–5). |
| `radius` | 15 | Search radius for `target`. |
| `engage` | route default | Stop to fight when an enemy targets Mario within ~3.5 m (or hurts him), then continue. Only for `goto` with `x`,`z` (not `target`). |
| `disengageWedges` | 2 | At this health or lower, dodge enemies instead of fighting them (0 = never). |

### `face` — turn on the spot
Exactly one of `yaw`, `x`,`z` or `target` (`"enemy"` etc.). `toleranceDegrees` (10).

### Jumps
| Kind | Keys (defaults) | What Mario does |
|---|---|---|
| `jump` | `holdA` (8), `stick`, direction | Single jump; holding A longer jumps higher. |
| `double-jump` | `holdA`, `holdA2`, `stick`, direction | Jump, land, jump again. |
| `triple-jump` | `holdA`, `holdA2`, `holdA3`, `stick`, direction | Three timed jumps; the highest normal jump. Needs a run-up. |
| `long-jump` | `holdA` (6), direction | Run, crouch, jump: long and low. |
| `backflip` | – | Crouch + jump while standing: very high, lands behind. |
| `side-flip` | direction | Turn around sharply and jump: high. |
| `dive` | direction | Dive forward. |
| `ground-pound` | `holdA` (6), `delay` (6) | Jump, then Z in the air. |
| `slide-kick` | direction | Run, crouch-slide (Z), then B: a low, fast kick that slides on after landing. Carries Mario several metres, so use it with open floor ahead. |
| `wall-kick` | `holdA` (8), direction | Run at a wall, jump, and press A as Mario bounces off it: a wall kick back the way he came. Fails `no-wall` when he lands without touching one. The direction must point at the wall. |

`stick` is 0–1 (how far the stick is pushed).

---

## Fighting

### `fight` — clear nearby enemies
| Key | Default | Meaning |
|---|---|---|
| `radius` | 15 | Fight enemies within this distance. |
| `attack` | `punch` | `punch`, `kick`, `auto` (= adaptive), `adaptive`, or `auto-legacy` (the older simple fight). |
| `adaptive` | route default | With `auto`: use the adaptive fight. |
| `reach` | 1.0 | Attack distance (m). |
| `clearTicks` | 60 | The fight ends after no enemy has been in range for this long. |
| `minWedges` | 0 | Stop fighting if health drops to this. |
| `disengageWedges` | 2 | At this health or lower, stop attacking and retreat to a safe spot. |
| `enemyType` / `excludeType` | – | Only / never fight this enemy type (one or the other). |
| `x`, `z` + `leash` | – | Stay within `leash` m of this point (both needed together). |
| `nav` | true | Path-find around obstacles while fighting. |

**The adaptive fight** knows every enemy type (reach, wind-up, recovery, flying or not, how many hits each Mario move
needs). It stomps enemies that can be stomped, punches only while an enemy is recovering from its own attack, keeps
its distance otherwise, pulls single enemies away from groups, and side-steps or jumps away from shots and charges.

### `boss`
Like `fight`, for a quest boss. `enemyType` (3), `radius` (15), `addRadius` (10, for the boss's helpers),
`attack` `air-kick` (default), `kick` or `auto`, `back` (1.25 m: how far behind the boss's centre Mario stands, 0.9–4), plus `clearTicks` (150),
`minWedges`, `reach`, `nav`, `adaptive`, `disengageWedges`.

### Single moves
`punch` (no keys), `kick` (`style`: `ground` or `air`), `press-b` (`ticks`, default 10).

### `nearest-enemy`
Logs the nearest enemy within `radius` (15) — handy while writing a route.

---

## Doors

### `use-door` — leave the room through the quest door
| Key | Default | Meaning |
|---|---|---|
| `x`, `z` | – | Where to stand: inside the door's unlock area. |
| `yaw` | – | Facing the door, in degrees. |
| `tolerance` | 0.4 | How exactly to stand on the spot. |
| `attempts` | 6 | Tries before giving up. |
| `ticks` | 90 | Wait per attempt for the room to change. |
| `approach` | 5 | Mario starts walking straight at the door from this many metres back. (Enemies within 8 m of the door are fought first.) |
| `aim` | true | The game picks a door by what you're looking at; Mario takes short steps (up to 5 per try) until it picks this door. |
| `excludeType`, `nav`, `adaptive`, `engage`, `disengageWedges` | | As for `goto`/`fight`. |

---

## Tools and objects

| Kind | Keys (defaults) | What it does |
|---|---|---|
| `grab` | `x`,`z` **or** `target` (`bomb`, `jigsaw`, `carriable`), `radius` (15), `attempts` (3) | Pick up the nearest matching object. |
| `release` | `mode` `b` (throw, default) or `z` (drop), `attempts` | Let go of what Mario holds. |
| `carry-place` | object `x`,`z` and/or `name`; `toX`,`toZ` (required); `mode` `drop` (default) or `throw`; `radius` (4); `settleTicks` (90); `attempts`; `tolerance`; `nav` | Fetch an object, carry it to a spot, put it down, and log where it ended up. Used for the Bog's floating pallets. |
| `throw-at` | `target` (`carriable`, `bomb`, `jigsaw`), `radius` (15), `enemyRadius` (25), `enemyType`, `attempts` (3) | Walk to the nearest pot/bomb/object, grab it, turn to the nearest enemy and throw it. With no enemy in range the object is put down again and the step ends `none`. |
| `catch-throw` | `x`,`z`, `radius` (9), `enemyRadius` (25), `standoff` (0), `attempts` (6), `clearTicks` (90), `minWedges`, `enemyType` | Catch a bomb an enemy threw and throw it back. |
| `aim-cannon` | target `x`,`y`,`z` (required), `pitch`, `toleranceDegrees` (2), `attempts` (4), `holdA` (1–8; leave it out for automatic), `muzzle` (`auto`/`forward`/`back`), `holdAim` | Grab a cannon's handle and turn it to point at the target. |
| `light-wick` | `yaw` (required), `tolerance` (0.12), `attempts` (4), `holdA`, `again`, `requireAim` | Bring the lighter/torch to the cannon's wick and fire it. |

---

## Waiting and control flow

| Kind | Keys | What it does |
|---|---|---|
| `wait` | `ticks` | Do nothing for a while. |
| `wait-until` | one or more of `room`, `wedgesMin`, `wedgesMax`, `carry` (`Idle`, `PickupPending`, `Holding`, `ReleasePending`), `questRunning`, `target` (`bomb`/`jigsaw`/`carriable`), `enemyType` (+ optional `x`,`z`, `radius`, `alive`) | Wait until the condition is true, e.g. `{"kind":"wait-until","room":3}` waits for room 3 to load. |
| `log` | `text` (required) | Write a line to the log. |
| `repeat` | `count` (required, ≤ 50), `body` (required, ≤ 64), optional `enemyType` (+ `x`,`z`, `radius`, `clearTicks` 30) | Run the next `body` steps `count` times. With `enemyType`, stop as soon as no enemy of that type is left. Repeats can't be nested. |

---

## Mayhem style and the route card

`"style": "mayhem"` (the default) is for routes that should look like Mario running amok while staying safe. It changes three things, all
through the same controller input as everything else, and never touches the game, its enemies or its scoring:

- A plain `fight` with `attack` `punch` or `kick` (also the default) becomes the adaptive `auto` fight, which already stomps what can be stomped,
  jump-kicks flyers, hits knights from behind and dodges shots. (Not when `adaptive` is `false`.)
- In the adaptive fight a punch becomes a **jump kick** when the enemy's open window still has about a second left, the kick needs fewer hits than
  the punch (kick 100 damage against punch 50) and nothing dangerous lies in the kick's recoil path. The log says `mayhem-finisher`.
  Shielded enemies (knights) are still hit from behind with punches.
- The route card (below) is filled, with a "mayhem" tag.

`"style": "classic"` keeps the old moves exactly (the route card still shows, without the mayhem tag). A step can opt out of a mayhem route with `"mayhem": false`. The movement steps
(`slide-kick`, `wall-kick`, `triple-jump`, `long-jump`, `dive`, `ground-pound`, ...) and `throw-at` are ordinary steps in either style: write
them where you want style.

### The route card

While a route runs, a small card sits on the right of the screen: the route's title (the quest and room, e.g. *Quest for the Golden
Trophy - room 1*), and a log of the last ten things the route did as they happen, newest at the bottom, each sliding in from the right:

```
goto (49.5, 32.5)
fight: elite goblin ×2 — engage
fight: elite goblin ×2 — jump kick
use door
```

The same action repeated shows a count (`punch (6)`); a step that did not end well says so (`goto (3.0, 4.0) timed out`). The card is
display only: it is not part of the route's input, it never takes clicks, and it disappears when the route ends.

## Tips

- Build a route room by room, then join the rooms into a `-full.json`.
- Start each room with `{"kind":"wait-until","room":N}` so a route survives slow loading screens.
- Watch the log while testing: every step writes a `mario-route step=… kind=… result=…` line, and fights write
  `fight-adaptive decision=…` lines explaining each choice.
- `Start-Mario flags route my-route.json` prints the game flags the route would start with, without starting the game;
  the route itself is validated when the game starts it, and a bad key is reported with its step number.
- Routes only ever press buttons. If a route can't do something with buttons, a human couldn't either — and that's the
  point.
