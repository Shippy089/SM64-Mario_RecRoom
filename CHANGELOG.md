# Changelog

## 2.00

### New

- Luigi. Pick him as the character on the Mario tab. Super Luigi 64 v2.0 by Cjes and CyberTanuki comes with the mod, unchanged, in `characters\`, and is applied to your ROM in memory. He looks and sounds like Luigi and moves like Mario.
- There is one more character. It isn't in the zip, and the Character list only shows it once what it needs is already on your PC. Its numbers don't add up.
- Skins: the Mario tab loads `.marioskin` files from the `skins` folder and shows each one's credits. None come with the mod. See `skins\README.txt`.
- Free roam: past 100 m from the centre of Mario's SM64 world, the centre moves to him between two frames, so the orange tape and the freeze at the edge no longer stop him. It's the same Mario: speed, facing, action, health and camera carry on, in the air or on the ground. Height doesn't move, so the ceiling tape is still there about 150 m up.
- Mario has SM64's round shadow on the floor under him. It shrinks and fades as he goes up and is gone about 6 m up. `shadow = off` turns it off.
- Xbox controllers rumble when Mario gets hurt (harder the more health he loses), dies or lands a ground pound. `rumble = off` turns it off. Other controllers have no rumble.
- The pause screen. Esc (Start on a controller) says PAUSE now instead of just freezing Mario. While paused, C (RB) puts the camera back behind Mario and R (LT / RT) respawns him at the last solid ground he stood on, with the health he had.
- The pause screen and the Mario Controls menu show the buttons of whatever you used last: keyboard keys, or the controller's own button names (Xbox, PlayStation, N64 adapters and others).
- Camera settings on the Mario tab: up and down, left and right, and camera speed.
- Reset to defaults on the Advanced tab, or `Start-Mario reset`. File paths stay.
- Launcher look on the Advanced tab: colour themes, highlight colour, your own gradient colours (two to eight), gradient on the title, still or moving.
- Tabs can be moved and hidden (Advanced tab). The launcher opens on the last tab you used.
- Settings carry over to new versions: a copy of `mario.ini` is kept in `%APPDATA%\MarioForRecRoom`, and a new folder starts from it.

### Changed

- Version number: 2.00 in the launcher, the plugin and `VERSION.txt`.
- Up on the mouse or stick now looks up by default. The old way is "Inverted" on the Mario tab.
- The native library reads Mario's shape and colours from the ROM it's given, so a ROM hack that redraws Mario shows up as itself. The normal ROM gives the same Mario as before.
- The native library reads sound data from wherever a ROM hack keeps it, and animation offsets the way the N64 does. The zip's library already has this; if you build your own, rebuild it with `native\build.ps1`.
- Free roam no longer swaps Mario for a new one at the edge. The old way (a new Mario at the player) is only used if moving the centre fails.

### Fixed

- ROM hacks with bigger sound codebooks than SM64's played loud noise instead of voice clips. The native library had room only for SM64's small codebooks, and the bigger ones overwrote the data next to them. Sound memory sizes are now read from the ROM as well.
- A damaged patch or skin file gets a clear error instead of a crash. A bad skin no longer stops Mario from loading; he keeps his own body.
- Skins are limited to 20000 vertices, 20000 triangles and a 32 MB skin.json, so a broken one can't eat all your memory.
- Gradient colours written with # in `mario.ini` work.
- Skin names with # or ; are quoted, so they read back whole.
- The last tab is saved when the launcher closes, not only when you change something.
- A `--config` file no longer touches the `%APPDATA%` copy.
- The search for patches on your PC gives up after 2 seconds instead of hanging the launcher on a slow drive.
- No more false "possible void" log lines on slopes.
- Less memory churn while Mario is lit.
- The HUD cleans up after itself if it fails to load.

## 1.0.0

First public release.
