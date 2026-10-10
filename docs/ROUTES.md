# Writing routes

A **route** is a JSON file (a plain text file in a set format) that makes Mario play by himself. The mod reads it one step at a
time and turns each step into ordinary SM64 controller input (stick, A, B, Z), the same buttons you'd press. Nothing teleports
Mario or changes the game.

To start one, open the launcher's **Routes** tab, pick it, then press Play. Routes live in the `routes/` folder. The ones that
ship there cover the five 2019 quests room by room (`<quest>-r<N>.json`) and whole quests (`<quest>-full.json`).

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
| `description`, `notes` | no | Free text and notes for people. The game ignores them. |
| `launch` | no | The launcher reads this, not the game. It names the quest, room and Mario features the route was written for. Without it, the route starts in the quest chosen on the Map tab. A route's quest always starts by itself (even with `quest_autostart = no`). A room beyond the quest's last one is refused with a message. |
| `style` | no | `"mayhem"` (default) or `"classic"`. See [Mayhem style](#mayhem-style-and-the-route-card). Every route in `routes/` says `"style": "mayhem"`. Change it to `"classic"` to get the behaviour from before the style existed. |
| `adaptive` | no | `true` (default): fights with `attack: "auto"`, the helpers around a `boss`, and the fight before a `use-door` use the adaptive hit-and-run fight. A plain `fight` (attack `punch`) isn't affected. |
| `engage` | no | The default for `goto` and `use-door`. `true` (default) lets Mario stop and fight when an enemy attacks him on the way. |

The parser is strict on purpose. An unknown key, an unknown step kind or a number that's out of range stops the route before it
starts, and the message names the step. A file can be at most 256 KiB.

## Units and directions

- Positions are **world meters**. `x` and `z` are the floor plane, and `y` is height.
- `yaw` is in **degrees**. `0` faces +Z and `90` faces +X.
- Time is in **ticks**. Mario runs at 30 ticks per second, so `30` is one second.
- Health is in **wedges** (SM64's power meter, 0–8).

## Keys every step accepts

| Key | Default | Meaning |
|---|---|---|
| `kind` | – | The step type (below). |
| `timeoutTicks` | depends on the step | Give up on the step after this many ticks (max 36000, which is 20 min). A timed-out step is logged and the route moves on. |
| `note` | – | Free text for people reading the file. The game ignores it. |
| `mayhem` | the route's `style` | `false` turns the mayhem style off for this one step. `true` turns it on in a classic route. |
| `guard` | `true` | The safety guard refuses input that would walk Mario into lava, a killzone (an area that kills him) or a deadly drop. Jumps, flips, dives and ground pounds always skip the guard. |

You can give a direction as `x`,`z` (a point to face or head toward) **or** as `yaw`, but not both. `x` and `z` always go
together.

---

## Moving

### `goto`: walk or run to a point
| Key | Default | Meaning |
|---|---|---|
| `x`, `z` (and optional `y`) | – | Where to go. Or use `target: "enemy"` to go to the nearest enemy. |
| `tolerance` | 0.35 | How close counts as "there" (m). |
| `run` | true | Run (full stick) or walk. |
| `stop` | false | Come to a full stop at the end. |
| `nav` | true | Use path-finding to get around walls and holes. |
| `stuckTicks` | 45 | Ticks without progress before Mario tries to get unstuck. |
| `unstickJumps` | 1 | Jumps to try when stuck (0–5). |
| `radius` | 15 | Search radius for `target`. |
| `engage` | route default | Stop to fight when an enemy targets Mario within about 3.5 m (or hurts him), then carry on. Only for `goto` with `x`,`z` (not `target`). |
| `disengageWedges` | 2 | At this health or lower, dodge enemies instead of fighting them (0 = never). |

### `face`: turn on the spot
Give exactly one of `yaw`, `x`,`z` or `target` (`"enemy"` and so on). `toleranceDegrees` is 10 by default.

### Jumps
| Kind | Keys (defaults) | What Mario does |
|---|---|---|
| `jump` | `holdA` (8), `stick`, direction | A single jump. Holding A longer jumps higher. |
| `double-jump` | `holdA`, `holdA2`, `stick`, direction | Jump, land, jump again. |
| `triple-jump` | `holdA`, `holdA2`, `holdA3`, `stick`, direction | Three timed jumps. It's the highest normal jump. Needs a run-up. |
| `long-jump` | `holdA` (6), direction | Run, crouch, jump. It's long and low. |
| `backflip` | – | Crouch and jump while standing. It's very high and lands behind him. |
| `side-flip` | direction | Turn around sharply and jump. It's high. |
| `dive` | direction | Dive forward. |
| `ground-pound` | `holdA` (6), `delay` (6) | Jump, then press Z in the air. |
| `slide-kick` | direction | Run, crouch-slide (Z), then press B. It's a low, fast kick that keeps sliding after landing. It carries Mario several metres, so use it with open floor ahead. |
| `wall-kick` | `holdA` (8), direction | Run at a wall, jump, and press A as Mario bounces off it. That kicks him back the way he came. It fails with `no-wall` when he lands without touching one. The direction must point at the wall. |

`stick` is 0–1 (how far the stick is pushed).

---

## Fighting

### `fight`: clear nearby enemies
| Key | Default | Meaning |
|---|---|---|
| `radius` | 15 | Fight enemies within this distance. |
| `attack` | `punch` | `punch`, `kick`, `auto` (= adaptive), `adaptive`, or `auto-legacy` (the older, simpler fight). |
| `adaptive` | route default | With `auto`: use the adaptive fight. |
| `reach` | 1.0 | Attack distance (m). |
| `clearTicks` | 60 | The fight ends after no enemy has been in range for this long. |
| `minWedges` | 0 | Stop fighting if health drops to this. |
| `disengageWedges` | 2 | At this health or lower, stop attacking and retreat to a safe spot. |
| `enemyType` / `excludeType` | – | Only fight this enemy type, or never fight it (use one or the other). |
| `x`, `z` + `leash` | – | Stay within `leash` m of this point (you need both together). |
| `nav` | true | Path-find around obstacles while fighting. |

**The adaptive fight** knows every enemy type: its reach, its wind-up, its recovery, whether it flies, and how many hits each
Mario move needs. It stomps what can be stomped and punches only while an enemy is recovering from its own attack. The rest of
the time it keeps its distance. It also pulls single enemies away from groups, and side-steps or jumps away from shots and
charges.

### `boss`
This works like `fight`, but for a quest boss. The keys are `enemyType` (3), `radius` (15), `addRadius` (10, for the boss's
helpers), `attack` (`air-kick` by default, or `kick` or `auto`) and `back` (1.25 m, how far behind the boss's centre Mario
stands, 0.9–4). It also takes `clearTicks` (150), `minWedges`, `reach`, `nav`, `adaptive` and `disengageWedges`.

### Single moves
`punch` (no keys), `kick` (`style`: `ground` or `air`), `press-b` (`ticks`, default 10).

### `nearest-enemy`
Logs the nearest enemy within `radius` (15). Handy while you write a route.

---

## Doors

### `use-door`: leave the room through the quest door
| Key | Default | Meaning |
|---|---|---|
| `x`, `z` | – | Where to stand, inside the door's unlock area. |
| `yaw` | – | Which way to face the door, in degrees. |
| `tolerance` | 0.4 | How exactly to stand on the spot. |
| `attempts` | 6 | Tries before giving up. |
| `ticks` | 90 | How long to wait per attempt for the room to change. |
| `approach` | 5 | Mario starts walking straight at the door from this many metres back. (Enemies within 8 m of the door are fought first.) |
| `aim` | true | The game picks a door by what you're looking at. Mario takes short steps (up to 5 per try) until it picks this door. |
| `excludeType`, `nav`, `adaptive`, `engage`, `disengageWedges` | | Same as for `goto` and `fight`. |

---

## Tools and objects

| Kind | Keys (defaults) | What it does |
|---|---|---|
| `grab` | `x`,`z` **or** `target` (`bomb`, `jigsaw`, `carriable`), `radius` (15), `attempts` (3) | Pick up the nearest matching object. |
| `release` | `mode` `b` (throw, default) or `z` (drop), `attempts` | Let go of what Mario holds. |
| `carry-place` | object `x`,`z` and/or `name`; `toX`,`toZ` (required); `mode` `drop` (default) or `throw`; `radius` (4); `settleTicks` (90); `attempts`; `tolerance`; `nav` | Fetch an object, carry it to a spot, put it down, and log where it ended up. It's used for the Bog's floating pallets. |
| `throw-at` | `target` (`carriable`, `bomb`, `jigsaw`), `radius` (15), `enemyRadius` (25), `enemyType`, `attempts` (3) | Walk to the nearest pot, bomb or object, grab it, turn to the nearest enemy and throw it. If no enemy is in range, Mario puts the object down again and the step ends `none`. |
| `catch-throw` | `x`,`z`, `radius` (9), `enemyRadius` (25), `standoff` (0), `attempts` (6), `clearTicks` (90), `minWedges`, `enemyType` | Catch a bomb that an enemy threw and throw it back. |
| `aim-cannon` | target `x`,`y`,`z` (required), `pitch`, `toleranceDegrees` (2), `attempts` (4), `holdA` (1–8; leave it out for automatic), `muzzle` (`auto`/`forward`/`back`), `holdAim` | Grab a cannon's handle and turn the cannon to point at the target. |
| `light-wick` | `yaw` (required), `tolerance` (0.12), `attempts` (4), `holdA`, `again`, `requireAim` | Bring the lighter or torch to the cannon's wick and fire the cannon. |

---

## Waiting and control flow

| Kind | Keys | What it does |
|---|---|---|
| `wait` | `ticks` | Do nothing for a while. |
| `wait-until` | one or more of `room`, `wedgesMin`, `wedgesMax`, `carry` (`Idle`, `PickupPending`, `Holding`, `ReleasePending`), `questRunning`, `target` (`bomb`/`jigsaw`/`carriable`), `enemyType` (+ optional `x`,`z`, `radius`, `alive`) | Wait until the condition is true. For example, `{"kind":"wait-until","room":3}` waits for room 3 to load. |
| `log` | `text` (required) | Write a line to the log. |
| `repeat` | `count` (required, ≤ 50), `body` (required, ≤ 64), optional `enemyType` (+ `x`,`z`, `radius`, `clearTicks` 30) | Run the next `body` steps `count` times. With `enemyType`, stop as soon as no enemy of that type is left. You can't nest repeats. |

---

## Mayhem style and the route card

`"style": "mayhem"` (the default) is for routes that should look wild while staying safe. It changes
three things. They all use the same controller input as everything else, and none of them touches the game, its enemies or its
scoring.

- A plain `fight` with `attack` set to `punch` or `kick` (or left at the default) becomes the adaptive `auto` fight. That fight
  already stomps what can be stomped, jump-kicks flyers, hits knights from behind and dodges shots. (This doesn't happen when
  `adaptive` is `false`.)
- In the adaptive fight, a punch becomes a **jump kick** when the enemy's open window still has about a second left, the kick
  needs fewer hits than the punch (kick 100 damage against punch 50), and nothing dangerous lies in the kick's recoil path. The
  log says `mayhem-finisher`. Shielded enemies (knights) still get hit from behind with punches.
- The route card (below) is filled in, with a "mayhem" tag.

`"style": "classic"` keeps the old moves exactly. The route card still shows, without the mayhem tag. A step can opt out of
a mayhem route with `"mayhem": false`. The movement steps (`slide-kick`, `wall-kick`, `triple-jump`, `long-jump`, `dive`,
`ground-pound`, ...) and `throw-at` are ordinary steps in either style. Put them wherever you want them in the route.

### The route card

While a route runs, a small card sits on the right of the screen. It shows the route's title (the quest and room, like *Quest
for the Golden Trophy - room 1*), and a log of the last ten things the route did, as they happen. The newest is at the bottom,
and each one slides in from the right:

```
goto (49.5, 32.5)
fight: elite goblin ×2 — engage
fight: elite goblin ×2 — jump kick
use door
```

If the same action repeats, the card shows a count (`punch (6)`). A step that didn't end well says so (`goto (3.0, 4.0) timed
out`). The card is display only. It isn't part of the route's input, it never takes clicks, and it goes away when the route
ends.

## Tips

- Build a route room by room, then join the rooms into a `-full.json`.
- Start each room with `{"kind":"wait-until","room":N}`, so the route survives slow loading screens.
- Watch the log while you test. Every step writes a `mario-route step=… kind=… result=…` line, and fights write
  `fight-adaptive decision=…` lines that explain each choice.
- `Start-Mario flags route my-route.json` prints the game flags the route would start with, without starting the game. The game
  checks the route itself when it starts it, and it reports a bad key with its step number.
- Routes only ever press buttons. If a route can't do something with buttons, a human couldn't either.
