module load mpi/g_mpich_3.1.4
module load netcdf/g_netcdf_f_4.4.3
module load python/2.7.15/gnu/4.8.3
module load hdf5/g_hdf5_1.8.16
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/APPLICATIONS/netcdf/g_netcdf_c_4.4.0/lib/

mkdir outputs
#/ADAPTATION/mentalo/src/git/schism_master/exe_final/schism.ex_VL_WWM
#gdb /ADAPTATION/mentalo/src/git/schism_master/src/schism.ex_VL_WWM
/ADAPTATION/mentalo/src/git/schism_master/src/schism.ex_VL_WWM
