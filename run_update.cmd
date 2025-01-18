@echo off
cd /D "%~dp0..\"
FOR /F "eol=# tokens=*" %%i IN (%~dp0.env) DO SET %%i

steamcmd.exe +force_install_dir %~dp0../ +login anonymous +app_update 4020 -beta x86-64 validate +quit
pause
