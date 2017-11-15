#!/bin/sh
#####################################
exepath='/home/lmentaschi/usr/WaveWatchIII/v4.18/exe'
echo "Preparing output for g_glob15 " 
mkdir g_glob15 ; cd g_glob15
ln -sf ../out_grd.g_glob15 out_grd.ww3
ln -sf ../mod_def.g_glob15 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
echo "Preparing output for g_seu05 " 
mkdir g_seu05 ; cd g_seu05
ln -sf ../out_grd.g_seu05 out_grd.ww3
ln -sf ../mod_def.g_seu05 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
echo "Preparing output for g_rSea025 " 
mkdir g_rSea025 ; cd g_rSea025
ln -sf ../out_grd.g_rSea025 out_grd.ww3
ln -sf ../mod_def.g_rSea025 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
echo "Preparing output for g_pac05 " 
mkdir g_pac05 ; cd g_pac05
ln -sf ../out_grd.g_pac05 out_grd.ww3
ln -sf ../mod_def.g_pac05 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
echo "Preparing output for g_jap033 " 
mkdir g_jap033 ; cd g_jap033
ln -sf ../out_grd.g_jap033 out_grd.ww3
ln -sf ../mod_def.g_jap033 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
echo "Preparing output for g_gmex033 " 
mkdir g_gmex033 ; cd g_gmex033
ln -sf ../out_grd.g_gmex033 out_grd.ww3
ln -sf ../mod_def.g_gmex033 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
echo "Preparing output for g_neu025 " 
mkdir g_neu025 ; cd g_neu025
ln -sf ../out_grd.g_neu025 out_grd.ww3
ln -sf ../mod_def.g_neu025 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
echo "Preparing output for g_med025 " 
mkdir g_med025 ; cd g_med025
ln -sf ../out_grd.g_med025 out_grd.ww3
ln -sf ../mod_def.g_med025 mod_def.ww3
ln -sf ../ww3_ounf.inp ww3_ounf.inp
$exepath/ww3_ounf
cd ..
