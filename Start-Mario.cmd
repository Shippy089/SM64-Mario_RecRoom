@echo off
rem Opens the Mario for Rec Room launcher. Extra words are passed on: Start-Mario quest jumbotron
set "EXE=%~dp0dist\MarioLauncher.exe"
if not exist "%EXE%" set "EXE=%~dp0src\Launcher\bin\Release\net10.0\MarioLauncher.exe"
if not exist "%EXE%" (
  echo MarioLauncher.exe was not found next to Start-Mario.cmd.
  echo If you opened this from inside the zip, close it, right-click the zip, choose "Extract All", and start it from the extracted folder.
  if exist "%~dp0src\Launcher\Launcher.csproj" echo From a source checkout, build it first:  dotnet build -c Release
  pause
  exit /b 1
)
rem A DOTNET_ROOT left behind by some other tool, with no runtime in it, stops a source build from starting. Ignore it then.
if defined DOTNET_ROOT if not exist "%DOTNET_ROOT%\shared\Microsoft.NETCore.App" set "DOTNET_ROOT="
"%EXE%" %*
set "CODE=%ERRORLEVEL%"
rem Double-clicked and it did not run: keep the window open so the message stays readable.
if "%~1"=="" if not "%CODE%"=="0" (
  echo.
  echo The launcher stopped with code %CODE%. The lines above say why.
  pause
)
exit /b %CODE%
