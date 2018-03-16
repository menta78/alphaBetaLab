#!/bin/sh
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

# 0. Preparations -----------------------------------------------------------

  set -e

	exepath='/home/lmentaschi/usr/WaveWatchIII/v4.18/exe'
	


	# Time inputs
	t_beg='20081202 000000'  # Starting time of run
  	t_end='20081205 000000'  # Ending time of run
#  t_rst='20091231 000000'  # Time for restart file, if empty no restart file
 	t_rst=                   # Time for restart file, if empty no restart file

	dtmap='86400'			# time step for map outputs
	dtpoint='10800'			# time step for point outputs
	strt_val='3'			# Value for the strt input file
	ncname='wind.nc'
	
	wind='yes'
	
	 # Time steps
	 dt1='1000.'
	 dt2='250.' 
	 dt3='250.'
	 dt4='10.'



echo '----- Preparation starts.... Cleaning up... -----------'

./cleanMulti.sh

# 0.a Process restarting

  if [ -z "$t_rst" ] ; then
    dt_rst='0'
    t_rst=$t_end
  else
    dt_rst='1'
    rdate=`echo $t_rst | awk '{ print $1 }'`
    rtime=`echo $t_rst | awk '{ print $2 }'`
  fi

# 0.b Clean-up

  echo ' ' ; echo ' '
  echo '                  ======> TEST RUN WAVEWATCH III <====== '
  echo '                    ==================================   '
  echo "                              Running $grid model"
  echo ' '

# 1. Grid pre-processor -----------------------------------------------------


  echo ' '
  echo '+--------------------+'
  echo '|  Grid preprocessor |'
  echo '+--------------------+'
  echo ' '

echo "   Preparing Wind input grid"
ln -sf ww3_grid.inp.wind ww3_grid.inp
$exepath/ww3_grid
mv mod_def.ww3 mod_def.wind
rm  -f ww3_grid.inp

echo "   Preparing output grid"
ln -sf ww3_grid.inp.points ww3_grid.inp
$exepath/ww3_grid
mv mod_def.ww3 mod_def.points
rm  -f ww3_grid.inp

./run_gridPreparation.sh


#  echo "   Screen ouput routed to ww3_grid.$grid.out"
#  $exepath/ww3_grid > ww3_grid.$grid.out
# $exepath/ww3_grid



# 3. Input fields -----------------------------------------------------------


rm  -f ww3_prnc.inp

cat > ww3_prnc.inp << EOF
$ -------------------------------------------------------------------- $
$ WAVEWATCH III Field preprocessor input file                          $
$ -------------------------------------------------------------------- $
$ Mayor types of field and time flag
$   Field types  :  ICE   Ice concentrations.
$                   LEV   Water levels.
$                   WND   Winds.
$                   WNS   Winds (including air-sea temp. dif.)
$                   CUR   Currents.
$                   DAT   Data for assimilation.
$
$   Format types :  AI    Transfer field 'as is'. (ITYPE 1)
$                   LL    Field defined on regular longitude-latitude
$                         or Cartesian grid. (ITYPE 2)
$   Format types :  AT    Transfer field 'as is', performs tidal 
$                         analysis on the time series (ITYPE 6)
$
$        - Format type not used for field type 'DAT'.
$
$   Time flag    : If true, time is included in file.
$   Header flag  : If true, header is added to file.
$                  (necessary for reading, FALSE is used only for
$                   incremental generation of a data file.)
$
  'WND' 'LL' T T
$
$ Name of dimensions ------------------------------------------------- $
$
 longitude latitude
$
$ Variables to use --------------------------------------------------- $
$
  u10 v10
$
$
$
$ Define data files -------------------------------------------------- $
$ The input line identifies the filename using for the forcing field.
$
$ -> filename
$
  $ncname
$
$ -------------------------------------------------------------------- $
$ End of input file                                                    $
$ -------------------------------------------------------------------- $
EOF

  if [ "$wind" = 'yes' ]
  then
    FLHW='F'
    echo ' '
    echo '+--------------------+'
    echo '| Input data         |'
    echo '+--------------------+'
    echo ' '

    echo '   Generating input wind fields ...'

    echo "   Screen ouput routed to ww3_prep.out"
  
    echo 'Importing NetCDF wind'
    
	echo 'before'
    ln -sf mod_def.wind mod_def.ww3
    echo 'after'
	$exepath/ww3_prnc
#	$exepath/ww3_prnc > ww3_prep.$grid.out
	mv wind.ww3 wind.wind
#	rm mod_def.ww3

  else
    FLHW='T'
  fi

# 4. Main program -----------------------------------------------------------

rm  -f ww3_multi.inp

cat > shelHeader.txt << EOF
$ WAVEWATCH III multi-grid input file
$ ------------------------------------
  8 1 T 3 F T
$
 'wind'  F F T F F F F
 'points'
EOF
 
cat > shelHeader2.txt << EOF
$
   $t_beg  $t_end
$
   T T
$
   $t_beg  $dtmap  $t_end
  N
  DPT WLV HS LM CGE FP DIR SPR DP WND
   $t_beg  $dtpoint  $t_end
EOF

cat > shelFooter.txt << EOF
     0.0   0.0  'STOPSTRING'  999.   XXX  NCEP     99 
   $t_beg     0  $t_end
   $t_end     0  $t_end
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
  $exepath/ww3_multi  > ww3_multi.out

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
  $t_beg $dtmap 1000000
$
$
$ Output request flags identifying fields as in ww3_shel.inp. See that
$ file for a full documentation of field output options. Namelist type
$ selection is used here (for alternative F/T flags, see ww3_shel.inp).
$
  N
  DPT WLV HS LM CGE FP DIR SPR DP WND
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
  $t_beg $dtpoint 100000
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
 'wind'
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

ln -s mod_def.wind mod_def.ww3

ln -s out_grd.wind out_grd.ww3

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
  $t_beg $dtpoint 100000
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
  $t_beg $dtpoint 100000
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


echo 'Generating spectra'

rm -f mod_def.ww3
ln -s mod_def.points mod_def.ww3

rm -f out_pnt.ww3
ln -s out_pnt.points out_pnt.ww3

rm -f ww3_ounp.inp
ln -s ww3_ounp_spectra.inp ww3_ounp.inp


$exepath/ww3_ounp > ww3_ounp_spectra.out
	
# 6. End, cleaning up -------------------------------------------------------

  echo ' ' ; echo "Cleaning-up `pwd`"
# rm -f *.ww3

  echo ' ' ; echo ' '
  echo '                  ======>  END OF WAVEWATCH III  <====== '
  echo '                    ==================================   '
  echo ' '

# End of run_WW3.sh --------------------------------------------------------------
