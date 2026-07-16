@echo off
rem Rebuild job-hunting.skill on Windows (uses the tar.exe bundled with Windows 10+).
cd /d "%~dp0"
if exist job-hunting.skill del job-hunting.skill
tar --format=zip --exclude ".DS_Store" --exclude "._*" -cf job-hunting.skill job-hunting
echo Built job-hunting.skill:
tar -tf job-hunting.skill
