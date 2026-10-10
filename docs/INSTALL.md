# Installing Mario for Rec Room

This is for Windows 10/11, 64-bit. Plan on about 15 minutes the first time. The launcher reports anything that is missing
(`Start-Mario check`).

Tested on the September 9, 2019 build. Other builds in the supported range can install, but not all of them are tested.

**What you need**

| | From a release zip | Building from source |
|---|---|---|
| The **.NET 10 SDK** ([download](https://dotnet.microsoft.com/download/dotnet/10.0)) | no, the launcher carries its own .NET | yes |
| An **old IL2CPP Rec Room client, 2019 to April 8, 2020** (below) | yes | yes |
| Your **Super Mario 64 ROM** (USA, .z64) | yes | yes |
| **BepInEx 6**, the mod loader (below) | yes | yes |
| **zig**, a compiler, to build the native Mario library once | no, the zip already has it built | yes |
| An internet connection for the **first start** (BepInEx downloads Unity's base files once) | yes | yes |

Unzip the release into a folder you can write to, like your Desktop or Documents. Don't use Program Files or the Rec Room
client folder. Your settings and logs are kept in that same folder, and `VERSION.txt` in it tells you which build you have.

## 1. An old IL2CPP Rec Room client

The mod works with old IL2CPP builds of Rec Room. IL2CPP is a way of building Unity games, and it's the kind BepInEx 6 can
load. The usable builds run from 2019 to April 8, 2020, before Rec Room added anti-cheat (software that blocks changes to a
game). Setup looks at the folder you give it and accepts the build when all of these are true:

- It is an IL2CPP build. That means it has `GameAssembly.dll` and `global-metadata.dat`, and the metadata is version 24 or newer.
  BepInEx 6 reads that (Unity 2017 onward).
- It has **no anti-cheat** (EasyAntiCheat, BattlEye, or Rec Room's own Referee). The mod never works around anti-cheat.
- It isn't your normal Steam install (`steamapps\common`). The mod is never installed into the live game.

Mono builds don't work. BepInEx's IL2CPP loader can't load them, so setup refuses them. A Mono build has no
`GameAssembly.dll` and has a `Managed` folder instead. **Rec Room switched from Mono to IL2CPP on December 14, 2018** (manifest
`1421943146240504109`). That update adds `GameAssembly.dll` and removes the Mono runtime, so every build before it is Mono and
won't work. The first IL2CPP builds were made with **Unity 2018.1**, and BepInEx 6 can't load those either. On the December 14
build, its code generator fails before any mod loads. The September 9, 2019 build uses Unity 2018.3 and works. The exact update
where Rec Room moved to Unity 2018.3 isn't pinned down yet, so setup reads each build's Unity version and refuses 2018.1 and
older.

**Rec Room started launching through Easy Anti-Cheat with the April 20, 2020 update** (manifest `9119006898280485087`, per Rec
Room's own patch notes; Rec Room's Referee replaced it in 2025). So April 8, 2020 is the last usable build (manifest
`3706709507199582170`). Step 1b below shows how to check a build before you spend time downloading it.

**The tested build** is September 9, 2019. The mod was developed and tested on it, and setup labels it *tested*:

| | |
|---|---|
| Steam app | 471710 (Rec Room is free) |
| Depot | 471711 |
| Manifest | 3817258843939969587 (built 2019-09-09 22:55 UTC) |

Steam keeps every old build of a game as a *manifest*. That's a snapshot of one depot (one set of game files) on one date. Rec
Room's Windows files are depot **471711** of app **471710**. You look up a manifest in that depot's history on SteamDB, then
download it with DepotDownloader, signed in with your own Steam account, into a folder of its own. Don't point the mod at your
normal, current Rec Room install.

### Step 1: find a manifest on SteamDB

1. Open <https://steamdb.info/depot/471711/manifests/>. You can also open <https://steamdb.info/app/471710/depots/>, click depot
   471711, and then click the *Manifests* tab.
2. Each row is one build. It shows the date the build went out and its **manifest ID**, which is a long number such as
   `3817258843939969587`. SteamDB may ask you to sign in with Steam before it shows the full history.
3. Pick a date from 2019 up to April 8, 2020, and copy its manifest ID. The one above is the tested build. Any other date is a
   *compatible build* if it passes setup's check.

Rooms and quests depend on the date. An earlier build won't have quests that came out later, and the Map tab only lists what
your build contains.

### Step 1b: check that a build is IL2CPP before you download it

DepotDownloader (step 2) can fetch just a build's file list, a few MB, with `-manifest-only`:

```
DepotDownloader -app 471710 -depot 471711 -manifest MANIFEST_ID -username YOUR_STEAM_NAME -remember-password -manifest-only -dir C:\Games\check
```

It writes a text file in that folder listing every file in the build. Open it and search for `GameAssembly.dll`. If it's
there, the build is IL2CPP and worth downloading. If it isn't there but `Recroom_Release_Data\Managed\Assembly-CSharp.dll` is,
the build is Mono and won't work. Also search for `EasyAntiCheat`, `BattlEye` and `Referee`. If any of those show up, the build has anti-cheat
and won't work either.

### Step 2: get DepotDownloader

DepotDownloader is an open-source command-line tool from SteamRE (<https://github.com/SteamRE/DepotDownloader>). Install it with
winget:

```
winget install --exact --id SteamRE.DepotDownloader
```

Or download the Windows build from its GitHub *Releases* page and unzip it.

### Step 3: download the build

Rec Room is free, but Steam only hands its files to an account that has it in its library. So click *Play* on its Steam store
page once (or install it the normal way) before you download. Then open a terminal and run this with your own Steam user name:

```
DepotDownloader -app 471710 -depot 471711 -manifest 3817258843939969587 -username YOUR_STEAM_NAME -remember-password -dir C:\Games\RecRoom-tested
```

That gets the tested build. For another date, change `-manifest` and the folder name:

```
DepotDownloader -app 471710 -depot 471711 -manifest MANIFEST_ID_FROM_STEAMDB -username YOUR_STEAM_NAME -remember-password -dir C:\Games\RecRoom-2019-02
```

- DepotDownloader asks for your password in the terminal, and for a Steam Guard code if your account uses one. Type them there
  yourself. They go only to Steam. `-remember-password` saves a login key, so the next download doesn't ask again.
- Expect about 4 GB. If the download stops, run the same command again with `-validate` added. It checks what's already there
  and fetches only what's missing or broken.
- When it finishes, the folder holds `Recroom_Release.exe`. Give that folder to the launcher. The setup wizard can also find
  folders it can see (see Setting up below).

**Without DepotDownloader,** the Steam client can do the same thing from its hidden console. Open `steam://open/console` in a
browser or in the Run box (Win+R), then type

```
download_depot 471710 471711 3817258843939969587
```

When it's done, Steam prints where it saved the files (usually `...\Steam\steamapps\content\app_471710\depot_471711`). The launcher
finds them there. If you want to keep them, copy them to a folder of their own, because Steam reuses that folder for the next
`download_depot`.

The mod runs the client **offline**. It never connects to Rec Room's servers.

**Other builds** show up as *compatible build* with their Unity version. BepInEx loads into them the same way. Each part of the
mod looks for the game code it hooks into, and stops cleanly (the game runs unmodded) when a build doesn't have it. The game log
says which part didn't fit. Rooms and quests are read from your own build, so the Map tab only lists what it has.

## 2. Your Super Mario 64 ROM

A ROM is a file copy of a game cartridge's data. You need a dump of your own Super Mario 64 cartridge, **USA** version, in
`.z64` (big-endian) format. Its SHA-256 (a fingerprint of the file) must be
`17ce077343c6133f8c9f2d6d6d9a4ab62c8cd2aa57c40aea1f490b4c8bb21d91`. If yours is `.n64` or `.v64`, setup makes a `.z64` copy next
to it, and yours stays as it is. The ROM is only read on your machine. It's never copied into the mod or the game folder.

## 3. BepInEx 6 (IL2CPP, x64)

BepInEx is the mod loader. **A release zip includes it** (`BepInEx-pack\BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.788.zip`,
unmodified, with its licences), and setup uses it by default, so there's nothing to download. Building from the repository
instead? Use the bleeding-edge `BepInEx-Unity.IL2CPP-win-x64` build listed in `docs/VERSIONS.md`. Other BepInEx builds may not
load old Rec Room builds. Point `[paths] bepinex` in `mario.ini` (or the wizard) at the downloaded `.zip`. You don't need to
unpack it.

**Already have BepInEx 6 in the client?** Setup uses it as it is and only adds the mod. Uninstall leaves BepInEx there. If an
old BepInEx 5 or a half-removed loader is in the way, setup moves it into a `BepInEx-before-mario-<date>` folder (nothing is
deleted) and puts BepInEx 6 in. If `doorstop_config.ini` has Doorstop switched off, setup switches it on, and uninstall switches
it back.

## 4. zig (only when you build the native library yourself)

A release zip includes the native Mario library (`dist\native\sm64-mario.dll`), so you can skip this. In the wizard, press
**N** (next) at the zig step. Otherwise, setup uses zig once to compile the library from the libsm64 sources. Install the
version listed in `docs/VERSIONS.md`, and either put it on your PATH or set `[paths] zig` in `mario.ini`. Get the libsm64 sources
as described in `docs/VERSIONS.md` (one `git clone` and one `git checkout`).

## 5. .NET 10

A release zip needs nothing here, because the launcher has .NET built in. To build from source (`dotnet build -c Release`), you
need the **.NET 10 SDK**.

## Setting up

Double-click `Start-Mario.cmd`. Windows may say it protected your PC because the launcher isn't code-signed. Choose *More info*,
then *Run anyway*. The first time, the **setup wizard** opens. It starts by looking around this PC. This takes a few seconds and
is read-only. It checks your Steam libraries, Downloads, Desktop, Documents, the folder the launcher is in and its parent, and
the games folders of your drives. It looks for Rec Room client folders, Super Mario 64 ROMs and BepInEx packs, and lists each one
with a plain label. Examples are "Sept 9, 2019 build (tested) ✓", "compatible build, Unity 2018.2.9f1 ✓", "has anti-cheat" and
"byte-swapped .v64, needs conversion". Nothing is downloaded and none of your files are copied.

If it found everything exactly right, press **A** on the first screen ("use everything found") to fill in all three and jump to
the install. Otherwise the wizard walks you through the steps. Keys: Enter picks the highlighted line, ↑↓ or 1-9 choose, T types
a path, S searches again, N goes to the next step, B goes back, and Esc leaves the wizard. If exactly one candidate fits, it's
already highlighted, so Enter just continues.

1. **Rec Room client:** pick the folder. The wizard checks that it's a compatible old build (see section 1 above).
2. **ROM:** pick the file. The wizard checks that it's Super Mario 64 (USA), .z64. A byte-swapped .v64 or little-endian .n64 is
   listed, but you have to convert it to .z64 first (with a ROM converter such as Tool64).
3. **BepInEx:** pick the pack in `BepInEx-pack\` (or another .zip or unpacked folder of the same build).
4. **zig:** found automatically if it's on your PATH. You don't need it with a release zip.
5. **Install:** copies BepInEx and the mod into the client folder (and builds the native library first if it's missing). Every
   file it adds is recorded, and nothing of yours is overwritten. If you set up again after a new download, it updates the mod in
   place. An older download may have put the mod in a differently named folder under `BepInEx\plugins`. In that case, setup
   removes the files it recorded there, and any file of yours in that folder stays.

Then press **P** (or select **▶ PLAY** and press Enter). You can rerun the wizard any time from the **Setup** tab.

**The first start takes a few minutes** and needs the internet. BepInEx downloads Unity's base files and generates its interface
files for your client, once. A *Hello Mario* loading bar follows the game while it starts, and it fills up as the game loads. The
bar names the first-start steps. If it stops with a red message, the message says what went wrong (see Troubleshooting). When the
bar reads 100 %, Mario is in the room.

## Where to start

The **Map** tab picks where **Play** starts:

- **Rec Center:** free play in the hub.
- **Other rooms of your client:** the Park, the Bowling Alley, and so on. The launcher lists everything it finds in your own
  client build under "Other rooms". Pick one and Play starts there. The pick is stored as `[start] hangout = <scene name>` in
  `mario.ini` (for example `hangout = Park`). Clear it, or pick the Rec Center, to go back to the Rec Center. Mario starts in the
  room the game loads for that scene. A few scenes are only part of a bigger room and can't start by themselves. The log and the
  loading bar then say that no room loads that scene.
- **A quest, or any room of one:** Mario starts the quest (from its first room, or from the room you pick) and plays it by the
  original rules. Starting in a later room isn't a full run, so scores from it don't count as one.

Only Play (the Rec Center or another room) and quests start from the Map tab. Routes have their own tab.

## Flying and the edge of the world

The **Wing cap** (Mario tab, `wing_cap` in `mario.ini`) gives Mario SM64's flight cap. *Auto* wears it whenever the original game
lets you fly (the room allows it, or you hold the Maker Pen). *Always* and *Never* force it on or off. The wings need a
native library built from this version. A release zip has one. If you built one yourself earlier, delete
`dist/native/sm64-mario.dll` and run Setup again. Otherwise the log says `mario-wing-cap-unavailable` and Mario goes without
wings. The Metal cap that Immortal mode adds works with either library.

**Constant flying** (Mario tab, `constant_flying = on`; off by default) keeps a Wing-cap flight at one steady speed. You don't
dive to gain speed, and you don't stall in a climb.

SM64's world is small. Mario can go about **150 m** from the spot where he starts, in every direction and upwards. This limit
comes from SM64 itself, because its coordinates are 16-bit. The mod puts a solid wall there. When you're within about 12 m of
it, orange construction tape fades in on the wall, and it gets stronger the closer you are (the log says
`mario-world-edge shown` the first time). If the tape ever misbehaves, only the tape is switched off. The wall stays.

If fights are too hard, turn on **Casual mode** on the **Mario** tab. You get more reach, a wider punch angle and softer knockback. It's
off by default, and it isn't the real SM64 rules.

The **Health meter** (Mario tab) shows SM64's power meter at the top of the screen while Mario is hurt. It's drawn from your own
ROM when the game starts, so no Nintendo art ships with the mod.

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

Plug in a controller at any time (`controller = auto` in `mario.ini`, or the **Game controller** row on the Mario tab). Mario
plays with SM64's own N64 layout. Every controller is mapped onto the N64 pad, and the keyboard keeps working. Whichever one you
touch drives Mario. The controller wins if both are in use, and both can turn the camera.

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

In SM64, the R button switches between the Lakitu and Mario cameras, and C-up / C-down look around in first person and zoom.
This mod's camera has neither of those, so R re-centres the camera and C-up / C-down tilt it. The D-pad and the other buttons do
nothing.

The stick has a round dead zone (`controller_deadzone`, 0.2 by default). A dead zone is how far you must push the stick before
Mario reacts. Xbox pads never go below Microsoft's recommended 0.24 on the left stick and 0.27 on the right. Triggers count as Z
past 30%, and the right stick counts as a C button past half way. Xbox-compatible pads use Windows' XInput. Every other game
controller (PlayStation, N64 adapters, generic) uses the Windows joystick API (winmm). So Steam Input and DS4Windows, which
present themselves as an Xbox pad, work too. The mod picks up a pad while the game is running, within two seconds of plugging it
in. The log says `mario-controller found=xinput|winmm family=xbox|playstation|n64|generic vid=.. pid=.. name=..` and
`mario-controller lost=..`. The button numbers for PlayStation, N64 and generic pads follow the usual Windows DirectInput order.
They haven't been tried on every make. If a button is wrong, send the `found` line and what each button did.

To go through a quest door, point the camera at the door, walk up close (about 2 m) and press the left mouse button.

## What the mod changes

- **The client's own files:** nothing. Setup only adds BepInEx and the mod next to them (recorded in `.mario-install.json`). The
  game files stay byte-for-byte as they were.
- **Settings your normal Rec Room shares:** the old game saves Unity settings (window size and a few flags) in
  `HKEY_CURRENT_USER\Software\Against Gravity\Rec Room`, and some cache files in
  `%USERPROFILE%\AppData\LocalLow\Against Gravity\Rec Room`. The launcher saves both right before it starts the game, and puts
  them back exactly when the game closes. If another copy of Rec Room ran at the same time, the launcher leaves them alone, so
  that copy's settings aren't lost. Each session's `logs\<date>\restore.txt` (under `shared-state`) says what was put back.
- **Stop** only closes the Rec Room that the launcher started. It never closes another copy.

## Uninstalling

Use **Setup → Uninstall** (or `Start-Mario uninstall`). It removes everything that setup added to the client folder. Files you
changed afterwards are kept and listed.

## Starting and stopping from the command line

`Start-Mario find` prints what the wizard would offer: the client folders, ROMs and BepInEx packs it can see, each with a label.
`Start-Mario setup --auto` then uses the ones that are exactly right and installs. It keeps a path you already set if that path
works. It refuses, and changes nothing, if something is missing or if several different client folders fit. In that case, set
`[paths] client` in `mario.ini` to the one you want.

`Start-Mario stop` closes the game the normal way, like clicking the window's X. `Start-Mario check` runs the checks.
`Start-Mario flags` prints what a start would pass to the game, without starting anything. Rec Room with Mario starts **from the
menu only** (Play, a quest or a route). Each start gets a one-time pass, and Rec Room started any other way runs without Mario.
Rec Room can only run once at a time. If it's already running, Play says so and does nothing. Close it first (**S** in the
launcher, or `Start-Mario stop`).

## Troubleshooting

The loading bar shows the first problem the mod logs. These are the usual ones:

- **The wizard didn't find my files.** It only looks in the places named above, a few folders deep, and it stops after about
  five seconds. Press **T** to type the path, or move the files into Downloads. `MARIO_NO_AUTODETECT=1` turns the automatic
  search off (the **S** key still searches).
- **"This Rec Room build has no room Mario can start in called '...'"**: the `hangout` setting names a scene that your client
  doesn't load as a room. Pick a room on the Map tab, or clear `hangout` in `mario.ini` to start in the Rec Center.
- **"Rec Room took too long to load (stuck at '...')"**: the game didn't finish loading the room in time. The cause may be a slow
  disk, a very first start, or a room that doesn't work. Close the game and start again. If it repeats, send
  `BepInEx\LogOutput.log`.
- **"Rec Room changed the room, player or camera under Mario, so Mario stopped"**: the original game moved things that Mario was
  attached to. Close the game and start again.
- **"BepInEx could not load the Mario mod"**: run Setup again (Setup tab).
- **"Rec Room is already running"**: another copy of the old client is open. Close it, then press Play.
- **"The Rec Room client isn't set up" / "Mario isn't installed in the Rec Room client folder yet"**: run Setup (the wizard), or
  fix the paths on the Setup tab.
- **"This Rec Room build has anti-cheat"**: use an older IL2CPP build from before anti-cheat.
- **"too old for BepInEx 6"**: the build was made with Unity 2018.1 or older (Rec Room's December 2018 builds), or its IL2CPP
  metadata is older than version 24. Use a 2019 build.
- **"Compatible build"**: it installs and starts. If Mario doesn't appear, `BepInEx\LogOutput.log` says which part didn't fit
  that build. The tested build above is the one known to work.
- **"BepInEx's interop cache was incomplete"**: this is fixed for you. BepInEx rebuilds the cache on that start, which takes a
  few minutes.
- **A `BepInEx-before-mario-<date>` folder appeared**: setup moved files that were in the way into it (an old loader, a
  hand-copied mod). Nothing was deleted. Remove the folder once everything works.
- **"Not Super Mario 64 (USA) in .z64 format"** (or "not found"): check the path, the region and the byte order.
- **The bar sits still on "Starting Rec Room" or says BepInEx has not started**: either BepInEx isn't installed in the client
  folder (run Setup again), or antivirus blocked `winhttp.dll`.
- **Nothing for a long time on a first start**: that's normal for the first few minutes (see above). With no internet
  connection, the first start can't finish. Connect and start again.
- **Rec Room closes during the first start**: look at `logs\<date>\player.log`. BepInEx's own log is in the client folder under
  `BepInEx\LogOutput.log`.
- Everything the mod does is written to `BepInEx\LogOutput.log` with a `mario-` prefix (the launcher's Log tab shows the recent
  lines).
- **Windows says it protected your PC** when you open `Start-Mario.cmd`. The launcher isn't code-signed. Choose *More info*, then
  *Run anyway*, if you trust where you got the zip.
