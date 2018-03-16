#!/bin/sh

  rm -f *.out
  rm -f *.ww3
  rm -f ww3.*
  rm -f mod_def*
  rm -f plot.*
  rm -f plot*.eps
  rm -f plot*.gif
  rm -f plot*.png
  rm -f buoy.all
  rm -f wind.wind

  rm -f ww3_grid.inp
  rm -f ww3_shel.inp

  if [ "$#" -ge '1' ] ; then
    if [ "$1" = 'all' ] ; then
      rm -rf restarts
    fi
  fi

