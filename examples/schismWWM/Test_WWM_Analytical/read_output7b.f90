!
!****************************************************************************************
!											*
!	read_output7 but compute vertical column at a given point (x,y) (for 2D, 	*
!	1 level only).									*
!											*
!       ifort -Bstatic -O3 -assume byterecl -o read_output7b read_output7b.f90
!****************************************************************************************
!
      program read_out
      parameter(nbyte=4)
      !parameter(mnp=80000)
      !parameter(mne=160000)
      !parameter(mnv=101)
      character*30 file63
      character*12 it_char
      character*48 start_time,version,variable_nm,variable_dim
      character*48 data_format
      !dimension sigma(mnv),cs(mnv),ztot(mnv),x(mnp),y(mnp),dp(mnp),kbp00(mnp),kfp(mnp)
      !dimension nm(mne,4),out(3,mnv,2),out2(mnv,2),icum(mnp,mnv,2),eta2(mnp),node3(3),arco(3)
      !dimension ztmp(mnv)
      allocatable :: sigma(:),cs(:),ztot(:),x(:),y(:),dp(:),kbp00(:),kfp(:)
      allocatable :: nm(:,:),out(:,:,:),out2(:,:),icum(:,:,:),eta2(:),ztmp(:)
      dimension node3(3),arco(3)
      
      print*, 'Input file to read from (without *_):'
      read(*,'(a30)')file63
      
      print*, 'Input # of files to read:'
      read(*,*) ndays

      print*, 'Input (x,y):'
      read(*,*) x00,y00

      print*, 'Input starting day offset:'
      read(*,*) corieday

      open(65,file='extract.out')
      !write(65,*)'(x,y)= ',x00,y00
      
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
      !if(nvrt.gt.mnv) then
      !  write(*,*)'Too many vertical levels',nvrt
      !  stop
      !endif
      allocate(ztot(nvrt),sigma(nvrt),cs(nvrt),out(3,nvrt,2),out2(nvrt,2),ztmp(nvrt),stat=istat)
      if(istat/=0) stop 'Falied to allocate (1)'

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
!      if(np.gt.mnp.or.ne.gt.mne) then
!        write(*,*)'Too many nodes/elements',np,ne
!        stop
!      endif
      allocate(x(np),y(np),dp(np),kbp00(np),kfp(np),nm(ne,4),icum(np,nvrt,2),eta2(np),stat=istat)
      if(istat/=0) stop 'Falied to allocate (2)'

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
      iel00=0
      do i=1,ne
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
          out(j,1,1)=signa(x(n1),x(n2),x00,y(n1),y(n2),y00) !temporary storage
          aa=aa+abs(out(j,1,1))
          if(j==1) ar=signa(x(n1),x(n2),x(n0),y(n1),y(n2),y(n0))
        enddo !j
        if(ar<=0) then
          print*, 'Negative area:',ar
          stop
        endif
        ae=abs(aa-ar)/ar
        if(ae<=1.e-5) then
          iel00=i
          node3(1:3)=nm(i,1:3)
          arco(1:3)=out(1:3,1,1)/ar
          arco(1)=max(0.,min(1.,arco(1)))
          arco(2)=max(0.,min(1.,arco(2)))
          if(arco(1)+arco(2)>1) then 
            arco(3)=0
            arco(2)=1-arco(1)
          else
            arco(3)=1-arco(1)-arco(2)
          endif
          exit
        endif
      enddo !i
      if(iel00==0) then
        print*, 'Cannot find a parent:',x00,y00
        stop
      endif

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
      it_tot=0
      do iday=1,ndays
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

        !print*, 'time=',time/86400

        do j=1,3
          nd=node3(j)
          read(63,rec=irec+nd) eta2(nd)
        enddo !j
!        do i=1,np
!          read(63,rec=irec+i) eta2(i)
!        enddo !i
        irec=irec+np

        out2=0
        if(i23d.eq.2) then
          do j=1,3 !nodes
            nd=node3(j)
            do m=1,ivs
              read(63,rec=irec+(nd-1)*ivs+m) tmp
              out2(1,m)=out2(1,m)+arco(j)*tmp
            enddo !m
          enddo !j
          irec=irec+np*ivs
          write(65,*)time/86400+corieday,(out2(1,m),m=1,ivs)
        else !i23d=3 
          write(65,*)time
          do j=1,3 !nodes
            nd=node3(j)
            do k=max0(1,kbp00(nd)),nvrt
              do m=1,ivs
                read(63,rec=irec+icum(nd,k,m)) out(j,k,m)
              enddo !m
            enddo !k
          enddo !j
          irec=irec+icum(np,nvrt,ivs)

!         Do interpolation
          etal=0; dep=0; idry=0
          do j=1,3
            nd=node3(j)
            if(eta2(nd)+dp(nd)<h0) idry=1
            etal=etal+arco(j)*eta2(nd)
            dep=dep+arco(j)*dp(nd)
          enddo !j
          if(idry==1) then
            if(file63(1:7).eq.'hvel.64') then
              out2=0
            else
              out2=-99
            endif
            write(65,*)'Dry'
          else !element wet
!           Compute z-coordinates
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

!             Following to prevent underflow
              if(k==kz) ztmp(k)=-hmod2
              if(k==nvrt) ztmp(k)=etal
            enddo !k

            if(dep<=h_s) then
              kbpl=kz
            else !z levels
!             Find bottom index
              kbpl=0
              do k=1,kz-1
                if(-dep>=ztot(k).and.-dep<ztot(k+1)) then
                  kbpl=k
                  exit
                endif
              enddo !k
              if(kbpl==0) then
                write(*,*)'Cannot find a bottom level:',dep
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
                  nd=node3(j)
                  kin=max(k,kbp00(nd))
                  out2(k,m)=out2(k,m)+arco(j)*out(j,kin,m)
                enddo !j
              enddo !m
              write(65,*)k,ztmp(k),(out2(k,m),m=1,ivs)     
            enddo !k
          
          endif !dry/wet
        endif !i23d
      enddo !it1=1,nrec

!+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      enddo !iday=1,ndays

      stop
      end

      function signa(x1,x2,x3,y1,y2,y3)
!...  Compute signed area formed by pts 1,2,3

      signa=((x1-x3)*(y2-y3)-(x2-x3)*(y1-y3))/2

      return
      end

