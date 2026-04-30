@echo off
for /f "delims=" %%i in ('python -c "from modules.config import VERSION; print(VERSION)"') do set VERSION=%%i

python -m nuitka ^
  --mode=onefile ^
  --clang ^
  --assume-yes-for-downloads ^
  --windows-icon-from-ico=icon.ico ^
  --windows-uac-admin ^
  --output-dir=build ^
  --output-filename="Dead by Daylight Tools.exe" ^
  --remove-output ^
  --product-name="Dead by Daylight Tools" ^
  --file-description="TUI utility for managing Dead by Daylight regions" ^
  --product-version=%VERSION%.0 ^
  --file-version=%VERSION%.0 ^
  --copyright="Copyright 2026 @emptyenemy" ^
  --company-name="@emptyenemy" ^
  --trademarks="Dead by Daylight is a trademark of Behaviour Interactive Inc. Not affiliated with or endorsed by Behaviour Interactive." ^
  --include-package=rich ^
  main.py
