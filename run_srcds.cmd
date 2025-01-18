@echo off
cd /D "%~dp0..\"
FOR /F "eol=# tokens=*" %%i IN (%~dp0.env) DO SET %%i

start srcds_win64.exe -console -p2p +maxplayers %MAXPLAYERS% +gamemode %GAMEMODE% +map %MAP% +sv_setsteamaccount %GSLT_TOKEN% +host_workshop_collection %WORKSHOP_COLLECTION_ID%
