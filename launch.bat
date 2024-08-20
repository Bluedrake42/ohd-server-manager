@echo off
start server\HarshDoorstop\Binaries\Win64\HarshDoorstopServer.exe Risala?BluforNumBots=16?OpforNumBots=16?MaxPlayers=64?Game=/BigLearning/Core/BP_BLGame_Testing.BP_BLGame_Testing_C -log -MapCycle=MapCycle.cfg -AdminList=Admins.cfg -SteamServerName="Event Playtest Server" %*
echo Server started.