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

# 0. Preparations -----------------------------------------------------------

  set -e

        # PATH TO THE EXE
	exepath='/home/user/usr/ww3/v6.x/exe'
        exepath='/STORAGE/src1/git/EMC_ww3/model/exe'
        # cdo command
        cdocmd='cdo'
        
        # n of parallel proc for MPI. If nParallelProc==1 runs without mpirun 
        nParallelProc=12
        # command for mpirun
        mpicmd='/usr/lib64/mpich-3.2/bin/mpiexec'

        windFilePath='../windData/wind_g_glb150w.nc'

	# Time inputs
        t_beg=$1;
        if [ ! $t_beg ];
        then
          t_beg='20000101 000000'  # Starting time of run
        fi
  	t_end='20000301 000000'  # Ending time of run
        # the model starts saving when it has warmed up a little
        heatedModelStartDate='20000201';



        pth=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
	cd $pth
        ln -sf $windFilePath ./wind_g_glb150w.nc

        echo 'run time start: '$t_beg;
        echo 'run time end: '$t_end;

#  t_rst='20091231 000000'  # Time for restart file, if empty no restart file
 	t_rst=                   # Time for restart file, if empty no restart file
        dtrestart='1'

	dtmap='14400'			# time step for map outputs
	dtpoint='10800'			# time step for point outputs
        dtspec='14400'                     # time step for spectra point output
	strt_val='3'			# Value for the strt input file
	ncname='wind.nc'
	
	wind='yes';
        gridname='g_glb150';
	




echo '----- Preparation starts.... Cleaning up... -----------'

# IMPORTANT: DO NOT CALL cleanMulti, otherwise when you will 
# restore your run after an acciedental stop, you will lose all your data!!
#./cleanMulti.sh

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

f=ww3_grid.inp."$gridname"w;
cp $f ww3_grid.inp.grout;
./run_gridPreparation.sh $exepath $gridname


#  echo "   Screen ouput routed to ww3_grid.$grid.out"
#  $exepath/ww3_grid > ww3_grid.$grid.out
# $exepath/ww3_grid



# 3. Input fields -----------------------------------------------------------


rm  -f ww3_prnc.inp

cat > ww3_prnc_template.inp << EOF
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
 lon lat
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
  @@NC_FILENAME@@
$
$ -------------------------------------------------------------------- $
$ End of input file                                                    $
$ -------------------------------------------------------------------- $
EOF

  if [ "$wind" = 'yes' ]
  then
    echo '+--------------------+'
    echo '| Input data         |'
    echo '+--------------------+'
    f=ww3_grid.inp."$gridname"w;
    echo ' ';
    grid=`echo $f | sed 's/ww3_grid\.inp\.\(.*\)$/\1/'`;
    echo '  Elaborating grid '$grid;

    if [ -f wind.$grid ];
    then
      echo "  file wind.$grid already exists";
      continue;
    fi
    
    echo '  Interpolating wind';
    actncname='wind_'$grid'.nc';
    if [ ! -f $actncname ];
    then
      $cdocmd -f nc remapbil,cdo_$grid.cdo $ncname $actncname; 
    else
      echo "  file $actncname already exists";
    fi

    echo '  Preparing inp file';
    cp ww3_prnc_template.inp ww3_prnc.inp;
    sed -i "s/@@NC_FILENAME@@/$actncname/" ww3_prnc.inp;

    FLHW='F'
  
    echo '  Generating input wind fields ...'
  
    echo "  Screen ouput routed to ww3_prep.$grid.out"
    
    echo '  Importing NetCDF wind'
    
    ln -sf mod_def.$grid mod_def.ww3
    if [ ! -f wind.$grid ];
    then
      $exepath/ww3_prnc > ww3_prep.$grid.out
      mv wind.ww3 wind.$grid
      #rm $actncname;
      rm ww3_prnc.inp;
    else
      echo "  file wind.$grid already exists";
    fi
    echo ' '
  else
    FLHW='T'
  fi
rm ww3_prnc_template.inp
if [ -f $ncname ];
then 
  rm $ncname
fi

echo;
echo;
echo 'looping over times'
t_act=`echo $t_beg | sed 's/\([0-9]*\) \([0-9]*\)/\1/'`;
t_end=`echo $t_end | sed 's/\([0-9]*\) \([0-9]*\)/\1/'`;
echo 'loop start time: '$t_act;
echo 'loop end time: '$t_end;
while [ $t_act -lt $t_end ];
do
  echo;
  echo;
  echo;
  echo;
  #t_actend=`./date.py -f %Y%m%d -s $t_act -t month -d $dtrestart -m`;
  t_actend=`./date.py -f %Y%m%d -s $t_act -t halfmonth`;
  if [ $t_actend -gt $t_end ];
  then 
    t_actend=$t_end;
  fi
  echo 'modelling from '$t_act' to '$t_actend;
  echo;
 
  # computing output only outside the heating time
  if [ $t_act -ge $heatedModelStartDate ];
  then
    computeoutput=true;
  else
    echo 'Date '$t_act' is within heating time.';
    echo 'Final output should NOT be produced for this partial run.';
    computeoutput=false;
  fi

  ./run_multi_partial.sh "$t_act 000000" "$t_actend 000000" $computeoutput $gridname $nParallelProc $mpicmd $exepath;
  exitstatus=$?;
  if [ ! -n exitstatus ]; then exit; fi;
  #t_act=`./date.py -f %Y%m%d -s $t_act -t month -d $dtrestart -m`;
  t_act=`./date.py -f %Y%m%d -s $t_act -t halfmonth`;
done;

rm wind.*

  echo ' ' ; echo ' '
  echo '                  ======>  END OF WAVEWATCH III  <====== '
  echo '                    ==================================   '
  echo ' '

# End of run_WW3.sh --------------------------------------------------------------
