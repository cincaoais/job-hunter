@echo off
REM Deploy job-hunter into Claude Code (user scope): skill + /job-* slash commands.
REM Run this after editing anything under job-hunting/ or claude-code/commands/.
cd /d "%~dp0"
set "DEST_SKILL=%USERPROFILE%\.claude\skills\job-hunting"
set "DEST_CMD=%USERPROFILE%\.claude\commands"
if not exist "%DEST_CMD%" mkdir "%DEST_CMD%"
robocopy job-hunting "%DEST_SKILL%" /MIR >nul
del /q "%DEST_CMD%\job-*.md" 2>nul
copy /y "claude-code\commands\job-*.md" "%DEST_CMD%\" >nul
echo Deployed skill    -^> %DEST_SKILL%
echo Deployed commands -^> %DEST_CMD%
echo Restart Claude Code to pick up new commands/skill.
