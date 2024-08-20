@echo off
:start

echo Running update...
call update.bat

echo Update complete. Starting server...
timeout /t 5 /nobreak > nul

start server\HarshDoorstop\Binaries\Win64\HarshDoorstopServer.exe AAS-TestMap?MaxPlayers=16 -log -SteamServerName="Harsh Doorstop Dedicated Server" %*

echo Server started. Press any key to stop the server and update again.
pause > nul

echo Stopping server...
taskkill /F /IM HarshDoorstopServer.exe
timeout /t 10 /nobreak > nul

echo Server stopped. Restarting process...
goto start
