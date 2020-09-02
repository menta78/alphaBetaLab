function []=SELFE_SLAB(base,hgrid,binary_name,s_or_z,lev_or_zcor,stacks,nspool,test)
% Authors: Sergey Frolov, Paul Turner, Joseph Zhang
% Date: April 2011
% Matlab function to visualize horizontal slabs at either a fix z level
% or at a fix sigma level.
% Before calling this function, add path of m-elio library; e.g. 
% path(path,'/usr/local/cmop/matlab/cmop/m-elio');
% SELFE_SLAB(hgrid,binary_name,s_or_z,lev_or_zcor,stacks,nspool,test)
% Inputs: 
%         base: base directory where 'hgrid' (below) resides (binary files are in base/outputs/)
%         hgrid: 'hgrid.gr3' or 'hgrid.ll';
%         binary_name = 'elev.61', 'salt.63' etc (no stack #)
%         s_or_z = 'S' (along a fixed sigma level) or 'Z' (along a fix z level).
%                  This is not used for 2D variables.
%         lev_or_zcor = level index (1 to nvrt) if s_or_z='S'; z-coordinate value 
%                       (z<0 is below MSL) if s_or_z='Z'. This is not used for 2D variables.
%         stacks: array of stack numbers (e.g. [2 4 5]) in the output file names (related to time)
%         nspool: sub-sampling frequency within each stack (e.g. '1' - include all)
%         test: 'y' (only plot out 1st frame for test); 'n' (plot all frames)
%         In addition, *zcor.63 must also be in this directory.
%         May need to adjust some parameters inside (e.g. caxis) to get right appearance of images
% Outputs: images and slab.avi

% Add m-elio to the matlab path (do this before calling any functions)
path(path,'/usr/local/cmop/matlab/cmop/m-elio');
close all; 
scrsz = get(0,'ScreenSize'); %screen size
figure('Position',[1 scrsz(4)/2 scrsz(3)/2 scrsz(4)/2]); 

% Read a lat/lon .ll grid for other coordinates
gr.hgrid=gr_readHGrid(strcat(base,'/',hgrid));

% For plotting vector scales
xmax=max(gr.hgrid.x); 
xmin=min(gr.hgrid.x); 
ymax=max(gr.hgrid.y); 
ymin=min(gr.hgrid.y); 

% Read the header for variable and vertical grid
header1=sz_readHeader(strcat(base,'/outputs/',num2str(stacks(1)),'_',binary_name));
headerz=sz_readHeader(strcat(base,'/outputs/',num2str(stacks(1)),'_zcor.63'));
dtout=header1.dt; %time step
nrec=header1.nSteps; % # of records in each stack
ivs=header1.flagSv; %1; scalar; 2: vector
i23D=header1.flagDm; %2 or 3D
nvrt=header1.vgrid.nLevels; %surface level index

% Read the variable and the vertical grid
%avi_out = avifile('slab.avi','FPS',5); %output movie to slab.avi

if(strcmp(test,'y'))
  stacks2=stacks(1); it2=1;
else
  stacks2=stacks; it2=nrec;
end

for day=stacks2
  timeout0=(day-1)*nrec*dtout;
  %Read binary files
  header1=sz_readHeader(strcat(base,'/outputs/',num2str(day),'_',binary_name));
  headerz=sz_readHeader(strcat(base,'/outputs/',num2str(day),'_zcor.63'));

  %Outputs from the function sz_readTimeStep:
  %ts: info for each record (time stamp, iteration #, and elevation);
  %d(dataVector,vectorComponent_k,time_iteration)
  % where: dataVector is of size 'gridSize' (sum(np*(local levels)) for 3D);
  %        vectorComponent_k is either 1 or 2 (scalar or vector);
  %        time_iteration is record number in the binary file.
  [d ts]=sz_readTimeStep(header1,1:nrec); 
  [dz tsz]=sz_readTimeStep(headerz,1:nrec); 

  for it=1:nspool:it2;
    timeout=timeout0+it*dtout;
    time_d=fix(timeout/86400);
    time_h=fix((timeout-time_d*86400)/3600);
    time_m=fix((timeout-time_d*86400-time_h*3600)/60);
    time_s=timeout-time_d*86400-time_h*3600-time_m*60;

    if(i23D==2)
      uout=d(:,1,it); %uout(1:np)
      vout=d(:,ivs,it);
    else %3D variable
      % For 3D variables, map outputs to a regular matlab structure
      % Last argument "1" is a flag for vertical levels 1:nvrt (0 for ELCIRC).
      % Output z is a simple 2d aray (1:np,1:nvrt) for 3D variables
      [z] = map_sz2hts(headerz,dz(:,1,it),1);
      [u] = map_sz2hts(header1,d(:,1,it),1);
      if(ivs==2)
        [v] = map_sz2hts(header1,d(:,2,it),1);
      end

      % Extract the slab
      if(strcmp(s_or_z,'S'))
        uout=u(:,lev_or_zcor);
        if(ivs==2)
          vout=v(:,lev_or_zcor);
        end
      else %Z
        myslab = lev_or_zcor*ones(gr.hgrid.np,1);
        uout=filter_depth_q(u, z, myslab); %uout(1:np)
        if(ivs==2)
          vout=filter_depth_q(v, z, myslab);
        end
      end
    end %i23D

    % plot [uout,vout] (1:np)
    % set axes
    axis([xmin xmax ymin ymax]);
    %axis([3.5e5 4.2e5 4.26e6 4.34e6]);
    v2=axis;
    % Write time stamp info
    loc_info_x=(v2(2)+v2(1))/2;
    loc_info_y=v2(4)*1.02-v2(3)*0.02;

    if(ivs==1) %scalar
      h1=patch('Faces',gr.hgrid.elem(:,3:end-1),'Vertices',gr.hgrid.nodes(:,2:end-1),...
      'FaceVertexCData',uout,'FaceColor','interp','EdgeColor','none');
      %line(gr.hgrid.bndLine.X,gr.hgrid.bndLine.Y,'color','k');
      colormap(jet(15));
      % Set colormap range
      caxis([0 5]); colorbar;
    else %vector
      loc_scale_x=v2(2)*0.3+v2(1)*0.7;
      loc_scale_y=-v2(4)*0.02+v2(3)*1.02;
      x_aug=[gr.hgrid.x' loc_scale_x];
      y_aug=[gr.hgrid.y' loc_scale_y];
      quiver(x_aug,y_aug,[uout' 1],[vout' 0]);
      text(loc_scale_x,loc_scale_y,'1 m/s');
    end %ivs
    text(loc_info_x,loc_info_y,{'Time (DD:HH:MM:SS)'; num2str([time_d time_h time_m time_s])});

    %axis off;

    % Add image to avi file
%    frame = getframe(gcf);
%    avi_out=addframe(avi_out,frame);
    if(day ~= stacks2(end) || it ~=it2)
      clf; %clear figure to avoid overlay
    else
      print('-dpng','limon.png');
    end

  end %it
end %for day=stacks2
%avi_out=close(avi_out);
