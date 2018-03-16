#!/bin/sh
#####################################
exepath=$1
gridname=$2

f=ww3_grid.inp.$gridname;
grid=$gridname
echo '   Preparing grid '$grid;
ln -sf $f ww3_grid.inp;
echo "   Screen ouput routed to ww3_grid."$grid".out";
$exepath/ww3_grid > ww3_grid.$grid.out;
mv mod_def.ww3 mod_def.$grid;
rm -f ww3_grid.inp;

f=ww3_grid.inp."$gridname"w;
grid="$gridname"w
echo '   Preparing grid '$grid;
ln -sf $f ww3_grid.inp;
echo "   Screen ouput routed to ww3_grid."$grid".out";
$exepath/ww3_grid > ww3_grid.$grid.out;
mv mod_def.ww3 mod_def.$grid;
rm -f ww3_grid.inp;

grid=grout
f=ww3_grid.inp.$grid;
echo '   Preparing grid '$grid;
ln -sf $f ww3_grid.inp;
echo "   Screen ouput routed to ww3_grid."$grid".out";
$exepath/ww3_grid > ww3_grid.$grid.out;
mv mod_def.ww3 mod_def.$grid;
rm -f ww3_grid.inp;

grid=points
f=ww3_grid.inp.$grid;
echo '   Preparing grid '$grid;
ln -sf $f ww3_grid.inp;
echo "   Screen ouput routed to ww3_grid."$grid".out";
$exepath/ww3_grid > ww3_grid.$grid.out;
mv mod_def.ww3 mod_def.$grid;
rm -f ww3_grid.inp;



