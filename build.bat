python -m nuitka ^
  --mode=onefile ^
  --windows-icon-from-ico=icon.ico ^
  --windows-uac-admin ^
  --output-dir=build ^
  --output-filename="Dead by Daylight Tools.exe" ^
  --remove-output ^
  --product-name="Dead by Daylight Tools" ^
  --file-description="TUI utility for managing Dead by Daylight regions" ^
  --product-version=1.0.0.0 ^
  --file-version=1.0.0.0 ^
  --copyright="Copyright 2026 @emptyenemy" ^
  --company-name="@emptyenemy" ^
  --trademarks="Dead by Daylight is a trademark of Behaviour Interactive Inc. Not affiliated with or endorsed by Behaviour Interactive." ^
  --include-package=rich ^
  main.py
