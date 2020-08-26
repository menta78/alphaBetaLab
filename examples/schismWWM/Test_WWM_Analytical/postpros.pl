#!/usr/bin/perl -w

# Extract time series outputs
if (@ARGV != 3)
{ print "USAGE: $0 <start> <end> <testnm>\n"; exit(1); }
$start=$ARGV[0]; $end=$ARGV[1]; $test=$ARGV[2];

#Prepare screen inputs for extraction
open(RE,">read.in");
print RE "1\n 1\n elev\n $start $end\n 0\n 0\n";
close(RE);
system "rm -f ForPlot_elev.dat; cd outputs/; ln -sf ../station.bp.elev station.bp; ../read_output9_xyz.WW < ../read.in >& scrn.out; mv -f fort.18 ../ForPlot_elev.dat";

open(RE,">read.in");
print RE "1\n 1\n elev\n $start $end\n 0\n 1\n";
close(RE);
system "rm -f ForPlot_elev_prof.dat; cd outputs/; ln -sf ../station.xy station.bp; ../read_output9_xyz.WW < ../read.in >& scrn.out; mv -f fort.18 ../ForPlot_elev_prof.dat";

open(RE,">read.in");
print RE "1\n 1\n WWM_1\n $start $end\n 0\n 1\n";
close(RE);
system "rm -f ForPlot_Hs_prof.dat; cd outputs/; ln -sf ../station.xy station.bp; ../read_output9_xyz.WW < ../read.in >& scrn.out; mv -f fort.18 ../ForPlot_Hs_prof.dat";
