@echo off 
setlocal enabledelayedexpansion 

rem PLEASE CHECK THIS FIRST!!!
rem -----------
set awvs_cmd="D:\Program Files (x86)\Acunetix\wvs_console.exe"
set output_path=D:\Test\20130519\
set scan_list=test-list.txt
rem -----------

echo -----    Please Check Settings    -----
echo AWVS console command:   !awvs_cmd! 
echo Scan site list file :   !scan_list!
echo Save scan result dir:   !output_path!
echo check
echo ...
if not exist !awvs_cmd!  echo !!!  AWVS console NOT EXIST,Pls reset   !!! 
if not exist !scan_list! echo !!!  Scan list file NOT EXIST,Pls reset !!! 
echo -----  If OK,please PRESS ANY KEY -----
pause

rem read website list file
for /f %%i in (!scan_list!) do ( 
set cc=%%i
echo *************** start scan website  **************** 
echo URL  :  !cc! 
echo Start:  !date! !time!
echo .

set ee=!cc:~0,7!

if !ee! == http://   set dd=!cc:~7!
if !ee! == https:/   set dd=!cc:~8!
if !dd:~-1! == /     set dd=!dd:~0,-1!

set dd=!dd::=!
set dd=!dd:/=_!

if exist !output_path!!dd! set dd=!dd!.!random!
md !output_path!!dd!

if exist !output_path!!dd! echo directory !dd! create OK. 
echo . 

!awvs_cmd! /Scan %%i  /SaveFolder !output_path!!dd! /Save /GenerateReport /ReportFormat pdf /Verbose

echo .
echo URL  :  !cc! 
echo End  :  !date! !time!
echo *************** scan website end ****************
) 

rem  hufuyu@gmail.com

