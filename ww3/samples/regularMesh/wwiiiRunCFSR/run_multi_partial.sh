#!/bin/bash
#############################################################################
#                                                                           #
# run_WW3.sh  : Script to run wave model end to end.           #
#                                                                           #
# Grids available in this test :                                            #
#                                                                           #
#                                                                           #
#  Remarks :                                                                #
#                                             Hendrik Tolman, Jan. 2012     #
#                                                                           #
#    Copyright 2012-2013 National Weather Service (NWS),                    #
#       National Oceanic and Atmospheric Administration.  All rights        #
#       reserved.  WAVEWATCH III is a trademark of the NWS.                 #
#       No unauthorized use without permission.                             #
#                                                                           #
#############################################################################

# FIRST PARAMETER: simulation start date
# SECOND PARAMETER: simulation end date

# 0. Preparations -----------------------------------------------------------

  set -e



	# Time inputs
	t_beg=$1  # Starting time of run
  	t_end=$2  # Ending time of run
 	t_rst=$t_end                 # Time for restart file, if empty no restart file
        computeoutput=$3;
        gridname=$4;
        nproc=$5
        mpicmd=$6
	exepath=$7

	dtmap='14400'			# time step for map outputs
	dtpoint='10800'			# time step for point outputs
        dtspec='14400'                     # time step for spectra point output
	strt_val='3'			# Value for the strt input file
        computeSpectrum='true';
	
	wind='yes'
	

t_endmap=`./date.py -f "%Y%m%d %H%M%S" -s "$t_end" -t second -d -$dtmap`;
t_endpoint=`./date.py -f "%Y%m%d %H%M%S" -s "$t_end" -t second -d -$dtpoint`;
t_endspec=`./date.py -f "%Y%m%d %H%M%S" -s "$t_end" -t second -d -$dtspec`;

ntmap=`./dateInterval.py -f "%Y%m%d %H%M%S" -s "$t_beg" -e "$t_end" -d $dtmap`
ntpoint=`./dateInterval.py -f "%Y%m%d %H%M%S" -s "$t_beg" -e "$t_end" -d $dtpoint`
ntspec=`./dateInterval.py -f "%Y%m%d %H%M%S" -s "$t_beg" -e "$t_end" -d $dtspec`



echo;
echo;
echo 'Running partial simulation'       
echo 'start date '$t_beg;
echo 'end date '$t_end;
echo 'end date for map generation '$t_endmap;
echo 'number of time interval for map: '$ntmap;
echo 'end date for point tables generation '$t_endpoint;
echo 'number of time interval for point table: '$ntpoint;
echo 'end date for spectrum generation '$t_endspec;
echo 'number of time interval for point spectrum: '$ntspec;


# 4. Main program -----------------------------------------------------------

rm  -f ww3_multi.inp

cat > shelHeader.txt << EOF
$ WAVEWATCH III multi-grid input file
$ ------------------------------------
  1 1 T 3 F T
$
EOF

echo '  '\'"$gridname"w\'  F F T F F F F >> shelHeader.txt;
echo '  '\'points\' >> shelHeader.txt;
 
cat > shelHeader2.txt << EOF
$
   $t_beg  $t_end
$
   T T
$
   $t_beg  $dtmap  $t_end
  N
$ DPT WLV HS LM T0M1 CGE FP DIR SPR DP
  DPT WLV HS LM T0M1 CGE FP DIR SPR PHS PTP PDIR TWS PNR
   $t_beg  $dtpoint  $t_end
EOF

cat > shelFooter.txt << EOF
     0.0   0.0  'STOPSTRING'  999.   XXX  NCEP     99 
   $t_beg     0  $t_end
$ writing restart at the end of the run
   $t_end     3600  $t_end
$ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
   $t_beg     0  $t_end
   $t_beg     0  $t_end
$    0 9999 1 0 9999 1 T
$
  'the_end'  0
$
  'STP'
$
$ End of input file
EOF

# Merge all files
cat shelHeader.txt >> ww3_multi.inp
cat gridlist.txt >> ww3_multi.inp
cat shelHeader2.txt >> ww3_multi.inp
cat output.points >> ww3_multi.inp
cat shelFooter.txt >> ww3_multi.inp

rm -f shelHeader.txt
rm -f shelHeader2.txt
rm -f shelFooter.txt

  echo ' '
  echo '+--------------------+'
  echo '|    Main program    |'
  echo '+--------------------+'
  echo ' '



# echo "   Screen ouput routed to ww3_shel.out"
#	ln -s ww3_shel.const.inp ww3_shel.inp
  echo 'screen output of ww3_multi routed to ww3_multi.out'
  export G95_UNBUFFERED_6=t;
  export G95_UNBUFFERED_0=t;
  export LD_LIBRARY_PATH=;
  set +e;
# $exepath/ww3_multi  > ww3_multi.out 2>&1 &

  # call to launch ww3 parallel from menta pc
# /usr/lib64/mpich/bin/mpirun -np 12 $exepath/ww3_multi > ww3_multi.out 2>&1 &

  if (( $nproc==1 ));
  then
    $exepath/ww3_multi > ww3_multi.out 2>&1 &
  else
    $mpicmd -np $nproc $exepath/ww3_multi > ww3_multi.out 2>&1 &
  fi

  # call to launch ww3 parallel from the jrc hpc cluster
  #$PWD/qsubSync.sh $PWD/ww3_multi.pbs

  wait;
  set -e;

  echo;
  echo;
  echo 'DEALING WITH RESTART FILES';
  echo 'removing the restart file of the previous simulation'
  rm -f restart_previousSim*.*;
  echo;
  echo 'backing up restart files of current simulation:';
  for f in `find ./ -name 'restart.*'`; 
  do 
    echo '  moving file '$f' ...'; 
    nf=`echo $f | sed 's/\(restart\)\(\.\([^ ]*\)\)/\1_previousSim\2/'`; 
    echo '  to file '$nf; 
    mv $f $nf;
  done
  echo;
  currentRestartFiles=`find ./ -name 'restart001.*'`;
  if [ ! $currentRestartFiles ];
  then
    echo 'ERROR: NO RESART FILE DETECTED, QUITTING';
    exit 10;
  fi
  echo 'postioning restart files for the next simulation:';
  for f in `find ./ -name 'restart001.*'`; 
  do 
    echo '  moving file '$f' ...'; 
    nf=`echo $f | sed 's/\(restart\)001\(\.\([^ ]*\)\)/\1\2/'`; 
    echo '  to file '$nf; 
    mv $f $nf;
  done;

  if [ $computeoutput == 'false' ] 
  then
    echo 'Output should not be produced. Quitting partial run.';
    exit;
  fi

  echo;
  echo;
  echo 'Generating output';
  echo 'setting genoutput status';
  touch genoutput;

# rm -f fort.* ww3_shel.inp test*

#  if [ -f restart001.ww3 ] ; then
#    mkdir -p restarts
#    echo "   Saving restart001.ww3 as restart.$grid.$rdate.$rtime"
#    echo "      in restarts ..."
#    mv restart001.ww3 restarts/restart.$grid.$rdate.$rtime
#  fi

# 4. Gridded output ---------------------------------------------------------
rm  -f ww3_ounf.inp

cat > ww3_ounf.inp << EOF
$ -------------------------------------------------------------------- $
$ WAVEWATCH III Grid output post-processing                            $
$ -------------------------------------------------------------------- $
$ Time, time increment and number of outputs
$
  $t_beg $dtmap $ntmap
$
$
$ Output request flags identifying fields as in ww3_shel.inp. See that
$ file for a full documentation of field output options. Namelist type
$ selection is used here (for alternative F/T flags, see ww3_shel.inp).
$
  N
$ DPT WLV HS LM T0M1 CGE FP DIR SPR DP
  HS T0M1 DIR SPR PHS PTP PDIR TWS PNR
$
$ -------------------------------------------------------------------- $
$ Output type 4 [3,4] (version netCDF)   
$        and   variable type 4 [2 = SHORT, 3 = it depends , 4 = REAL]
$ Output type 0 1 2 [0,1,2,3,4,5]   (swell partition)
$ variables T [T] or not [F] in the same file
$
  4 4
  0 1 2
  T
$
$ -------------------------------------------------------------------- $
$ File prefix
$ number of characters in date
$ IX, IY range
$
 ww3.         
 6
 1 999 1 999
$
$ For each field and time a new file is generated with the file name
$ ww3.date_xxx.nc , where date is a conventional time idicator with S3
$ characters,
$ and xxx is a field identifier.
$
$ -------------------------------------------------------------------- $
$ End of input file                                                    $
$ -------------------------------------------------------------------- $
EOF

  echo ' '
  echo '+--------------------+'
  echo '|   Gridded output   |'
  echo '+--------------------+'
  echo ' '

# ./run_multi_output.sh

# 5. Main program -----------------------------------------------------------

rm  -f ww3_gint.inp

cat > gintHeader.txt << EOF
$ -------------------------------------------------------------------- $
$ WAVEWATCH III Grid integration input file                            $
$ -------------------------------------------------------------------- $
$ Time, time increment and number of outputs
$
  $t_beg $dtmap $ntmap
$
$ Total number of grids (NGR). The code assumes that the first NGR-1  
$ grids are the input grids and the last grid is the target grid in 
$ which the output fields are to be interpolated. It also assumes
$ that all the grids have the same output fields switched on 
$
$ NGR
$  
EOF
 
cat > gintHeader2.txt << EOF
$ In this example grd1, grd2 and grd3 are the input grids. For each
$ of these grids a mod_def.grdN and an out_grd.grdN are available.
$ The target grid is grd4, and a mod_def.grd4 is also made available.
$ Upon execution of the code an out_grd.grd4 is generated via
$ interpolation of output fields from the various out_grd.grdN
$ (N variying from 1 to 3) files.
$
$ -------------------------------------------------------------------- $
$ End of input file                                                    $
$ -------------------------------------------------------------------- $ 
EOF

# Merge all files
cat gintHeader.txt >> ww3_gint.inp
cat gridlistGint.txt >> ww3_gint.inp
cat gintHeader2.txt >> ww3_gint.inp

rm -f gintHeader.txt
rm -f gintHeader2.txt

 echo ' '
  echo '+--------------------+'
  echo '|   Merging Gridded output   |'
  echo '+--------------------+'
  echo ' '

$exepath/ww3_gint > ww3_gint.out

rm -f mod_def.ww3 

ln -sf mod_def.grout mod_def.ww3

ln -sf out_grd.grout out_grd.ww3

 echo ' '
  echo '+--------------------+'
  echo '|   Exporting Gridded output   |'
  echo '+--------------------+'
  echo ' '

$exepath/ww3_ounf > ww3_ounf.out 











# 5. Point output -----------------------------------------------------------
rm  -f ww3_ounp_table.inp

cat > ww3_ounp_table.inp << EOF
$ -------------------------------------------------------------------- $
$ WAVEWATCH III NETCDF Point output post-processing                    $
$ --------------------------------------------------------------------- $
$ First output time (yyyymmdd hhmmss), increment of output (s), 
$ and number of output times.
$
  $t_beg $dtpoint $ntpoint
$
$ Points requested --------------------------------------------------- $
$
$ Define points index for which output is to be generated. 
$ If no one defined, all points are selected
$ One index number per line, negative number identifies end of list.
$ 1
$ 2
 -1
$
$ file prefix
 ww3.
$
$ number of characters in date
 6
$
$ version netCDF [3,4]
 4
$
$ Points in same file [T] or not [F] and max number of points to be 
$ processed in one pass
 T 100 
$
$ Output type ITYPE [0,1,2,3]
 2
$
$ Flag for global attributes WW3 [0] or variable version [1-2-3-4]
 0
$ -------------------------------------------------------------------- $
$ ITYPE = 0, inventory of file.
$            No additional input, the above time range is ignored.
$
$ -------------------------------------------------------------------- $
$ ITYPE = 1, netCDF Spectra.
$          - Sub-type OTYPE :  1 : Print plots.
$                              2 : Table of 1-D spectra
$                              3 : Transfer file.
$                              4 : Spectral partitioning.
$          - Scaling factors for 1-D and 2-D spectra Negative factor
$            disables, output, factor = 0. gives normalized spectrum.
$
$ 3  1  0
$
$ The transfer file contains records with the following contents.
$
$ - File ID in quotes, number of frequencies, directions and points.
$   grid name in quotes (for unformatted file C*21,3I,C*30).
$ - Bin frequencies in Hz for all bins.
$ - Bin directions in radians for all bins (Oceanographic conv.).
$                                                         -+
$ - Time in yyyymmdd hhmmss format                         | loop
$                                             -+           |
$ - Point name (C*10), lat, lon, d, U10 and    |  loop     | over
$   direction, current speed and direction     |   over    |
$ - E(f,theta)                                 |  points   | times
$                                             -+          -+
$
$ -------------------------------------------------------------------- $
$ ITYPE = 2, netCDF Tables of (mean) parameter
$          - Sub-type OTYPE :  1 : Depth, current, wind
$                              2 : Mean wave pars.
$                              3 : Nondimensional pars. (U*)
$                              4 : Nondimensional pars. (U10)
$                              5 : 'Validation table'
$                              6 : WMO standard output 
  2
$
$ -------------------------------------------------------------------- $
$ ITYPE = 3, netCDF Source terms
$          - Sub-type OTYPE :  1 : Print plots.
$                              2 : Table of 1-D S(f).
$                              3 : Table of 1-D inverse time scales
$                                  (1/T = S/F).
$                              4 : Transfer file
$          - Scaling factors for 1-D and 2-D source terms. Negative
$            factor disables print plots, factor = 0. gives normalized
$            print plots.
$          - Flags for spectrum, input, interactions, dissipation,
$            bottom and total source term.
$          - scale ISCALE for OTYPE=2,3
$                              0 : Dimensional.
$                              1 : Nondimensional in terms of U10
$                              2 : Nondimensional in terms of U*
$                             3-5: like 0-2 with f normalized with fp.
$
$  4  0  0  T T T T T T  0
$
$ The transfer file contains records with the following contents.
$
$ - File ID in quotes, nubmer of frequencies, directions and points,
$   flags for spectrum and source terms (C*21, 3I, 6L)
$ - Bin frequencies in Hz for all bins.
$ - Bin directions in radians for all bins (Oceanographic conv.).
$                                                         -+
$ - Time in yyyymmdd hhmmss format                         | loop
$                                             -+           |
$ - Point name (C*10), depth, wind speed and   |  loop     | over
$   direction, current speed and direction     |   over    |
$ - E(f,theta) if requested                    |  points   | times
$ - Sin(f,theta) if requested                  |           |
$ - Snl(f,theta) if requested                  |           |
$ - Sds(f,theta) if requested                  |           |
$ - Sbt(f,theta) if requested                  |           |
$ - Stot(f,theta) if requested                 |           |
$                                             -+          -+
$
$ -------------------------------------------------------------------- $
$ End of input file                                                    $
$ -------------------------------------------------------------------- $
EOF

rm  -f ww3_ounp_spectra.inp

cat > ww3_ounp_spectra.inp << EOF
$ -------------------------------------------------------------------- $
$ WAVEWATCH III NETCDF Point output post-processing                    $
$ --------------------------------------------------------------------- $
$ First output time (yyyymmdd hhmmss), increment of output (s), 
$ and number of output times.
$
  $t_beg $dtspec $ntspec
$
$ Points requested --------------------------------------------------- $
$
$ Define points index for which output is to be generated. 
$ If no one defined, all points are selected
$ One index number per line, negative number identifies end of list.
$ 1
$ 2
EOF

cat spectra.ptids >> ww3_ounp_spectra.inp;

cat >> ww3_ounp_spectra.inp << EOF
 -1
$
$ file prefix
 ww3.
$
$ number of characters in date
 6
$
$ version netCDF [3,4]
 4
$
$ Points in same file [T] or not [F] and max number of points to be 
$ processed in one pass
 T 100 
$
$ Output type ITYPE [0,1,2,3]
 1
$
$ Flag for global attributes WW3 [0] or variable version [1-2-3-4]
 0
$ -------------------------------------------------------------------- $
$ ITYPE = 0, inventory of file.
$            No additional input, the above time range is ignored.
$
$ -------------------------------------------------------------------- $
$ ITYPE = 1, netCDF Spectra.
$          - Sub-type OTYPE :  1 : Print plots.
$                              2 : Table of 1-D spectra
$                              3 : Transfer file.
$                              4 : Spectral partitioning.
$          - Scaling factors for 1-D and 2-D spectra Negative factor
$            disables, output, factor = 0. gives normalized spectrum.
$
  3  1  0
$
$ The transfer file contains records with the following contents.
$
$ - File ID in quotes, number of frequencies, directions and points.
$   grid name in quotes (for unformatted file C*21,3I,C*30).
$ - Bin frequencies in Hz for all bins.
$ - Bin directions in radians for all bins (Oceanographic conv.).
$                                                         -+
$ - Time in yyyymmdd hhmmss format                         | loop
$                                             -+           |
$ - Point name (C*10), lat, lon, d, U10 and    |  loop     | over
$   direction, current speed and direction     |   over    |
$ - E(f,theta)                                 |  points   | times
$                                             -+          -+
$
$ -------------------------------------------------------------------- $
$ ITYPE = 2, netCDF Tables of (mean) parameter
$          - Sub-type OTYPE :  1 : Depth, current, wind
$                              2 : Mean wave pars.
$                              3 : Nondimensional pars. (U*)
$                              4 : Nondimensional pars. (U10)
$                              5 : 'Validation table'
$                              6 : WMO standard output 
$  4
$
$ -------------------------------------------------------------------- $
$ ITYPE = 3, netCDF Source terms
$          - Sub-type OTYPE :  1 : Print plots.
$                              2 : Table of 1-D S(f).
$                              3 : Table of 1-D inverse time scales
$                                  (1/T = S/F).
$                              4 : Transfer file
$          - Scaling factors for 1-D and 2-D source terms. Negative
$            factor disables print plots, factor = 0. gives normalized
$            print plots.
$          - Flags for spectrum, input, interactions, dissipation,
$            bottom and total source term.
$          - scale ISCALE for OTYPE=2,3
$                              0 : Dimensional.
$                              1 : Nondimensional in terms of U10
$                              2 : Nondimensional in terms of U*
$                             3-5: like 0-2 with f normalized with fp.
$
$  4  0  0  T T T T T T  0
$
$ The transfer file contains records with the following contents.
$
$ - File ID in quotes, nubmer of frequencies, directions and points,
$   flags for spectrum and source terms (C*21, 3I, 6L)
$ - Bin frequencies in Hz for all bins.
$ - Bin directions in radians for all bins (Oceanographic conv.).
$                                                         -+
$ - Time in yyyymmdd hhmmss format                         | loop
$                                             -+           |
$ - Point name (C*10), depth, wind speed and   |  loop     | over
$   direction, current speed and direction     |   over    |
$ - E(f,theta) if requested                    |  points   | times
$ - Sin(f,theta) if requested                  |           |
$ - Snl(f,theta) if requested                  |           |
$ - Sds(f,theta) if requested                  |           |
$ - Sbt(f,theta) if requested                  |           |
$ - Stot(f,theta) if requested                 |           |
$                                             -+          -+
$
$ -------------------------------------------------------------------- $
$ End of input file                                                    $
$ -------------------------------------------------------------------- $
EOF
    
  echo ' '
  echo '+--------------------+'
  echo '|    Point output    |'
  echo '+--------------------+'
  echo ' '
  
echo 'Generating table'

rm -f mod_def.ww3
ln -s mod_def.points mod_def.ww3

rm -f out_pnt.ww3
ln -s out_pnt.points out_pnt.ww3

rm -f ww3_ounp.inp
ln -s ww3_ounp_table.inp ww3_ounp.inp

$exepath/ww3_ounp > ww3_ounp_table.out


if [ $computeSpectrum == true ];
then
  echo 'Generating spectra'
  
  rm -f mod_def.ww3
  ln -s mod_def.points mod_def.ww3
  
  rm -f out_pnt.ww3
  ln -s out_pnt.points out_pnt.ww3
  
  rm -f ww3_ounp.inp
  ln -s ww3_ounp_spectra.inp ww3_ounp.inp

  $exepath/ww3_ounp > ww3_ounp_spectra.out
fi

# 6. End, cleaning up -------------------------------------------------------

# echo ' ' ; echo "Cleaning-up `pwd`"
# rm -f *.ww3

rm -f out_grd.grout;
rm -f out_grd.ww3;
rm -f genoutput;

  echo ' ' ; echo ' '
  echo '                  ======>  END OF PARTIAL WAVEWATCH III  <====== '
  echo '                    ==================================   '
  echo ' '

# End of run_WW3.sh --------------------------------------------------------------


t_beg_fname1=`./date.py -f "%Y%m%d %H%M%S" -s "$t_beg" -t second -d 0 -o "%Y%m"`;
t_beg_fname2=`./date.py -f "%Y%m%d %H%M%S" -s "$t_beg" -t second -d 0 -o "%Y%m%d"`;

fname1="ww3."$t_beg_fname1".nc"
fname2="ww3."$t_beg_fname2".nc"
echo 'moving '$fname1' to '$fname2
mv $fname1 $fname2

fname1="ww3."$t_beg_fname1"_tab.nc"
fname2="ww3."$t_beg_fname2"_tab.nc"
echo 'moving '$fname1' to '$fname2
mv $fname1 $fname2

if [ $computeSpectrum == true ];
then
  fname1="ww3."$t_beg_fname1"_spec.nc"
  fname2="ww3."$t_beg_fname2"_spec.nc"
  echo 'moving '$fname1' to '$fname2
  mv $fname1 $fname2
fi
