@echo off
setlocal enabledelayedexpansion

echo Starting server...

rem Start the server
start "" /B "server\HarshDoorstop\Binaries\Win64\HarshDoorstopServer.exe" Khafji?BluforNumBots=16?OpforNumBots=16?MaxPlayers=64?Game=/ConstructionPrototype/GameMode/BP_HDGame_AdvanceAndSecure_Construct.BP_HDGame_AdvanceAndSecure_Construct_C?BluforFaction=BP_HDFactionInfo_PMC_Construct?OpforFaction=BP_HDFactionInfo_Insurgents_Construct -log -MapCycle=MapCycle.cfg -AdminList=Admins.cfg -SteamServerName="Event Playtest Server" %*

rem Wait a moment for the process to start
timeout /t 5 /nobreak

rem Find the PID of the server
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq HarshDoorstopServer.exe" /fo list ^| find "PID:"') do set "PID=%%a"

if not defined PID (
    echo Failed to capture PID. Server may not have started correctly.
    pause
    goto :EOF
)

echo Server started with PID: !PID!

echo Waiting...
rem Waiting...
timeout /t 20 /nobreak

echo Terminating server...
rem Terminate the specific server process
taskkill /F /PID !PID!
if errorlevel 1 (
    echo Failed to terminate server with PID !PID!.
) else (
    echo Server with PID !PID! terminated.
)

echo Calling update.bat...
rem Call update.bat
call update.bat
echo Update completed.

echo Script finished. Press any key to exit.
pause

endlocal
