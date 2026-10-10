# Exact versions

These are the versions the mod is built and tested with. Other versions may not work.

| What | Version | Where |
|---|---|---|
| Rec Room client | any compatible old IL2CPP build, December 14, 2018 or later, without anti-cheat (tested: September 9, 2019, Steam app 471710, depot 471711, manifest 3817258843939969587) | your own Steam account |
| BepInEx | 6.0.0-be.788 (commit 5b766a3), IL2CPP win-x64 | https://builds.bepinex.dev/projects/bepinex_be/788/BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.788%2B5b766a3.zip (SHA-256 `f4cc496bd098a0df4164b81e3737297707f13a47c2478dba2f60eefab784817a`) |
| zig | 0.17.0 | https://ziglang.org/download/ |
| libsm64 | commit `fd11813208272b4271d92bd92feb8f3fdbe61be5` | https://github.com/libsm64/libsm64 |
| Mario model (fetched by libsm64's `import-mario-geo.py`) | n64decomp/sm64 commit `06ec56df7f951f88da05f468cdcacecba496145a` | downloaded by that script |
| Super Mario 64 ROM | USA, .z64, SHA-256 `17ce077343c6133f8c9f2d6d6d9a4ab62c8cd2aa57c40aea1f490b4c8bb21d91` | your own cartridge |
| .NET | SDK 10 to build; nothing to run (the release launcher carries its own) | https://dotnet.microsoft.com/download/dotnet/10.0 |

A release zip carries its own build stamp in `VERSION.txt` (the commit, the build time and the SHA-256 of the native library); quote it
when you report a problem. `NOTICE.txt` lists what is in the package and where it comes from.

## Getting the libsm64 source

```
git clone https://github.com/libsm64/libsm64.git native/libsm64
git -C native/libsm64 checkout fd11813208272b4271d92bd92feb8f3fdbe61be5
cd native/libsm64
python import-mario-geo.py
cd ../..
```

The launcher's Set up then builds `dist/native/sm64-mario.dll` from it. The build checks the checkout against
`native/libsm64-source.json` first.
