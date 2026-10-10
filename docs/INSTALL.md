# Installing Mario for Rec Room

Windows 10/11, 64-bit. About 15 minutes the first time. The launcher checks everything for you (`Start-Mario check`), so you
will know exactly what is missing.

**What you need**

| | From a release zip | Building from source |
|---|---|---|
| The **.NET 10 SDK** — [download](https://dotnet.microsoft.com/download/dotnet/10.0) | no — the launcher carries its own .NET | yes |
| The **September 9, 2019 Rec Room client** (below) | yes | yes |
| Your **Super Mario 64 ROM** (USA, .z64) | yes | yes |
| **BepInEx 6**, the mod loader (below) | yes | yes |
| **zig**, to compile the native Mario library once | no — the zip includes it, already built | yes |
| An internet connection for the **first start** (BepInEx downloads Unity's base files once) | yes | yes |

Unzip the release into a folder you can write to — your Desktop or Documents, not Program Files, and not inside the Rec Room
client folder. Everything below (settings, logs) is kept in that folder. `VERSION.txt` in it says which build you have.

## 1. The September 9, 2019 Rec Room client

The mod is built and tested on one exact build of Rec Room (it checks the files):

| | |
|---|---|
| Steam app | 471710 (Rec Room is free) |
| Depot | 471711 |
| Manifest | 3817258843939969587 (built 2019-09-09 22:55 UTC) |

Download that manifest with a Steam depot tool such as DepotDownloader, signed in with your own Steam account, into its
own folder — for example `C:\Games\RecRoom-2019`. Don't point the mod at your normal, current Rec Room install.

The mod runs this client **offline**: it never connects to Rec Room's servers.

**Other builds.** Setup also accepts another IL2CPP Rec Room build in its own folder, marked *untested*: BepInEx loads into it
the same way, and each part of the mod checks for the game code it hooks and stops cleanly (the game runs unmodded) when that
build lacks it. The game log says which part didn't fit. It never accepts:

- a build with **anti-cheat** (EasyAntiCheat, BattlEye): the mod never works around anti-cheat;
- your normal Steam install (`steamapps\common`): the mod is never installed into the live game;
- an older **Mono** build (no `GameAssembly.dll`): BepInEx's IL2CPP loader can't load it.

## 2. Your Super Mario 64 ROM

A dump of your own Super Mario 64 cartridge, **USA** version, in `.z64` (big-endian) format. Its SHA-256 must be
`17ce077343c6133f8c9f2d6d6d9a4ab62c8cd2aa57c40aea1f490b4c8bb21d91`. If yours is `.n64` or `.v64`, setup makes a
`.z64` copy next to it (yours stays as it is). The ROM is only read on your machine; it's never copied into the mod or the game folder.

## 3. BepInEx 6 (IL2CPP, x64)

The mod loader. **A release zip includes it** (`BepInEx-pack\BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.788.zip`, unmodified, with its licences), and setup
uses it by default, so there is nothing to download. Building from the repository instead? Use the bleeding-edge
`BepInEx-Unity.IL2CPP-win-x64` build listed in `docs/VERSIONS.md` — other builds may not load this 2019 client — and point
`[paths] bepinex` in `mario.ini` (or the wizard) at the downloaded `.zip`; there is no need to unpack it.

**Already have BepInEx 6 in the client?** Setup uses it as it is and only adds the mod; uninstall leaves it there. An old
BepInEx 5 or a half-removed loader in the way is moved into a `BepInEx-before-mario-<date>` folder (nothing is deleted), and
BepInEx 6 goes in. If `doorstop_config.ini` has Doorstop switched off, setup switches it on (uninstall switches it back).

## 4. zig (only when you build the native library yourself)

A release zip includes the native Mario library (`dist\native\sm64-mario.dll`), so you can skip this: in the wizard press
**N** (next) at the zig step. Otherwise zig is used once, during setup, to compile the library from the libsm64 sources. Install
the version listed in `docs/VERSIONS.md` and either put it on your PATH or set `[paths] zig` in `mario.ini`. Get the libsm64
sources as described in `docs/VERSIONS.md` (one `git clone` + `git checkout`).

## 5. .NET 10

A release zip needs nothing: the launcher has .NET built in. To build from source (`dotnet build -c Release`) you need the **.NET 10 SDK**.

## Setting up

Double-click `Start-Mario.cmd`. (Windows may say it protected your PC because the launcher is not code-signed: choose *More
info*, then *Run anyway*.) The first time, the **setup wizard** opens. It first looks on this PC (a few seconds, read-only: your
Steam libraries, Downloads, Desktop, Documents, the folder the launcher is in and its parent, and the games folders of your
drives) for Rec Room client folders, Super Mario 64 ROMs and BepInEx packs, and lists each one with a plain label, for example
"Sept 9, 2019 build ✓", "different version" or "byte-swapped .v64, needs conversion". Nothing is downloaded and none of your files
are copied. If it found everything exactly right, press **A** on the first screen ("use everything found") to fill in all three
and jump to the install. Otherwise it walks you through the steps (Enter = pick the highlighted line, ↑↓ or 1-9 = choose,
T = type a path, S = search again, N = next, B = back, Esc = leave the wizard); with exactly one fitting candidate it is
already highlighted, so Enter just continues:

1. **Rec Room client:** pick the folder. It checks that it's the exact 2019 build.
2. **ROM:** pick the file. It checks that it's Super Mario 64 (USA), .z64. A byte-swapped .v64 or little-endian .n64 is listed
   but must be converted to .z64 first (a ROM converter such as Tool64).
3. **BepInEx:** the pack in `BepInEx-pack\` (or another .zip / unpacked folder of the same build).
4. **zig:** found automatically if it's on your PATH; not needed with a release zip.
5. **Install:** copies BepInEx and the mod into the client folder (and builds the native library first if it is missing).
   Every file it adds is recorded, and nothing of yours is overwritten.
   Setting up again after a new download updates the mod in place. If an older download had put the mod in a differently named
   folder under `BepInEx\plugins`, the files setup recorded there are removed (any file of yours in that folder stays).

Then press **P** (or select **▶ PLAY** and press Enter). You can rerun the wizard any time from the **Setup** tab.

**The first start takes a few minutes** and needs the internet: BepInEx downloads Unity's base files and generates its
interface files for this 2019 client, once. A *Hello Mario* loading bar follows the game while it starts and fills up as the game
loads; the first-start steps are named on it. If the bar stops with a red message, the message says what went wrong (see
Troubleshooting). When it reads 100 % Mario is in the room.

## Where to start

The **Map** tab picks where **Play** starts:

- **Rec Center** — free play in the hub.
- **Other rooms of your client** — the Park, the Bowling Alley, ... Everything the launcher finds in your own client build is listed
  under "Other rooms". Pick one and Play starts there; it is stored as `[start] hangout = <scene name>` in `mario.ini`
  (for example `hangout = Park`), and clearing it (or picking the Rec Center) goes back to the Rec Center. Mario starts in the
  room the game loads for that scene. A few scenes are only part of a bigger room and cannot start by themselves: the log
  (and the loading bar) then say that no room loads that scene.
- **A quest, or any room of one** — Mario starts the quest (from its first room, or the room you pick) and plays it by the original
  rules. Starting in a later room is not a full run, so scores from it don't count as one.

Only Play (the Rec Center or another room) and quests are started from the Map tab; routes have their own tab.

## Flying and the edge of the world

The **Wing cap** (Mario tab, `wing_cap` in `mario.ini`) gives Mario SM64's flight cap: *Auto* wears it while the original game
lets you fly (the room allows it, or you hold the Maker Pen), *Always* and *Never* force it. Its wings need a native library built
from this version: a release zip has one; if you built one earlier yourself, delete `dist/native/sm64-mario.dll` and run Setup
again (otherwise the log says `mario-wing-cap-unavailable` and Mario goes without wings; the Metal cap that Immortal mode adds
works with either).

**Constant flying** (Mario tab, `constant_flying = on`; off by default) keeps a Wing-cap flight at one steady speed, so there is no
diving to gain speed and no stalling in a climb.

SM64's world is small. Mario can go about **150 m** from the spot where he starts, in every direction and upwards; it is a limit of
SM64 itself (its coordinates are 16-bit). The mod puts a solid wall there. When you are within about 12 m of it, orange
construction tape fades in on the wall, getting stronger the closer you are (the log says `mario-world-edge shown` the first
time). If the tape ever misbehaves, only the tape is switched off; the wall stays.

Fights too hard? Turn on **Casual mode** on the **Mario** tab: more reach, a wider punch angle and softer knockback. It is off by default and is not the real SM64 rules.

The **Health meter** (Mario tab) shows SM64's power meter at the top of the screen while Mario is hurt. It is drawn
from your own ROM when the game starts, so no Nintendo art ships with the mod.

## Controls (keyboard)

| Key | Mario (SM64 button) |
|---|---|
| W A S D | Move (analog stick) |
| Space | Jump (A) |
| Left mouse button | Punch, grab, throw (B) |
| Shift | Crouch, ground pound, long-jump/backflip with Space (Z) |
| Mouse or arrow keys | Turn the camera |
| R | Re-centre the camera behind Mario |
| 1 | Open / close the Mario menu (2 and 3 move through it) |
| Esc | Pause Mario's controls (press again to resume) |

Controls only respond while the game window is focused.

## Controls (game controller)

Plug in a controller at any time (`controller = auto` in `mario.ini`, the **Game controller** row on the Mario tab). Mario plays with SM64's own
N64 layout: every controller is mapped onto the N64 pad, and the keyboard keeps working (whichever you touch drives Mario;
the controller wins if both are in use, and both can turn the camera).

| N64 button | Mario | Xbox (XInput) | PlayStation (DualShock 4, DualSense) | N64 USB adapters | Other game controllers |
|---|---|---|---|---|---|
| Control stick | Move; how far you push is walk or run | Left stick | Left stick | Stick | Left stick |
| A | Jump | A | Cross | A (button 1) | Button 2 |
| B | Punch, kick, dive, grab, throw | X or B | Square or Circle | B (button 2) | Button 1 or 3 |
| Z | Crouch, ground pound, long jump and backflip with A | LT or RT | L2 or R2 | Z (button 3) | Button 7 or 8 |
| R | Re-centre the camera behind Mario | RB | R1 | R (button 6) | Button 6 |
| L | Open / close the Mario menu | LB | L1 | L (button 5) | Button 5 |
| Start | Pause Mario's controls (press again to resume) | Start | Options | Start (button 4) | Button 10 |
| C-left, C-right | Turn the camera (they page through the open menu) | Right stick left / right | Right stick left / right | C-left (button 9), C-right (button 10) | Right stick left / right |
| C-up, C-down | Tilt the camera | Right stick up / down | Right stick up / down | C-up (button 7), C-down (button 8) | Right stick up / down |

SM64's R button switches between its Lakitu and Mario cameras, and C-up / C-down look around in first person and zoom. This
mod's camera has neither, so R re-centres the camera and C-up / C-down tilt it. The D-pad and the other buttons do nothing.

The stick has a round dead zone (`controller_deadzone`, 0.2 by default; Xbox pads never go below Microsoft's recommended 0.24 left
and 0.27 right). Triggers count as Z past 30%, and the right stick counts as a C button past half way. Xbox-compatible pads use
Windows' XInput; every other game controller (PlayStation, N64 adapters, generic) uses the Windows joystick API (winmm), so
Steam Input or DS4Windows (which present an Xbox pad) work too. A pad is picked up when the game is running, within two seconds of
plugging it in. The log says `mario-controller found=xinput|winmm family=xbox|playstation|n64|generic vid=.. pid=.. name=..` and
`mario-controller lost=..`. The button numbers for PlayStation, N64 and generic pads are the usual Windows DirectInput order and
have not been tried on every make: if a button is wrong, send the `found` line and what each button did.

To go through a quest door, point the camera at the door, walk up close (about 2 m) and press the left mouse button.

## What the mod changes

- **The client's own files:** nothing. Setup only adds BepInEx and the mod next to them (recorded in `.mario-install.json`), and
  the game files stay byte-for-byte the 2019 build.
- **Settings your normal Rec Room shares:** the 2019 game saves Unity settings (window size and a few flags) in
  `HKEY_CURRENT_USER\Software\Against Gravity\Rec Room` and some cache files in `%USERPROFILE%\AppData\LocalLow\Against Gravity\Rec Room`.
  The launcher saves both right before it starts the game and puts them back exactly when the game closes. If another copy of
  Rec Room ran at the same time, it leaves them alone, so that copy's settings aren't lost. Each session's
  `logs\<date>\restore.txt` (under `shared-state`) says what was put back.
- **Stop** only closes the Rec Room it started, never another copy.

## Uninstalling

**Setup → Uninstall** (or `Start-Mario uninstall`) removes everything setup added to the client folder. Files you changed afterwards are kept and
listed.

## Starting and stopping from the command line

`Start-Mario find` prints what the wizard would offer (the client folders, ROMs and BepInEx packs it can see, each with a label)
and `Start-Mario setup --auto` then uses the exactly-right ones and installs: it keeps a path you already set that works, and
refuses, changing nothing, if something is missing or if several different client folders fit (set `[paths] client` in
`mario.ini` to the one you want).

`Start-Mario stop` (closes the game the normal way, like its window's X), `Start-Mario check`, `Start-Mario flags` (prints what a
start would pass to the game, without starting anything). Rec Room with Mario starts **from the menu only** (Play, a quest or a
route): each start gets a one-time pass, and Rec Room started any other way runs without Mario.
Rec Room can run only once: if it is already running, Play says so and does nothing — close it first
(**S** in the launcher, or `Start-Mario stop`).

## Troubleshooting

The loading bar shows the first problem the mod logs. The usual ones:

- **The wizard didn't find my files** — it only looks in the places named above, a few folders deep, and stops after about
  five seconds. Press **T** to type the path, or move the files into Downloads. `MARIO_NO_AUTODETECT=1` turns the automatic
  search off (the **S** key still searches).
- **"This Rec Room build has no room Mario can start in called '...'"** — the `hangout` setting names a scene your client does not
  load as a room. Pick a room on the Map tab, or clear `hangout` in `mario.ini` to start in the Rec Center.
- **"Rec Room took too long to load (stuck at '...')"** — the game did not finish loading the room in time (a slow disk, a very
  first start, or a room that doesn't work). Close it and start again; if it repeats, send `BepInEx\LogOutput.log`.
- **"Rec Room changed the room, player or camera under Mario, so Mario stopped"** — the original game moved things Mario was
  attached to. Close it and start again.
- **"BepInEx could not load the Mario mod"** — run Setup again (Setup tab).
- **"Rec Room is already running"** — another copy of the 2019 client is open. Close it, then press Play.
- **"The Rec Room client isn't set up" / "Mario isn't installed in the Rec Room client folder yet"** — run Setup (the wizard), or
  fix the paths on the Setup tab.
- **"This Rec Room build has anti-cheat"** — use the September 9, 2019 build, or another older build without anti-cheat.
- **"Untested build"** — it installs and starts; if Mario doesn't appear, `BepInEx\LogOutput.log` says which part didn't fit
  that build. The September 9, 2019 build above is the one that is known to work.
- **"BepInEx's interop cache was incomplete"** — fixed for you: BepInEx rebuilds it on that start (a few minutes).
- **A `BepInEx-before-mario-<date>` folder appeared** — setup moved files that were in the way there (an old loader, a
  hand-copied mod). Nothing was deleted; remove the folder once everything works.
- **"Not Super Mario 64 (USA) in .z64 format"** (or "not found") — check the path, the region and the byte order.
- **The bar sits still on "Starting Rec Room" or says BepInEx has not started** — BepInEx is not installed in the client folder
  (run Setup again), or antivirus blocked `winhttp.dll`.
- **Nothing for a long time on a first start** — normal for the first few minutes (see above). With no internet connection the
  first start cannot finish: connect and start again.
- **Rec Room closes during the first start** — look at `logs\<date>\player.log`; BepInEx's own log is in the client
  folder under `BepInEx\LogOutput.log`.
- Everything the mod does is written to `BepInEx\LogOutput.log` with a `mario-` prefix (the launcher's Log tab shows the recent lines).
- **Windows says it protected your PC** when you open `Start-Mario.cmd` — the launcher is not code-signed. *More info*, then
  *Run anyway*, if you trust where you got the zip.
