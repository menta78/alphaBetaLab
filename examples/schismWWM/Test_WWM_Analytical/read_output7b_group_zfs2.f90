!
!****************************************************************************************
!											*
!	read_output7b with (x,y,z) read in from station.xy (z>=0 is distance from F.S.) 
!         for 3D variables (surface values for 2D variables).
!       Outputs: fort.1[89] 
!											*
!       ifort -Bstatic -assume byterecl -O3 -o read_output7b_group_zfs2 read_output7b_group_zfs2.f90
!****************************************************************************************
!
      program read_out
      parameter(nbyte=4)
!      parameter(mnp=80000)
!      parameter(mne=160000)
!      parameter(mnv=100)
      character*30 file63
      character*12 it_char
      character*48 start_time,version,variable_nm,variable_dim
      character*48 data_format
!      dimension sigma(mnv),cs(mnv),ztot(mnv),x(mnp),y(mnp),dp(mnp),kbp00(mnp),kfp(mnp)
!      dimension nm(mne,4),out(mnp,3,mnv,2),out2(mnp,mnv,2),icum(mnp,mnv,2),eta2(mnp),node3(mnp,3),arco(mnp,3)
!      dimension ztmp(mnv),x00(mnp),y00(mnp),iep(mnp),swild(3),out3(mnp,2),z00(mnp)
      dimension swild(3)
      allocatable :: sigma(:),cs(:),ztot(:),x(:),y(:),dp(:),kbp00(:),kfp(:)
      allocatable :: nm(:,:),out(:,:,:,:),out2(:,:,:),icum(:,:,:),eta2(:),node3(:,:),arco(:,:)
      allocatable :: ztmp(:),x00(:),y00(:),iep(:),out3(:,:),z00(:)
      
      print*, 'Input file to read from (without *_):'
      read(*,'(a30)')file63
      
      print*, 'Input start and end file # to read:'
      read(*,*) iday1,iday2

      print*, 'Input start CORIE day (0 if none):'
      read(*,*) corieday

      open(10,file='station.xy',status='old')
      read(10,*) 
      read(10,*) nxy
      allocate(x00(nxy),y00(nxy),z00(nxy),stat=istat)
      if(istat/=0) stop 'Falied to allocate (1)'

      do i=1,nxy
        read(10,*)j,x00(i),y00(i),z00(i)
        if(z00(i)<0) then
          write(*,*)'Invalid z value:',i; stop
        endif
      enddo !i
      close(10)

!...  Header
!...
      open(63,file='1_'//file63,status='old',access='direct',recl=nbyte)
      irec=0
      do m=1,48/nbyte
        read(63,rec=irec+m) data_format(nbyte*(m-1)+1:nbyte*m)
      enddo
      if(data_format.ne.'DataFormat v5.0') then
        print*, 'This code reads only v5.0:  ',data_format
        stop
      endif
      irec=irec+48/nbyte
      do m=1,48/nbyte
        read(63,rec=irec+m) version(nbyte*(m-1)+1:nbyte*m)
      enddo
      irec=irec+48/nbyte
      do m=1,48/nbyte
        read(63,rec=irec+m) start_time(nbyte*(m-1)+1:nbyte*m)
      enddo
      irec=irec+48/nbyte
      do m=1,48/nbyte
        read(63,rec=irec+m) variable_nm(nbyte*(m-1)+1:nbyte*m)
      enddo
      irec=irec+48/nbyte
      do m=1,48/nbyte
        read(63,rec=irec+m) variable_dim(nbyte*(m-1)+1:nbyte*m)
      enddo
      irec=irec+48/nbyte

      write(*,'(a48)')data_format
      write(*,'(a48)')version
      write(*,'(a48)')start_time
      write(*,'(a48)')variable_nm
      write(*,'(a48)')variable_dim

      read(63,rec=irec+1) nrec
      read(63,rec=irec+2) dtout
      read(63,rec=irec+3) nspool
      read(63,rec=irec+4) ivs
      read(63,rec=irec+5) i23d
      irec=irec+5

      print*, 'i23d=',i23d,' nrec= ',nrec

!     Vertical grid
      read(63,rec=irec+1) nvrt
      read(63,rec=irec+2) kz
      read(63,rec=irec+3) h0
      read(63,rec=irec+4) h_s
      read(63,rec=irec+5) h_c
      read(63,rec=irec+6) theta_b
      read(63,rec=irec+7) theta_f
      irec=irec+7
      allocate(ztot(nvrt),sigma(nvrt),cs(nvrt),ztmp(nvrt),stat=istat)
      if(istat/=0) stop 'Falied to allocate (2)'

      do k=1,kz-1
        read(63,rec=irec+k) ztot(k)
      enddo
      do k=kz,nvrt
        kin=k-kz+1
        read(63,rec=irec+k) sigma(kin)
        cs(kin)=(1-theta_b)*sinh(theta_f*sigma(kin))/sinh(theta_f)+ &
     &theta_b*(tanh(theta_f*(sigma(kin)+0.5))-tanh(theta_f*0.5))/2/tanh(theta_f*0.5)
      enddo
      irec=irec+nvrt

!     Horizontal grid
      read(63,rec=irec+1) np
      read(63,rec=irec+2) ne
      irec=irec+2
      allocate(x(np),y(np),dp(np),kbp00(np),kfp(np),nm(ne,4),out(np,3,nvrt,2), &
     &out2(np,nvrt,2),icum(np,nvrt,2),eta2(np),node3(np,3),arco(np,3), &
     &iep(np),out3(np,2),stat=istat)
      if(istat/=0) stop 'Falied to allocate (3)'

      do m=1,np
        read(63,rec=irec+1)x(m)
        read(63,rec=irec+2)y(m)
        read(63,rec=irec+3)dp(m)
        read(63,rec=irec+4)kbp00(m)
        irec=irec+4
      enddo !m=1,np
      do m=1,ne
        read(63,rec=irec+1)i34
        irec=irec+1
        do mm=1,i34
          read(63,rec=irec+1)nm(m,mm)
          irec=irec+1
        enddo !mm
      enddo !m
      irec0=irec

      print*, 'last element',(nm(ne,j),j=1,3)

!...  Find parent element for (x00,y00)
      iep=0
      do i=1,ne
        do l=1,nxy
          aa=0
          ar=0 !area
          do j=1,3
            j1=j+1
            j2=j+2
            if(j1>3) j1=j1-3
            if(j2>3) j2=j2-3
            n0=nm(i,j)
            n1=nm(i,j1)
            n2=nm(i,j2)
            swild(j)=signa(x(n1),x(n2),x00(l),y(n1),y(n2),y00(l)) !temporary storage
            aa=aa+abs(swild(j))
            if(j==1) ar=signa(x(n1),x(n2),x(n0),y(n1),y(n2),y(n0))
          enddo !j
          if(ar<=0) then
            print*, 'Negative area:',ar
            stop
          endif
          ae=abs(aa-ar)/ar
          if(ae<=1.e-5) then
            iep(l)=i
            node3(l,1:3)=nm(i,1:3)
            arco(l,1:3)=swild(1:3)/ar
            arco(l,1)=max(0.,min(1.,arco(l,1)))
            arco(l,2)=max(0.,min(1.,arco(l,2)))
            if(arco(l,1)+arco(l,2)>1) then 
              arco(l,3)=0
              arco(l,2)=1-arco(l,1)
            else
              arco(l,3)=1-arco(l,1)-arco(l,2)
            endif
            cycle
          endif
        enddo !l; build pts

        ifl=0 !flag
        do l=1,nxy
          if(iep(l)==0) then
            ifl=1
            exit
          endif
        enddo !l
        if(ifl==0) exit
      enddo !i=1,ne

      do j=1,nxy
        if(iep(j)==0) then
          print*, 'Cannot find a parent for pt:',j,x00(j),y00(j)
          stop
        endif
      enddo !j

!...  Compute relative record # for a node and level for 3D outputs
!...
      icount=0
      do i=1,np
        do k=max0(1,kbp00(i)),nvrt
          do m=1,ivs
            icount=icount+1
            icum(i,k,m)=icount
          enddo !m
        enddo !k
      enddo !i=1,np

!...  Time iteration
!...
      it_tot=(iday1-1)*nrec
      do iday=iday1,iday2
!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      write(it_char,'(i12)')iday
      open(63,file=it_char//'_'//file63,status='old',access='direct',recl=nbyte)

      irec=irec0
      do it1=1,nrec
        read(63,rec=irec+1) time
        read(63,rec=irec+2) it
        irec=irec+2
        it_tot=it_tot+1
        time=it_tot*dtout

!        print*, 'time=',time/86400

        do i=1,nxy
          do j=1,3
            nd=node3(i,j)
            read(63,rec=irec+nd) eta2(nd)
          enddo !j
        enddo !i
!        do i=1,np
!          read(63,rec=irec+i) eta2(i)
!        enddo !i
        irec=irec+np

        out2=0
        out3=0
        if(i23d.eq.2) then
          do i=1,nxy
            do j=1,3 !nodes
              nd=node3(i,j)
              do m=1,ivs
                read(63,rec=irec+(nd-1)*ivs+m) tmp
                out2(i,1,m)=out2(i,1,m)+arco(i,j)*tmp
              enddo !m
            enddo !j
          enddo !i
          irec=irec+np*ivs
          !write(18,'(e16.8,6000(1x,e14.6))')time/86400+corieday,(out2(i,1,1),i=1,nxy)
          !if(ivs==2) write(19,'(e16.8,6000(1x,e14.6))')time/86400+corieday,(out2(i,1,2),i=1,nxy)
          if(it1==nrec.and.iday==iday2) then
            do i=1,nxy
              write(18,*)real(x00(i)),real(out2(i,1,1))
            enddo !i
          endif
        else !i23d=3 
          do i=1,nxy
            do j=1,3 !nodes
              nd=node3(i,j)
              do k=max0(1,kbp00(nd)),nvrt
                do m=1,ivs
                  read(63,rec=irec+icum(nd,k,m)) out(i,j,k,m)
                enddo !m
              enddo !k
            enddo !j
          enddo !i
          irec=irec+icum(np,nvrt,ivs)

!         Do interpolation
          do i=1,nxy
            etal=0; dep=0; idry=0
            do j=1,3
              nd=node3(i,j)
              if(eta2(nd)+dp(nd)<h0) idry=1
              etal=etal+arco(i,j)*eta2(nd)
              dep=dep+arco(i,j)*dp(nd)
      
!             Debug
!              write(11,*)i,j,nd,dp(nd),arco(i,j)

            enddo !j
            if(idry==1) then
              if(file63(1:7).eq.'hvel.64') then
                out2(i,0:nvrt,1:2)=0
              else
                out2(i,0:nvrt,1:2)=-99
              endif
!              write(65,*)'Dry'
            else !element wet
!             Compute z-coordinates
              do k=kz,nvrt
                kin=k-kz+1
                hmod2=min(dep,h_s)
                if(hmod2<=h_c) then
                  ztmp(k)=sigma(kin)*(hmod2+etal)+etal
                else if(etal<=-h_c-(hmod2-h_c)*theta_f/sinh(theta_f)) then
                  write(*,*)'Pls choose a larger h_c (2):',etal,h_c
                  stop
                else
                  ztmp(k)=etal*(1+sigma(kin))+h_c*sigma(kin)+(hmod2-h_c)*cs(kin)
                endif

!               Following to prevent underflow
                if(k==kz) ztmp(k)=-hmod2
                if(k==nvrt) ztmp(k)=etal
              enddo !k

              if(dep<=h_s) then
                kbpl=kz
              else !z levels
!               Find bottom index
                kbpl=0
                do k=1,kz-1
                  if(-dep>=ztot(k).and.-dep<ztot(k+1)) then
                    kbpl=k
                    exit
                  endif
                enddo !k
                if(kbpl==0) then
                  write(*,*)'Cannot find a bottom level:',dep,i
                  stop
                endif
                ztmp(kbpl)=-dep
                do k=kbpl+1,kz-1
                  ztmp(k)=ztot(k)
                enddo !k
              endif

              do k=kbpl+1,nvrt
                if(ztmp(k)-ztmp(k-1)<=0) then
                  write(*,*)'Inverted z-level:',etal,dep,ztmp(k)-ztmp(k-1)
                  stop
                endif
              enddo !k
       
              do k=kbpl,nvrt
                do m=1,ivs
                  do j=1,3
                    nd=node3(i,j)
                    kin=max(k,kbp00(nd))
                    out2(i,k,m)=out2(i,k,m)+arco(i,j)*out(i,j,kin,m)
                  enddo !j
                enddo !m
!                write(65,*)i,k,ztmp(k),(out2(i,k,m),m=1,ivs)     
              enddo !k

!             Interplate in vertical
              k0=0
              do k=kbpl,nvrt-1
                if(ztmp(nvrt)-z00(i)>=ztmp(k).and.ztmp(nvrt)-z00(i)<=ztmp(k+1)) then
                  k0=k
                  rat=(ztmp(nvrt)-z00(i)-ztmp(k))/(ztmp(k+1)-ztmp(k))
                  exit
                endif
              enddo !k
              if(k0==0) then
!                write(12,*)'Warning: failed to find a vertical level:',it,i
              else
                do m=1,ivs
                  out3(i,m)=out2(i,k0,m)*(1-rat)+out2(i,k0+1,m)*rat
                enddo !m
              endif
            endif !dry/wet
          enddo !i=1,nxy
          !write(18,'(e16.8,6000(1x,f12.3))')time/86400+corieday,(out3(i,1),i=1,nxy)
          !if(ivs==2) write(19,'(e16.8,6000(1x,f12.3))')time/86400+corieday,(out3(i,2),i=1,nxy)
         
        endif !i23d
      enddo !it1=1,nrec

!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      enddo !iday

      stop
      end

      function signa(x1,x2,x3,y1,y2,y3)
!...  Compute signed area formed by pts 1,2,3

      signa=((x1-x3)*(y2-y3)-(x2-x3)*(y1-y3))/2

      return
      end

