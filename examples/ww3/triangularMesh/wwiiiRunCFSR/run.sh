#exepath=/STORAGE/usr/WaveWatchIII/v4.18_ww3SpaceResNumericalErr/exe
exepath=/home/lmentaschi/src/git/EMC_ww3/model/exe_uostMPI
exepath=/home/lmentaschi/src/git/EMC_ww3/model/exe
exepath=/home/lmentaschi/src/git/EMC_ww3_backup/model/exe_unstWorkingUOST
pycmd=/home/lmentaschi/usr/python/bin/python
mpiruncmd=mpirun.mpich
nproc=4

rm -rf run
mkdir run
cd run
ln -s ../* ./

$exepath/ww3_grid | tee ww3_grid.out

$pycmd interpWindDataToMesh.py

$exepath/ww3_prep

$mpiruncmd -np $nproc $exepath/ww3_shel | tee ww3_shel.out
#$exepath/ww3_shel | tee ww3_shel.out
#gdb $exepath/ww3_shel

rm ww3.*.nc
$exepath/ww3_ounf

