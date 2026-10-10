<div align="center">

# Mario for Rec Room

**Super Mario 64's Mario in old IL2CPP builds of Rec Room (December 14, 2018 or later). Offline, single player, real SM64 physics.**

[![Latest release](https://img.shields.io/github/v/release/Shippy089/SM64-Mario_RecRoom?label=download&color=e52521)](https://github.com/Shippy089/SM64-Mario_RecRoom/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-049cd8)](LICENSE.txt)
![Windows 10/11 x64](https://img.shields.io/badge/Windows-10%20%2F%2011%20x64-fbd000)
![Rec Room old IL2CPP builds](https://img.shields.io/badge/Rec%20Room-old%20IL2CPP%20builds-43b047)
![Offline only](https://img.shields.io/badge/online-never-555555)

**[Download the latest release](https://github.com/Shippy089/SM64-Mario_RecRoom/releases/latest)** · [Install guide](docs/INSTALL.md) · [Routes](docs/ROUTES.md)

by Shippy089

</div>

> [!IMPORTANT]
> You need your own **Super Mario 64 (USA) ROM** and your own copy of an **old IL2CPP Rec Room client (December 14, 2018 or later)**. Neither is
> included, neither is downloaded for you, and the mod never talks to Rec Room's servers.

> [!NOTE]
> This repo holds the docs, routes and native build scripts. The playable package (launcher, mod, native library and the
> BepInEx loader in one zip) is on the [Releases](https://github.com/Shippy089/SM64-Mario_RecRoom/releases) page.

## What it is

The real Super Mario 64 Mario, running on [libsm64], dropped into an old Rec Room build: the Rec Center, the Park, the other
rooms, and the quests that build has. He moves the way he did on the N64. Triple jumps, backflips, wall kicks, long jumps, dives,
punches, ground pounds, the 8-wedge health meter and his voice are all there.

Rec Room itself isn't changed. Same rooms, same enemies, same doors, same quest rules and scoring. Mario gets no special
treatment and has to beat the quests as they were built.

It's offline and single player. No servers, no other players, no accounts.

## Features

- **Any room.** The Rec Center or any other room in your client build (the Park, the Bowling Alley, the paintball maps and so
  on), picked on the **Map** tab. If a scene is only part of a bigger room, the log says so and it isn't loaded.
- **The quests.** Golden Trophy, Jumbotron, Crimson Cauldron, Lost Skulls and Crescendo of the Blood Moon (whichever your build
  has), from the start or from any room. Mario goes through the doors himself.
- **Combat.** His punches, kicks and stomps hurt Rec Room enemies, and their attacks hurt him. Quests only; the Rec Center
  and the other rooms have no combat to hook into.
- **SM64 lava.** Mario burns, hops, loses health and smokes instead of the quest ending on contact. On by default
  (`sm64_lava`).
- **Carrying.** Buttons, pots, traps, bombs, torches, lighters, cannon handles, jigsaw pieces and floating pallets, picked up,
  carried and thrown with Mario's own grab.
- **Wing cap.** A triple jump becomes flight. He wears it whenever the original game lets you fly (the room allows it, or
  you hold the Maker Pen), or always, or never (`wing_cap`).
- **Constant flying** (off by default): one steady flight speed instead of SM64's dive-to-speed-up and stall-on-climb.
- **World edge.** SM64's world is small: about **150 m** from where Mario starts, in every direction and up. There's a solid
  wall there, and orange construction tape fades in on it when you get within about 12 m.
- **Controllers.** Xbox, PlayStation, N64 USB adapters and other gamepads use SM64's N64 layout
  ([button tables](docs/INSTALL.md)). Keyboard and mouse keep working.
- A follow camera you steer, SM64 sound, and SM64's power meter on screen, drawn from your ROM.
- **Casual mode** (off by default): more reach and softer knockback, if SM64 fights are too hard.
- **Routes**: JSON files that make Mario play by himself using controller input only, no teleporting
  ([docs/ROUTES.md](docs/ROUTES.md)).

## Getting started

**You need** Windows 10 or 11 (64-bit), an **old IL2CPP Rec Room client (December 14, 2018 or later)** and a **Super Mario 64 (USA) ROM**. **BepInEx
6** (the mod loader) comes in the zip, and the launcher has .NET built in, so there's nothing else to install.
[docs/INSTALL.md](docs/INSTALL.md) covers where each part comes from (including how to download an old build with SteamDB and
DepotDownloader) and what the launcher checks. Allow about 15 minutes the
first time.

1. **Unzip** the release into a folder you can write to, like Desktop or Documents. Not Program Files, and not by running it
   from inside the zip window.
2. **Double-click `Start-Mario.cmd`.** Windows may say it "protected your PC" because the launcher isn't code-signed; choose
   *More info*, then *Run anyway*.
3. The first time, a **setup wizard** looks for the Rec Room client, your ROM and the BepInEx pack (Steam libraries, Downloads,
   Desktop, Documents, next to the launcher) and lists what it found. Pick with Enter, or press **A** to take everything it
   found and install. It only reads those files: it never downloads, copies or overwrites them. If it finds nothing, type the
   path.
4. Press **P** (or **▶ PLAY**, then Enter). A *Hello Mario* loading bar follows the game while it starts; Mario is there when
   it fills. **The first start takes a few minutes and needs the internet once**, while BepInEx downloads Unity's base files
   and prepares itself for your client. Later starts take under a minute.
5. Play. W A S D moves, Space jumps, left click punches and grabs, Shift crouches, the mouse turns the camera
   ([all controls](docs/INSTALL.md#controls-keyboard)). Esc pauses Mario's controls.

The launcher has tabs for the rest (Tab or 1–7 to switch, arrow keys and Enter to change things):

| Tab | What it does |
|---|---|
| Play | The Play button, what to start, Immortal Mario (testing only), live status (health, room, position) |
| Map | The Rec Center, any other room of your client, or any room of the five quests, checked against your own build |
| Mario | Fighting, Casual mode, SM64 health meter, SM64 lava, carrying, Wing cap, constant flying, controller, camera, sound |
| Routes | Pick a route file for Mario to play by himself |
| Setup | Your file paths, a status check, set up / update, uninstall |
| Advanced | Start the quest immediately, where logs go, the flags Play would pass to the game |
| Log | Mario's live log while the game runs |

> [!TIP]
> Mario only appears when Rec Room is started from this menu. Each Play gives the game a one-time pass; Rec Room started any
> other way (its own exe, a shortcut, copied flags) runs as plain Rec Room with the mod inactive.

Some commands also work from a command line: `Start-Mario find` (what setup could use on this PC), `Start-Mario setup --auto`,
`Start-Mario check`, `Start-Mario stop`, `Start-Mario flags`.

## What's been tested

This is a work in progress by one person. Where things stand:

| Seen working in the game | Built and unit-tested, not proven in the game yet |
|---|---|
| Setup, Play and uninstall from the launcher, on a fresh install | Some rooms: 22 of the 28 tried start; the 6 StuntRunner courses are only parts of another room |
| Building the native library from a fresh libsm64 download | Carrying and placing objects (pallets) |
| Mario in the Rec Center: controls, camera, sound | Most quest routes (Jumbotron, Crimson Cauldron, Crescendo); a Golden Trophy route fight still times out |
| Starting in the Park with the Wing cap on | Finishing a whole quest with an S rank |
| Quests: start, fight, open doors, Mario in the next room | Game controllers: mapping tables only, no real pad tried |
| Fighting goblins and taking damage | Builds other than the tested one (they install as *compatible build*) |
| Firing a cannon with the lighter (Lost Skulls) | |
| SM64 lava: burn hop, fire puffs, health loss, death ends the quest cleanly | |
| Constant flying, the Wing cap's wings, the orange world-edge tape | |
| Casual mode loading and punches landing | |

## Known limits

- **Any old build, one tested.** Any IL2CPP Rec Room build without anti-cheat installs. Builds before December 14, 2018 are Mono and can't load the mod.
  Only the September 9, 2019 build has been tested; parts of the mod may not fit others. Builds with anti-cheat, and your live
  Steam install, are always refused; the mod never works around anti-cheat.
- **150 m world.** SM64 uses 16-bit coordinates, so the world ends about 150 m from where Mario starts. Very large rooms get
  cut off by the wall.
- **Offline and solo.** No online play, no other players, no accounts, no scores sent anywhere. A mid-quest start or a run
  with Immortal on isn't a full run.
- **Some scenes need their parent room.** A few scenes are only part of a bigger room and can't start alone. The launcher
  lists every scene it finds, and the log says when one can't be used.
- **Windows only**, flat screen with keyboard and mouse or a controller. No VR.
- **If loading stops or hangs**, the loading bar says what went wrong in plain words. The full detail is in
  `BepInEx\LogOutput.log` in the client folder (lines starting with `mario-`) and in `logs\<date>\player.log`.

## What isn't included

No Rec Room files, no Nintendo ROM data, no decompiled Rec Room code. You supply the client and the ROM, and setup only reads
them. BepInEx ships unmodified with its licences (`BepInEx-pack\` in the release zip). The native Mario library in the zip is
compiled from the open-source [libsm64] sources (see `NOTICE.txt` and `docs/VERSIONS.md`); it contains no ROM data and reads
your ROM at runtime. To compile it yourself you need zig (`docs/INSTALL.md`).

The mod is MIT-licensed ([LICENSE.txt](LICENSE.txt)). Rec Room, Super Mario 64, libsm64 and BepInEx keep their own licences.

This is a fan project, not affiliated with or endorsed by Rec Room Inc. or Nintendo. Check the terms of the games you use it
with before sharing recordings or builds.

[libsm64]: https://github.com/libsm64/libsm64
