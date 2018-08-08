#exepath=/STORAGE/usr/WaveWatchIII/v4.18_ww3SpaceResNumericalErr/exe
exepath=/STORAGE/src1/git/EMC_ww3/model/exe/
pycmd=/STORAGE/usr/anaconda2/bin/python2.7
mpiruncmd=/usr/lib64/mpich-3.2/bin/mpirun
nproc=12

rm -rf run
mkdir run
cd run
ln -s ../* ./

$exepath/ww3_grid

$pycmd interpWindDataToMesh.py

$exepath/ww3_prep

$mpiruncmd -np $nproc $exepath/ww3_shel | tee ww3_shel.out
#$exepath/ww3_shel | tee ww3_shel.out
#gdb $exepath/ww3_shel

rm ww3.*.nc
$exepath/ww3_ounf

