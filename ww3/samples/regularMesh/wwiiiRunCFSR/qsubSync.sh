#!/bin/bash

#script to submit to a pbs cluster a job and wait for its conclusion

cmd=$1;

sleepingTime=60; # 1 minutes

date;
echo "submitting command "$cmd;
jobId=`qsub $cmd`;
err=$?;
if [ $err != 0 ]
then
  echo "error submitting the job. Quitting";
  exit;
fi
echo 'job id: '$jobId
echo;
while true;
do
  qout=`qstat $jobId`;
  err=$?;
  if [ $err == 0 ]
  then
    dt=`date`;
    #echo -en "\e[1A";
    #echo -e "\e[0K\r"$dt': the job is still running. sleeping for '$sleepingTime' seconds';
    echo -ne "\r"$dt': the job is still running. sleeping for '$sleepingTime' seconds';
    sleep $sleepingTime;
  else
    echo
    echo "job finished. Quitting"
    break;
  fi
done
