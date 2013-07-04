@echo off 
setlocal enabledelayedexpansion 

rem PLEASE CHANGE THIS FIRST!!!
rem -----------
set awvs_cmd="D:\Program Files (x86)\Acunetix\wvs_console.exe"
set output_path=D:\Test\20130703\
set scan_list=ce-list.txt
rem -----------

echo -----    Please Check Settings    -----
echo AWVS console command:   !awvs_cmd! 
echo Scan site list file :   !scan_list!
echo Save scan result dir:   !output_path!
echo check
echo ...
if !output_path:~-1! NEQ \   set  output_path=!output_path!\
if not exist !output_path!  md !output_path!
if not exist !awvs_cmd!     echo !!!  AWVS console NOT EXIST,Pls reset   !!! 
if not exist !scan_list!    echo !!!  Scan list file NOT EXIST,Pls reset !!! 
if exist !scan_list! and exist !awvs_cmd! ( echo ----- check pass,scan soon ----- )
else(
echo -----  please Reset AWVS_CMD SCAN_LIST ,and retry -----
pause
exit
)

rem read website list file
for /f %%i in (!scan_list!) do ( 
set cc=%%i
rem : fix bug -> site url not start with "http://" or "https://"
rem :            add it as default.
rem : if !cc:~0,4! NEQ http   set cc=http://!cc!
set ee=!cc:~0,7!
if !ee! == http://     set dd=!cc:~7!
if !ee! == https:/     set dd=!cc:~8!

if not defined dd     (set dd=!cc!
set cc=http://!cc!
)

if !dd:~-1! == /        set dd=!dd:~0,-1!
set dd=!dd::=!
set dd=!dd:/=_!

if exist !output_path!!dd! set dd=!dd!.!random!
md !output_path!!dd!
!awvs_cmd! /Scan !cc!  /SaveFolder !output_path!!dd! /Save /GenerateReport /ReportFormat pdf /Verbose
) 

rem  hufuyu@gmail.com
rem  v1.1-20130704


