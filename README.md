<div align="center">

# Mario for Rec Room (2019)

### *what if Mario got lost in a 2019 Rec Room*

**Super Mario 64's Mario. In the September 9, 2019 build of Rec Room. Offline. Alone. Punching goblins with real N64 physics.**

[![Latest release](https://img.shields.io/github/v/release/Shippy089/SM64-Mario_RecRoom?label=download&color=e52521)](https://github.com/Shippy089/SM64-Mario_RecRoom/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-049cd8)](LICENSE.txt)
![Windows 10/11 x64](https://img.shields.io/badge/Windows-10%20%2F%2011%20x64-fbd000)
![Rec Room 2019-09-09](https://img.shields.io/badge/Rec%20Room-Sept%209%2C%202019-43b047)
![Servers contacted](https://img.shields.io/badge/servers%20contacted-0-555555)
![Goblins](https://img.shields.io/badge/goblins-in%20danger-8b0000)

**[⬇ GRAB THE LATEST RELEASE](https://github.com/Shippy089/SM64-Mario_RecRoom/releases/latest)** · [Install guide](docs/INSTALL.md) · [Make Mario play by himself](docs/ROUTES.md)

made by **Shippy089**, one person, way too many hours

</div>

> [!IMPORTANT]
> **Bring your own stuff.** You need your own **Super Mario 64 (USA) ROM** and your own copy of the **September 9, 2019
> Rec Room client**. Neither one is in here, neither one gets downloaded for you, and the mod never talks to Rec Room's
> servers. Not once. Not even a little.

> [!NOTE]
> This repo holds the docs, the routes and the native build scripts. The thing you actually play (launcher, mod, native
> library, BepInEx loader, all in one zip) lives on the [Releases](https://github.com/Shippy089/SM64-Mario_RecRoom/releases) page.

## ok but what is this

You know Rec Room from 2019? The Rec Center, the Park, the quests with the goblins and the pirates and the giant robot?
Yeah. Mario is in there now.

Not a Mario-shaped hat on your avatar. **Actual Super Mario 64 Mario**, running on [libsm64], so he moves exactly like he did
on the N64: triple jumps, backflips, wall kicks, long jumps, dives, punches, ground pounds, the 8-slice health pie, the
voice, all of it. He just happens to be standing in a 2019 VR social game that has no idea what to do with him.

The Rec Room side stays **untouched**. Same rooms, same enemies, same doors, same quest rules, same scoring. Mario doesn't
get a cheat mode; he has to beat the quests the way they were built. Good luck. The goblins are not nerfed.

It's offline and it's just you. No servers, no other players, no accounts.

## what he can do

- 🏠 **Go anywhere.** The Rec Center, or any other room in your client build (the Park, the Bowling Alley, Paintball maps,
  you name it). Pick it on the **Map** tab. If a room is secretly just a chunk of another room, the log tells you instead of
  exploding.
- ⚔️ **All five 2019 quests.** Golden Trophy, Jumbotron, Crimson Cauldron, Lost Skulls, Crescendo of the Blood Moon. Start
  at the beginning or drop into any room. Mario walks through the doors like a normal person.
- 👊 **Fight.** His punches, kicks and stomps hurt Rec Room enemies. Their swords and arrows hurt him back. (Quests only;
  the Rec Center has nobody to fight, which is probably for the best.)
- 🔥 **Lava is SM64 lava.** Touch it and Mario does the hot-butt hop, screams, loses health and smokes. The quest does NOT
  instantly end like it would for a normal player. It's on by default (`sm64_lava`).
- 📦 **Pick stuff up.** Buttons, pots, traps, bombs, torches, lighters, cannon handles, jigsaw pieces, floating pallets.
  Grab, carry, yeet, all with Mario's own SM64 grab.
- 🪽 **Wing cap.** Triple jump and he flies. He wears it whenever the original game lets you fly (the room allows it, or
  you're holding the Maker Pen), or always, or never. Your call (`wing_cap`).
- ✈️ **Constant flying** (off by default): one steady flight speed, no diving for speed, no stalling out mid-climb.
- 🧱 **A world edge.** SM64's world is tiny: about **150 m** from where Mario starts, in every direction (and up). Past that
  is a solid wall, and orange construction tape fades in when you get close so you don't faceplant into nothing.
- 🎮 **Controllers.** Xbox, PlayStation, N64 USB adapters and other gamepads use SM64's own N64 layout
  ([button tables](docs/INSTALL.md)). Keyboard and mouse still work.
- 🎥 A follow camera you steer, real SM64 sound, and SM64's own power meter on screen (drawn straight from your ROM).
- 🧸 **Casual mode** (off by default): longer reach, softer knockback. For when SM64 combat is being SM64 combat.
- 🤖 **Routes**: JSON files that make Mario play by himself using nothing but controller inputs. No teleporting, no
  cheating, just a robot holding the stick ([docs/ROUTES.md](docs/ROUTES.md)).

## getting it running

**You need:** Windows 10 or 11 (64-bit), the **September 9, 2019 Rec Room client**, and a **Super Mario 64 (USA) ROM**. That's
it. **BepInEx 6** (the mod loader) comes in the zip, and the launcher carries its own .NET, so there's nothing else to install.
[docs/INSTALL.md](docs/INSTALL.md) explains where each thing comes from and what the launcher checks. Budget ~15 minutes the
first time.

1. **Unzip** the release somewhere you can write to: Desktop, Documents, whatever. NOT Program Files, and NOT by
   double-clicking into the zip and running it from in there. Extract it for real.
2. **Double-click `Start-Mario.cmd`.** Windows will probably say it "protected your PC" because the launcher isn't
   code-signed (I am one person, not a company). Hit *More info*, then *Run anyway*.
3. First launch opens a **setup wizard** that digs around your PC (Steam libraries, Downloads, Desktop, Documents, next to
   the launcher) for the Rec Room client, your ROM and the BepInEx pack. Pick with Enter, or hit **A** to take everything it
   found and install. It only reads your files. It never downloads them, never copies them anywhere, never overwrites them.
   Found nothing? Type the path yourself.
4. Hit **P** (or **▶ PLAY**, then Enter). A *Hello Mario* loading bar follows the game as it boots; when it fills up, Mario's
   there. **The very first start takes a few minutes and needs internet once**, because BepInEx downloads Unity's base files and
   sets itself up for the 2019 client. After that it's under a minute.
5. Play. W A S D moves, Space jumps, left click punches and grabs, Shift crouches, the mouse turns the camera
   ([every control](docs/INSTALL.md#controls-keyboard)). Esc pauses Mario's controls.

The launcher has tabs for everything else (Tab or 1–7 to switch, arrows and Enter to change stuff):

| Tab | What's in it |
|---|---|
| Play | The big Play button, what to start, Immortal Mario (testing only), live status (health, room, position) |
| Map | The Rec Center, any other room of your client, any room of the five quests. All checked against your own build. |
| Mario | Fighting, Casual mode, SM64 health meter, SM64 lava, carrying, Wing cap, constant flying, controller, camera, sound |
| Routes | Pick a route file and let Mario play himself |
| Setup | Your file paths, a status check, set up / update, uninstall |
| Advanced | Start the quest immediately, where logs go, the exact flags Play would pass to the game |
| Log | Mario's live log while the game runs |

> [!TIP]
> **Mario only shows up when Rec Room is started from this menu.** Every Play hands the game a one-time pass. Launch Rec Room
> any other way (its own exe, a shortcut, copy-pasted flags) and it's just plain Rec Room with the mod asleep.

A few things also work from a command line: `Start-Mario find` (what setup could use on this PC), `Start-Mario setup --auto`,
`Start-Mario check`, `Start-Mario stop`, `Start-Mario flags`.

## what actually works (honest edition)

Work in progress, made by one person. Here's the truth:

| ✅ Seen working in the game | 🧪 Built and unit-tested, not proven in the game yet |
|---|---|
| Setup, Play and uninstall from the launcher, on a fresh install | Some rooms: 22 of the 28 tried start fine; the 6 StuntRunner courses are only parts of another room |
| Building the native library from a fresh libsm64 download | Carrying and placing objects (pallets) |
| Mario in the Rec Center: controls, camera, sound | Most quest routes (Jumbotron, Crimson Cauldron, Crescendo); a Golden Trophy route fight still times out |
| Starting in the Park with the Wing cap on | Beating a whole quest with an S rank |
| Quests: start, fight, open doors, Mario shows up in the next room | Game controllers: mapping tables only, no real pad tried |
| Fighting goblins and taking damage | Other Rec Room builds (they install as *untested*) |
| Firing a cannon with the lighter (Lost Skulls) | |
| SM64 lava: burn hop, fire puffs, health loss, death ends the quest cleanly | |
| Constant flying, the Wing cap's wings, the orange world-edge tape | |
| Casual mode loading and punches landing | |

## known jank

- **One tested client.** Built and tested on the September 9, 2019 build. Other IL2CPP builds install as *untested* and may
  not work. Builds with anti-cheat, and your live Steam install, get refused every time. The mod never goes near anti-cheat.
- **150 m world.** SM64 runs on 16-bit coordinates, so the world ends about 150 m from where Mario starts. Huge rooms get
  cut off by the wall.
- **Offline and solo.** No online, no other players, no accounts, no scores sent anywhere. Starting mid-quest or with
  Immortal on doesn't count as a full run.
- **Some scenes need their parent room.** A few scenes are only pieces of a bigger room and can't start alone. The launcher
  lists every scene it finds, and the log says when one can't be used.
- **Windows only**, flat screen with keyboard and mouse or a controller. No VR headset.
- **Stuck loading?** The loading bar says what broke in plain words. Full detail is in `BepInEx\LogOutput.log` in the client
  folder (lines starting with `mario-`) and in `logs\<date>\player.log`.

## what's NOT in here

No Rec Room files. No Nintendo ROM data. No decompiled Rec Room code. You bring the client and the ROM, and setup only reads
them. BepInEx ships unmodified with its licences (`BepInEx-pack\` in the release zip). The native Mario library in the zip is
compiled from the open-source [libsm64] sources (see `NOTICE.txt` and `docs/VERSIONS.md`); it contains zero ROM bytes and reads
your ROM at runtime. Want to compile it yourself? You need zig (`docs/INSTALL.md`).

The mod is MIT-licensed ([LICENSE.txt](LICENSE.txt)). Rec Room, Super Mario 64, libsm64 and BepInEx keep their own licences.

**Fan project.** Not affiliated with or endorsed by Rec Room Inc. or Nintendo. Check the terms of the games you use it with
before sharing recordings or builds.

<div align="center">

*now go punch a goblin*

</div>

[libsm64]: https://github.com/libsm64/libsm64
