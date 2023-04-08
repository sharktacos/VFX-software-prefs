if not exist "%LOCALAPPDATA%\EpicGamesLauncher\Saved\Config\Windows\" xcopy GameUserSettings.ini %LOCALAPPDATA%\EpicGamesLauncher\Saved\Config\Windows\ 
if not exist "Z:\Documents\Unreal Projects\" mkdir "Z:\Documents\Unreal Projects\"
"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"
