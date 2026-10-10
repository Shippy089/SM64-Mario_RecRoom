<div align="center">

# Mario for Rec Room (2019)

**Super Mario 64's Mario, inside the September 9, 2019 Rec Room. Offline, by yourself, by the original rules.**

[![Latest release](https://img.shields.io/github/v/release/Shippy089/SM64-Mario_RecRoom?label=download&color=e52521)](https://github.com/Shippy089/SM64-Mario_RecRoom/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-049cd8)](LICENSE.txt)
![Windows 10/11 x64](https://img.shields.io/badge/Windows-10%20%2F%2011%20x64-fbd000)
![Rec Room 2019-09-09](https://img.shields.io/badge/Rec%20Room-Sept%209%2C%202019-43b047)
![Offline only](https://img.shields.io/badge/online-never-555555)

**[⬇ Download the latest release](https://github.com/Shippy089/SM64-Mario_RecRoom/releases/latest)** · [Install guide](docs/INSTALL.md) · [Writing routes](docs/ROUTES.md)

By Shippy089

</div>

> [!IMPORTANT]
> Bring your own **Super Mario 64 (USA) ROM** and your own copy of the **September 9, 2019 Rec Room client**. Neither is
> included or downloaded, and the mod never connects to Rec Room's servers.

> [!NOTE]
> This repository holds the docs, routes and native build scripts. The ready-to-play package (launcher, mod, native
> library and the BepInEx loader) is the zip on the [Releases](https://github.com/Shippy089/SM64-Mario_RecRoom/releases) page.

Play as **Super Mario 64's Mario** inside the September 9, 2019 version of Rec Room — offline, in the Rec Center, in any
other room of that version (the Park, the Bowling Alley, ...) and in all five quests of that time (Quest for the Golden
Trophy, The Rise of Jumbotron, The Curse of the Crimson Cauldron, Isle of Lost Skulls, Crescendo of the Blood Moon).

Mario keeps everything that makes him Mario: his real SM64 movement and physics (from [libsm64]), his jumps, flips,
wall kicks, punches and dives, his 8-wedge health and his sounds. The Rec Room world stays exactly as it was in 2019 —
its rooms, enemies, doors, scoring and quest logic are untouched. Mario plays the original quests by the original rules.

You play alone and offline: the mod never connects to Rec Room's servers, and there are no other players.

**What you can do**

- **Start in any room.** Free play in the Rec Center, or pick any other room of your client build on the **Map** tab
  (`hangout` in `mario.ini`). The launcher finds the rooms in your own client; a room that is only part of another room
  says so in the log instead of loading.
- **Quests.** Start a quest, or any room of one, and play it room to room with Mario coming through the doors.
- **Combat.** Mario's punches, kicks and stomps hurt Rec Room enemies; their attacks hurt Mario (in quests: the
  Rec Center and the other rooms have no combat system to plug into).
- **Lava** works like SM64 lava: Mario burns, hops up with his "hot" voice and loses health, with fire and smoke puffs,
  instead of the quest ending on the spot (`sm64_lava`, on by default).
- **Carrying.** Buttons, pots, traps, bombs, torches, lighters, cannon handles, jigsaw pieces and floating pallets —
  picked up, carried and thrown with Mario's own grab.
- **Wing cap.** SM64's flight cap: a triple jump becomes flight, and the cap grows wings. It is worn whenever the original
  game lets you fly (the room allows it, or you hold the Maker Pen), or always / never if you choose (`wing_cap` in
  `mario.ini`, or the Mario tab). With the testing-only Immortal switch on, Mario also wears the Metal cap.
- **Constant flying** (off by default; `constant_flying`, or the Mario tab): with the Wing cap on, Mario flies at one steady
  speed instead of SM64's own speed build-up (no diving to gain speed, no stalling in a climb).
- **A world edge.** SM64's world is small: Mario can go about **150 m** from the spot where he starts, in every direction
  (and up). There he meets a solid wall. Within about 12 m of it, orange construction tape fades in on the wall, so you can see
  where flying has to stop. Most rooms are far smaller than that; a long flight can reach it.
- **Game controllers.** Xbox, PlayStation, N64 USB adapters and other gamepads play Mario with SM64's own N64 layout
  ([button tables](docs/INSTALL.md)); the keyboard and mouse keep working (`controller`, `controller_deadzone`).
- A follow camera you steer, SM64 sound, and SM64's own power meter on screen (drawn from your ROM).
- **Casual mode** (off by default): more reach and softer knockback, for people who find SM64 fights too hard.
- **Routes**: JSON files that make Mario play by himself, using only controller input ([docs/ROUTES.md](docs/ROUTES.md)).

## Quick start

**You need** Windows 10 or 11 (64-bit) and two things only you can supply: the **September 9, 2019 Rec Room
client** and a **Super Mario 64 (USA) ROM**. The **BepInEx 6** mod loader is included (`BepInEx-pack\`). [docs/INSTALL.md](docs/INSTALL.md) says where to
get each and what the launcher checks. Allow about 15 minutes the first time.

1. **Unzip** the release into a folder you can write to (your Desktop or Documents — not Program Files, and not from inside
   the zip window).
2. **Double-click `Start-Mario.cmd`.** (Windows may say it "protected your PC" because the launcher is not code-signed:
   choose *More info*, then *Run anyway*.)
3. The first time, a **setup wizard** looks on your PC for the Rec Room client, your ROM and the BepInEx pack, and lists what
   it found (Steam libraries, Downloads, Desktop, Documents, next to the launcher). Pick one with Enter, or press **A** to use
   everything it found and install it into the client folder. It only reads, never downloads or copies those files, and never
   overwrites yours. Nothing found? Type a path instead.
4. Press **P** (or select **▶ PLAY** and press Enter). A *Hello Mario* loading bar follows the game while it starts; when it
   fills up, Mario is there. **The very first start takes a few minutes and needs the internet once**: BepInEx downloads
   Unity's base files and prepares itself for the 2019 client. Later starts take under a minute.
5. Play. Keyboard: W A S D move, Space jumps, left mouse button punches and grabs, Shift crouches, the mouse turns the camera
   ([all controls](docs/INSTALL.md#controls-keyboard)). Esc pauses Mario's controls.

The launcher has tabs for everything else (Tab or 1–7 to switch, arrow keys and Enter to change things):

| Tab | What it does |
|---|---|
| Play | The Play button, what to start, Immortal Mario (testing only), and live status (Mario's health, room, position) |
| Map | Pick the Rec Center, any other room of your client, or any room of the five quests. Each map is checked against your own client build. |
| Mario | Fighting, Casual mode (easier fights, off by default), SM64 health meter, SM64 lava, carrying, Wing cap, constant flying, game controller, camera, sound |
| Routes | Pick a route file for Mario to play by himself |
| Setup | Your file paths, a status check, set up / update, uninstall |
| Advanced | Start the quest immediately, where logs go, and a button that shows the flags Play would pass to the game |
| Log | Mario's live log lines while the game runs |


**Mario only appears when Rec Room is started from this menu.** Each Play hands the game a one-time pass; Rec Room started any
other way (its own exe, a shortcut, copied flags) runs as plain Rec Room with the mod asleep.

The rest also works from the command line: `Start-Mario find` (lists what setup can use on this PC), `Start-Mario setup --auto`,
`Start-Mario check`, `Start-Mario stop`, `Start-Mario flags`.
To start in another room, put its scene name in `mario.ini` (`[start]` `hangout = Park`), or pick it on the Map tab.

## What works, and what is not tried yet

This is a work in progress, made by one person. Honestly:

| Tested in the game | Built and unit-tested, not yet tried in the game |
|---|---|
| Setup, Play and uninstall from the launcher, on a fresh install | Other rooms: they all start the same way as the Park, but each has its own shapes and quirks; only a few have been played and some may need fixes |
| Building the native library from a fresh libsm64 download | Carrying and placing objects (pallets) |
| Mario in the Rec Center: controls, camera, sound | Most quest routes (Jumbotron, Crimson Cauldron, Crescendo) |
| Starting in the Park, with the Wing cap switched on | Completing a whole quest with an S rank |
| Quests: start, fight, open doors yourself, Mario in the next room | Long flights with constant flying, and reaching the world edge |
| Fighting goblins, taking damage | How Casual mode feels in a real fight |
| Firing a cannon with the lighter (Lost Skulls) | How the power meter and the orange world-edge tape look on screen |
| | Game controllers (Xbox, PlayStation, N64 adapters): mapping tables only, no real pad tried |
| | SM64 lava: the burning floor, the burn hop and the fire puffs |

Known limits:

- **One tested client.** The mod is tested on the September 9, 2019 build. Other IL2CPP builds install as *untested* and may
  not work; builds with anti-cheat and your live Steam install are always refused (docs/INSTALL.md).
- **The world is about 150 m from where Mario starts**, in every direction. That is SM64's own limit (16-bit coordinates);
  the mod puts a wall there. Very large rooms may be cut off by it.
- **Offline and solo.** No online play, no other players, no Rec Room accounts, no scores sent anywhere. Quest scores from
  a mid-quest start or with Immortal on aren't a full run.
- **Rooms that need other rooms.** A few scenes are only part of a bigger room and cannot start by themselves; the launcher
  lists every scene it finds, and the log says when one can't be used.
- **Windows only**, in the game's normal screen mode with a keyboard and mouse or a game controller; no VR headset.
- **If the game stops or hangs while loading**, the loading bar says what went wrong in plain words, and the full detail is
  in `BepInEx\LogOutput.log` in the client folder (lines starting with `mario-`) and `logs\<date>\player.log`.

## What this package does not contain

No Rec Room files, no Nintendo ROM data, and no decompiled Rec Room code. You supply your own copies of the client and the ROM;
the setup only reads them. BepInEx is included unmodified (`BepInEx-pack\`, with its licences). The release zip includes the native Mario library already compiled from the
open-source [libsm64] sources (see `NOTICE.txt` and `docs/VERSIONS.md`); it contains no copy of the ROM and reads your ROM at
runtime. To compile it yourself instead you need zig (`docs/INSTALL.md`).

The mod is MIT-licensed (`LICENSE.txt`); Rec Room, Super Mario 64, libsm64 and BepInEx keep their own licences.

This is a fan project. It is not affiliated with or endorsed by Rec Room Inc. or Nintendo. Check the terms of the
games you use it with before sharing recordings or builds.


[libsm64]: https://github.com/libsm64/libsm64
