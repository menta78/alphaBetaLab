for f in `find ./ -name 'ww3_grid.inp.*' | egrep '^\.\/ww3_grid\.inp\.g_(.*)[^w]$'`; 
do 
  echo $f; 
  sed -i 's/   F T T T F T/   T T T T F T/' $f; 
done;
