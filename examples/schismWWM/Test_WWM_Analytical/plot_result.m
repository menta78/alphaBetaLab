% Plot out results for comp.
clear all; close all;
eta_ts=load('elev.dat'); %time (days), eta
eta_new=load('elev_prof.dat'); %x, eta
eta_old=load('elev_prof.dat.0'); %x, eta
eta_obs=load('ana_eta.dat'); %x, eta - analytical soln
Hs_new=load('Hs_prof.dat'); %x, Hsig
Hs_old=load('Hs_prof.dat.0'); 
Hs_obs=load('ana_Hs.dat'); 

subplot(3,1,1);
plot(eta_ts(:,1),eta_ts(:,2),'k');
title({'Analytical test of Longuet-Higgins'; 'Convergence to steady state'});
xlabel('Time (days)');ylabel('Elev.');
subplot(3,1,2);
plot(eta_old(:,1),eta_old(:,2),'b.',eta_new(:,1),eta_new(:,2),'g',eta_obs(:,1),eta_obs(:,2),'r');
title('Comp. of steady-state profiles: set-up');
%v=axis; axis([0 30 v(3) v(4)]);
legend('Old','New','Ana','Location','NorthEastOutside');
xlabel('x (m)'); ylabel('Elev. (m)');
subplot(3,1,3);
plot(Hs_old(:,1),Hs_old(:,2),'b.',Hs_new(:,1),Hs_new(:,2),'g',Hs_obs(:,1),Hs_obs(:,2),'r');
title('Comp. of steady-state profiles: sig. wave height');
%v=axis; axis([0 30 v(3) v(4)]);
legend('Old','New','Ana','Location','NorthEastOutside');
xlabel('x (m)'); ylabel('Hs (m)');

print('-dpng','out.png');
%Make sure exit for batch mode
quit
