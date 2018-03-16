#!/bin/bash
# sample call: runall.sh run_D3Djobs.sh A13Hst
scprt=$1;
ptrn=$2;

if [ ! $scprt ] || [ ! $ptrn ];
then
  echo 'sample call: runall.sh run_D3Djobs.sh A13Hst';
  exit;
fi

echo "script name "$scprt;
echo "jobname pattern "$ptrn;
echo "ok? (press y if you agree)";
read ok;
if [ $ok != 'y' ];
then
  exit;
fi
echo;
echo 'launching processes';

i=1;
for d in *; 
do 
  if [ -d $d ]; 
  then 
    echo "elabrating "$d; 
    if [ -f $d/checkfile ]
    then
      echo "checkfile already exists. Skipping directory";
      i=$[$i + 1];
      echo;
      continue;
    fi 
    istr=`printf %02d $i`;
    cmd="qsub -j y -o `pwd`/log$istr.txt -N "$ptrn$istr" -q all.q $scprt";
    echo "launching command:"
    echo $cmd;
    $cmd;
    i=$[$i + 1];
    while [ ! -f $d/checkfile ]
    do
      echo "checkfile not yet generated. Sleeping for 5 seconds.";
      sleep 5;
    done
    echo;
  fi; 
done;
