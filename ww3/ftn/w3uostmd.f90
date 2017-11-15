MODULE W3UOSTMD

! SOURCE TERM UNRESOLVED OBSTACLES MODULE
! MENTASCHI 2015
! THIS MODULE DOES NOT DEPEND FROM OTHER MODULES TO IMPROVE ITS PORTABILITY

!!!!!!!!!!!!!!
! WARNING! 
! I developed this module in an object oriented way, because oo programming is
! the standard of any advanced language.
! MY MISTAKE
! - object oriented in fortran is clumpsy
! - nobody in fortran community is used to oo programming
! - nothing supports it, the debugger crashes when I attempt to debug my
! classes. And even worse ....
! - MPI DOES NOT SUPPORT OBJECTS
!
! THEREFORE
! future effort is required to reformulate the implemetation of this module in
! terms of old fashioned arrays and functions.
!!!!!!!!!!!!!!


IMPLICIT NONE



! Source term representation of unresolved obstacles/dissipation
  
  PRIVATE
  
  
  
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!  PUBLIC SUBROUTINES CALLED FROM THE MODEL !!!!!!!!!!!!!!!!!!
  ! UOST_INITIALIZE: initializes the module
  PUBLIC :: UOST_INITIALIZE
  ! UOST_FINALIZE: finalizes the module (ww3 does not finalize)
  PUBLIC :: UOST_FINALIZE
  ! UOST_INITGRID: called for each grid. initializes each grid of the model
  PUBLIC :: UOST_INITGRID
  ! UOST_LOAD: called for each grid. loads each grid from file
  !   for each grid there are two files:
  !   obstructions_local.<gridname>.in and obstructions_shadow.<gridname>.in
  !   The two files have the same structure
  PUBLIC :: UOST_LOAD
  ! UOST_SETGRID: sets the grid which is actually elaborated by the model
  PUBLIC :: UOST_SETGRID
  ! UOST_SRCTRMCOMPUTE: estimates the source term for a given cell
  PUBLIC :: UOST_SRCTRMCOMPUTE
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


  INTEGER, PARAMETER :: GRIDNAME_LEN = 10
  REAL, PARAMETER :: TOLERANCE = 0.000001
  REAL, PARAMETER :: PI = 3.1415927
  
  
  
  
  
  ! Class lon_lat_spectralgrid represents the grid of alpha and beta (local or shadow) for
  ! a given cell
  TYPE LON_LAT_SPECTRALGRID
    LOGICAL :: INITIALIZED = .FALSE.
    INTEGER :: ILON, ILAT
    ! alpha, beta by frequency/direction.
    ! To save memory alpha and beta are represented as 1 byte integers
    INTEGER*1, ALLOCATABLE :: ALPHA(:,:), BETA(:,:)
    ! cellsize: array containing the sizes of the cell (or of the upstream cell) for each direction in km.
    REAL*4, ALLOCATABLE :: CELLSIZE(:)
    REAL :: FACTOR = 100
    REAL :: CELLSIZEFACTOR = 1000
    CONTAINS
      PROCEDURE, PASS :: INIT => LON_LAT_SPECTRALGRID_INIT
      PROCEDURE, PASS :: FINALIZE => LON_LAT_SPECTRALGRID_FINALIZE
      PROCEDURE, PASS :: GETALPHABETA => LON_LAT_SPECTRALGRID_GETALPHABETA
  END TYPE LON_LAT_SPECTRALGRID
    
  TYPE LON_LAT_SPECTRALGRID_POINTER
    CLASS(LON_LAT_SPECTRALGRID), POINTER :: P
  END TYPE LON_LAT_SPECTRALGRID_POINTER
  
  
  
  
  ! Class griddata contains the unresolved obstacles data for a given grid
  TYPE GRIDDATA
    CHARACTER(GRIDNAME_LEN) :: GRIDNAME
    ! enabled: the source term returns a non 0 term only for enabled grids
    LOGICAL :: ENABLED = .TRUE.
    INTEGER :: NX, NY, NTH, NK, NSPEC
    REAL, ALLOCATABLE :: TH(:)
    ! LON_LAT_SPECTRALGRIDS is a "list" of local dissipation lon_lat_spectralgrid, 
    ! one for each of the obstructed cells
    CLASS(LON_LAT_SPECTRALGRID), ALLOCATABLE :: LON_LAT_SPECTRALGRIDS(:)
    ! LON_LAT_SPECTRALGRID_MAP: spatial grid of LON_LAT_SPECTRALGRIDS for local dissipation.
    ! To save memory it is a matrix of pointers. 
    ! For obstructed cells the pointer points to an existing LON_LAT_SPECTRALGRID,
    ! otherwise it points to NULL
    CLASS(LON_LAT_SPECTRALGRID_POINTER), ALLOCATABLE :: LON_LAT_SPECTRALGRID_MAP(:,:)
    ! LON_LAT_SPECTRALGRIDS_SHADOW is a "list" of shadow effect lon_lat_spectralgrid, 
    ! one for each cell with some obstructed neighbour
    CLASS(LON_LAT_SPECTRALGRID), ALLOCATABLE :: LON_LAT_SPECTRALGRIDS_SHADOW(:)
    ! LON_LAT_SPECTRALGRID_SHADOW_MAP: spatial grid of LON_LAT_SPECTRALGRIDS for the shadow.
    ! To save memory it is a matrix of pointers. 
    ! For cells with obstructed neighbours the pointer points to an existing LON_LAT_SPECTRALGRID,
    ! otherwise it points to NULL
    CLASS(LON_LAT_SPECTRALGRID_POINTER), ALLOCATABLE :: LON_LAT_SPECTRALGRID_SHADOW_MAP(:,:)
    CONTAINS
      PROCEDURE, PASS :: INIT => GRID_INITIALIZE
      PROCEDURE, PASS :: FINALIZE => GRID_FINALIZE
      PROCEDURE, PASS :: LOAD => GRID_LOAD
      PROCEDURE, PASS :: FINALIZE_LON_LAT_SPECTRALGRIDS => GRID_FINALIZE_LON_LAT_SPECTRALGRIDS
  END TYPE GRIDDATA
  
  
  
  
  
  ! Class sourceterm represents the source term
  TYPE SOURCETERM
    REAL, ALLOCATABLE :: COSTH(:), SINTH(:)
    REAL :: GAMMAUP = 10
    REAL :: GAMMADOWN = 20
    ! griddata is a pointer to the grid actually computed
    CLASS(GRIDDATA), POINTER :: GRD
    CONTAINS
      !PROCEDURE, PASS, PRIVATE :: COMPUTE_PSI => SOURCETERM_COMPUTE_PSI

      !compute_ld: estimates the local dissipation (private method)
      PROCEDURE, PASS, PRIVATE :: COMPUTE_LD => SOURCETERM_COMPUTE_LD
      !compute_se: estimates the shadow effect (private method)
      PROCEDURE, PASS, PRIVATE :: COMPUTE_SE => SOURCETERM_COMPUTE_SE
      !compute: estimates the whole dissipation
      PROCEDURE, PASS :: COMPUTE => SOURCETERM_COMPUTE
      !setgrid: sets grd pointer and computes some cached structures
      PROCEDURE, PASS :: SETGRID => SOURCETERM_SETGRID
  END TYPE SOURCETERM
  
  
  
  
  
  ! actualgrid: global pointer pointing to the grid actually elaborated. Set by UOST_SETGRID
  CLASS(GRIDDATA), POINTER :: ACTUALGRID
  ! griddatas: list containing all the instances of griddata
  CLASS(GRIDDATA), TARGET, ALLOCATABLE :: GRIDDATAS(:)
  ! srctrm: global singleton source term
  CLASS(SOURCETERM), ALLOCATABLE :: SRCTRM




  CONTAINS

  
  
  
  !ALLOCATES ALL ALPHAX AND ALPHAY
  SUBROUTINE GRID_INITIALIZE(THIS, GRIDNAME, NX, NY, NK, NTH, TH)
    INTEGER, INTENT(IN) :: NX, NY, NK, NTH    
    REAL, INTENT(IN) :: TH(:)
    CHARACTER(GRIDNAME_LEN), INTENT(IN) :: GRIDNAME
    CLASS(GRIDDATA), INTENT(INOUT) :: THIS
    
    THIS%GRIDNAME = GRIDNAME
    THIS%NX = NX
    THIS%NY = NY
    THIS%NK = NK
    THIS%NTH = NTH
    THIS%NSPEC = NK*NTH
    ALLOCATE(THIS%TH(NTH))
  END SUBROUTINE GRID_INITIALIZE
  
  
  
  
  SUBROUTINE GRID_FINALIZE(THIS)
    CLASS(GRIDDATA), INTENT(INOUT) :: THIS  
    DEALLOCATE(THIS%TH)
    CALL THIS%FINALIZE_LON_LAT_SPECTRALGRIDS()
  END SUBROUTINE GRID_FINALIZE
  
  
  
  
  SUBROUTINE GRID_FINALIZE_LON_LAT_SPECTRALGRIDS(THIS)
    CLASS(GRIDDATA), INTENT(INOUT) :: THIS  
    INTEGER :: I
    
    IF (.NOT. ALLOCATED(THIS%LON_LAT_SPECTRALGRIDS)) RETURN
    
    DO I=1,SIZE(THIS%LON_LAT_SPECTRALGRIDS) 
      CALL THIS%LON_LAT_SPECTRALGRIDS(I)%FINALIZE()
    ENDDO

    DEALLOCATE(THIS%LON_LAT_SPECTRALGRIDS)
    DEALLOCATE(THIS%LON_LAT_SPECTRALGRID_MAP)
  END SUBROUTINE GRID_FINALIZE_LON_LAT_SPECTRALGRIDS
  
  
  
  
  
  SUBROUTINE GRID_LOAD(THIS, FILEUNIT)
    INTEGER, INTENT(IN) :: FILEUNIT
    CLASS(GRIDDATA), INTENT(INOUT), TARGET :: THIS
    CHARACTER(50) :: FILENAME
    LOGICAL :: FILEEXISTS
    INTEGER :: JG, J, L, I, ILON, ILAT
    CLASS(LON_LAT_SPECTRALGRID), POINTER :: SPGRD
    
    JG = LEN_TRIM(THIS%GRIDNAME)
    FILENAME = 'obstructions_local.'//THIS%GRIDNAME(:JG)//'.in'
    INQUIRE(FILE=FILENAME, EXIST=FILEEXISTS)
    
    J = LEN_TRIM(FILENAME)
    IF (.NOT. FILEEXISTS) THEN
      WRITE(*,*)'FILE '//FILENAME(:J)//' NOT FOUND. USING GRIDGEN SETTING'
      THIS%ENABLED = .FALSE.
      CALL EXIT
    ENDIF  
    WRITE(*,*)'FILE '//FILENAME(:J)//' FOUND. LOADING ADVANCED OBSTRUCTION SETTINGS FOR GRID '//THIS%GRIDNAME

    ! LOADING LOCAL ALPHA/BETA
    CALL LON_LAT_SPECTRALGRID_LOADGRIDSFROMFILE(THIS%LON_LAT_SPECTRALGRIDS,&
      FILEUNIT, FILENAME(:J), THIS%NK, THIS%NTH)

    IF (ALLOCATED(THIS%LON_LAT_SPECTRALGRID_MAP)) DEALLOCATE(THIS%LON_LAT_SPECTRALGRID_MAP) 
    ALLOCATE(THIS%LON_LAT_SPECTRALGRID_MAP(THIS%NX, THIS%NY))

    DO I=1,THIS%NX
      DO J=1,THIS%NY
        THIS%LON_LAT_SPECTRALGRID_MAP(I, J)%P => NULL()
      ENDDO
    ENDDO
    
    L = SIZE(THIS%LON_LAT_SPECTRALGRIDS)
    DO I=1,L
      SPGRD => THIS%LON_LAT_SPECTRALGRIDS(I)
      ILON = SPGRD%ILON
      ILAT = SPGRD%ILAT
      THIS%LON_LAT_SPECTRALGRID_MAP(ILON, ILAT)%P => SPGRD 
    ENDDO

    ! LOADING SHADOW ALPHA/BETA
    FILENAME = 'obstructions_shadow.'//THIS%GRIDNAME(:JG)//'.in'
    J = LEN_TRIM(FILENAME)
    CALL LON_LAT_SPECTRALGRID_LOADGRIDSFROMFILE(THIS%LON_LAT_SPECTRALGRIDS_SHADOW,&
      FILEUNIT, FILENAME(:J), THIS%NK, THIS%NTH)

    IF (ALLOCATED(THIS%LON_LAT_SPECTRALGRID_SHADOW_MAP)) DEALLOCATE(THIS%LON_LAT_SPECTRALGRID_SHADOW_MAP) 
    ALLOCATE(THIS%LON_LAT_SPECTRALGRID_SHADOW_MAP(THIS%NX, THIS%NY))

    DO I=1,THIS%NX
      DO J=1,THIS%NY
        THIS%LON_LAT_SPECTRALGRID_SHADOW_MAP(I, J)%P => NULL()
      ENDDO
    ENDDO
    
    L = SIZE(THIS%LON_LAT_SPECTRALGRIDS_SHADOW)
    DO I=1,L
      SPGRD => THIS%LON_LAT_SPECTRALGRIDS_SHADOW(I)
      ILON = SPGRD%ILON
      ILAT = SPGRD%ILAT
      THIS%LON_LAT_SPECTRALGRID_SHADOW_MAP(ILON, ILAT)%P => SPGRD 
    ENDDO
  END SUBROUTINE GRID_LOAD
  
  
  
  
  
  
  SUBROUTINE LON_LAT_SPECTRALGRID_INIT(THIS, ILON, ILAT, NK, NTH)
    CLASS(LON_LAT_SPECTRALGRID), INTENT(INOUT) :: THIS
    INTEGER, INTENT(IN) :: ILON, ILAT, NK, NTH
    
    IF (THIS%INITIALIZED) RETURN
    THIS%ILON = ILON
    THIS%ILAT = ILAT
    ALLOCATE(THIS%ALPHA(NK,NTH))
    ALLOCATE(THIS%BETA(NK,NTH))
    ALLOCATE(THIS%CELLSIZE(NTH))
    THIS%INITIALIZED = .TRUE.
  END SUBROUTINE LON_LAT_SPECTRALGRID_INIT
  
  
  
  
  SUBROUTINE LON_LAT_SPECTRALGRID_FINALIZE(THIS)
    CLASS(LON_LAT_SPECTRALGRID), INTENT(INOUT) :: THIS
    
    DEALLOCATE(THIS%ALPHA)
    DEALLOCATE(THIS%BETA)
    DEALLOCATE(THIS%CELLSIZE)
  END SUBROUTINE LON_LAT_SPECTRALGRID_FINALIZE
  
  
  
  
  SUBROUTINE LON_LAT_SPECTRALGRID_LOADGRIDSFROMFILE(LON_LAT_SPECTRALGRIDS, FILEUNIT, FILENAME, NK, NTH)
    CLASS(LON_LAT_SPECTRALGRID), ALLOCATABLE, TARGET, INTENT(OUT) :: LON_LAT_SPECTRALGRIDS(:)
    CHARACTER(*), INTENT(IN) :: FILENAME
    INTEGER, INTENT(IN) :: FILEUNIT, NK, NTH
    CHARACTER(LEN=600) :: LINE
    INTEGER :: FIOSTAT
    LOGICAL :: HEADER, FILESTART, READINGCELLSIZE, READINGALPHA, STRUCT_ALLOCATED
    INTEGER :: ILON, ILAT, SPGRDS_SIZE, IGRD, IK
    REAL, ALLOCATABLE :: TRANS(:)
    CLASS(LON_LAT_SPECTRALGRID), POINTER :: SPGRD
    
    FILESTART = .TRUE.
    HEADER = .TRUE.;
    IGRD = 0
    IK = 0
    READINGCELLSIZE = .FALSE.
    READINGALPHA = .FALSE.
    
    ALLOCATE(TRANS(NTH))
    
    OPEN(FILEUNIT, FILE=FILENAME, STATUS='OLD', ACTION='READ')
    READ_LOOP: DO
      READ(FILEUNIT, '(A)', IOSTAT=FIOSTAT) LINE

      IF (FIOSTAT .NE. 0) EXIT READ_LOOP
        
      IF (LINE(1:1) .EQ. '$') CYCLE
      
      IF (FILESTART) THEN
        READ(LINE, '(I5)') SPGRDS_SIZE
        STRUCT_ALLOCATED = ALLOCATED(LON_LAT_SPECTRALGRIDS)
        IF (.NOT. STRUCT_ALLOCATED) ALLOCATE(LON_LAT_SPECTRALGRIDS(SPGRDS_SIZE))
        FILESTART = .FALSE.
      ELSEIF (HEADER) THEN
        READ(LINE, '(2I4) '), ILON, ILAT
        IGRD = IGRD + 1
        SPGRD => LON_LAT_SPECTRALGRIDS(IGRD)
        CALL SPGRD%INIT(ILON, ILAT, NK, NTH)
        HEADER = .FALSE.
        IK = 1
        READINGCELLSIZE = .TRUE.
      ELSEIF (READINGCELLSIZE) THEN
        READ(LINE, *) SPGRD%CELLSIZE
        READINGCELLSIZE = .FALSE.
        READINGALPHA = .TRUE.
      ELSE        
        READ(LINE, *) TRANS
        IF (READINGALPHA) THEN
          SPGRD%ALPHA(IK, :) = NINT(TRANS*SPGRD%FACTOR)
        ELSE
          SPGRD%BETA(IK, :) = NINT(TRANS*SPGRD%FACTOR)
        ENDIF
        IF (IK .LT. NK) THEN
          IK = IK + 1
        ELSE IF (READINGALPHA) THEN
          READINGALPHA = .FALSE.
          IK = 1
        ELSE
          HEADER = .TRUE.
          IK = 1
        ENDIF
      ENDIF
    ENDDO READ_LOOP
    CLOSE(FILEUNIT)

    DEALLOCATE(TRANS)
    
  END SUBROUTINE LON_LAT_SPECTRALGRID_LOADGRIDSFROMFILE
  
  SUBROUTINE LON_LAT_SPECTRALGRID_GETALPHABETA(THIS, IK, ITH, ALPHA, BETA)
    CLASS(LON_LAT_SPECTRALGRID), INTENT(IN) :: THIS
    INTEGER, INTENT(IN) :: IK, ITH
    REAL, INTENT(OUT) :: ALPHA, BETA
    
    ALPHA = THIS%ALPHA(IK, ITH)/THIS%FACTOR
    BETA = THIS%BETA(IK, ITH)/THIS%FACTOR
  END SUBROUTINE LON_LAT_SPECTRALGRID_GETALPHABETA
  
  
  SUBROUTINE SOURCETERM_SETGRID(THIS, GRD)
    
    CLASS(SOURCETERM), INTENT(INOUT) :: THIS
    CLASS(GRIDDATA), TARGET, INTENT(IN) :: GRD
    INTEGER :: ITH, NTH
    
    THIS%GRD => GRD
    NTH = GRD%NTH
    
    IF (ALLOCATED(THIS%COSTH)) THEN
      DEALLOCATE(THIS%COSTH)
      DEALLOCATE(THIS%SINTH)
    ENDIF
    
    ALLOCATE(THIS%COSTH(NTH))
    ALLOCATE(THIS%SINTH(NTH))
    
    DO ITH=1,NTH
      THIS%COSTH(ITH) = COS(GRD%TH(ITH))
      THIS%SINTH(ITH) = SIN(GRD%TH(ITH))
    ENDDO
  END SUBROUTINE SOURCETERM_SETGRID 



! SUBROUTINE SOURCETERM_COMPUTE_PSI(THIS, U10ABS, U10DIR, CGABS, CGDIR, DT, PSI)
!   USE CONSTANTS, ONLY: PI

!   CLASS(SOURCETERM), INTENT(INOUT), TARGET :: THIS
!   REAL, INTENT(IN) :: U10ABS, U10DIR, CGABS, CGDIR, DT
!   REAL, INTENT(OUT) :: PSI
!   REAL, PARAMETER :: BETA = .000015
!   REAL :: THDELTA, CP, WA
!   
!   ! computing the wave age
!   THDELTA = ABS(U10DIR - CGDIR)
!   DO WHILE (THDELTA .GT. PI)
!     THDELTA = THDELTA - 2*PI
!   ENDDO 
!   THDELTA = ABS(THDELTA)
!   IF (PI/2 - THDELTA .GT. TOLERANCE) THEN
!     CP = CGABS/2 ! this is scrictly valid only in deep water
!     WA = CP/U10ABS/COS(THDELTA)
!   ELSE
!     WA = 9999999 ! a very high number
!   ENDIF

!   PSI = 1 + BETA/WA**2.*DT
! END SUBROUTINE SOURCETERM_COMPUTE_PSI



  SUBROUTINE SOURCETERM_COMPUTE_LD(THIS, IX, IY, SPEC, CG, DT, U10ABS, U10DIR, S)
    CLASS(SOURCETERM), INTENT(INOUT) :: THIS
    INTEGER, INTENT(IN) :: IX, IY
    REAL, INTENT(IN) :: SPEC(THIS%GRD%NSPEC), CG(THIS%GRD%nk)
    REAL, INTENT(OUT) :: S(THIS%GRD%NSPEC)
    REAL, INTENT(IN) :: U10ABS, U10DIR
    REAL, INTENT(IN) :: DT
    
    !TYPE(GRIDDATA) :: G
    CLASS(LON_LAT_SPECTRALGRID), POINTER :: SPGRID
    INTEGER :: IK, ITH, ISP, NK, NTH
    REAL :: ALPHA, BETA, CGI, CELLSIZE, SPECI, SFC
    LOGICAL :: CELLOBSTRUCTED
!    REAL :: PSI

    S = 0

    !G = THIS%GRID
    SPGRID => THIS%GRD%LON_LAT_SPECTRALGRID_MAP(IX, IY)%P
    CELLOBSTRUCTED = ASSOCIATED(THIS%GRD%LON_LAT_SPECTRALGRID_MAP(IX, IY)%P)
    IF (.NOT. CELLOBSTRUCTED) RETURN    

    NK = THIS%GRD%NK
    NTH = THIS%GRD%NTH
    
    DO IK = 1,NK
      !looping on the frequency
      CGI = CG(IK)
      DO ITH = 1,NTH
        !looping on the direction

        CALL SPGRID%GETALPHABETA(IK, ITH, ALPHA, BETA)
        
        IF (ALPHA .EQ. 1) CYCLE
        
        CELLSIZE = SPGRID%CELLSIZE(ITH)*SPGRID%CELLSIZEFACTOR

        ISP = ITH + (IK-1)*NTH
        SPECI = SPEC(ISP)
        
!#ifdef NO_ST4_LN1
!        PSI = 1
!#else
!        CALL THIS%COMPUTE_PSI(U10ABS, U10DIR, CG(IK), TH(ITH), DT, PSI)
!#endif

        IF (BETA > 0.09) THEN
          SFC = - CGI/CELLSIZE * (1 - BETA)/BETA
        ELSE
          SFC = - CGI/CELLSIZE * THIS%GAMMAUP
        ENDIF
        
!        S(ISP) = SFC * SPECI * PSI
        S(ISP) = SFC * SPECI
      ENDDO
    ENDDO
    
  END SUBROUTINE SOURCETERM_COMPUTE_LD



  SUBROUTINE SOURCETERM_COMPUTE_SE(THIS, IX, IY, SPEC, CG, DT, U10ABS, U10DIR, S)
    CLASS(SOURCETERM), INTENT(INOUT), TARGET :: THIS
    INTEGER, INTENT(IN) :: IX, IY
    REAL, INTENT(IN) :: SPEC(THIS%GRD%NSPEC), CG(THIS%GRD%NK)
    REAL, INTENT(OUT) :: S(THIS%GRD%NSPEC)
    REAL, INTENT(IN) :: U10ABS, U10DIR
    REAL, INTENT(IN) :: DT
    
    CLASS(LON_LAT_SPECTRALGRID), POINTER :: SPGRID
    INTEGER :: IK, ITH, IS
    REAL :: CGI, SPECI, SFC, CELLSIZE, &
            SFCLEFT, SFCRIGHT, SFCCENTER, THDIAG, CGDIAG, &
            ALPHASH, BETASH, GAMMMA, GG
    INTEGER :: N = 8, ITHDIAG, ISP, NK, NTH, NX, NY
    LOGICAL :: CELLOBSTRUCTED
!    REAL :: PSI
 
    S = 0

    NK = THIS%GRD%NK
    NTH = THIS%GRD%NTH
    NX = THIS%GRD%NX
    NY = THIS%GRD%NY
    
    IF ((IX .EQ. 1) .OR. (IX .EQ. NX) .OR. (IY .EQ. 1) .OR. (IY .EQ. NY)) RETURN

    CELLOBSTRUCTED = ASSOCIATED(THIS%GRD%LON_LAT_SPECTRALGRID_SHADOW_MAP(IX, IY)%P)
    IF (.NOT. CELLOBSTRUCTED) RETURN
    
    SPGRID => THIS%GRD%LON_LAT_SPECTRALGRID_SHADOW_MAP(IX, IY)%P 

    DO IK=1,NK
      !looping on the frequency
      DO ITH=1,NTH
        !looping on the direction

        CALL SPGRID%GETALPHABETA(IK, ITH, ALPHASH, BETASH)
 
        IF (ALPHASH .EQ. 1) CYCLE        
 
        CELLSIZE = SPGRID%CELLSIZE(ITH)*SPGRID%CELLSIZEFACTOR

        CGI = CG(IK)

        GG = CGI/CELLSIZE

        IF (ALPHASH > 0.2) THEN
          GAMMMA = BETASH/ALPHASH - 1
        ELSE
          GAMMMA = THIS%GAMMADOWN
        ENDIF
        
!#ifdef NO_ST4_LN1
!        PSI = 1
!#else
!        CALL THIS%COMPUTE_PSI(U10ABS, U10DIR, CG(IK), TH(ITH), DT, PSI)
!#endif
!        SFC = - GG*GAMMMA*PSI
        SFC = - GG*GAMMMA

        ISP = ITH + (IK-1)*NTH
        SPECI = SPEC(ISP)
        S(ISP) = SFC * SPECI
      ENDDO
    ENDDO  
  END SUBROUTINE SOURCETERM_COMPUTE_SE
  

  
  SUBROUTINE SOURCETERM_COMPUTE(THIS, IX, IY, SPEC, CG, DT, U10ABS, U10DIR, S)
    CLASS(SOURCETERM), INTENT(INOUT) :: THIS
    INTEGER, INTENT(IN) :: IX, IY
    REAL, INTENT(IN) :: SPEC(THIS%GRD%NSPEC), CG(THIS%GRD%NK)
    REAL, INTENT(IN) :: DT
    REAL, INTENT(IN) :: U10ABS, U10DIR
    REAL, INTENT(OUT) :: S(THIS%GRD%NSPEC)

    REAL :: S_UP(THIS%GRD%NSPEC)
    REAL :: S_DOWN(THIS%GRD%NSPEC)
    
    IF (.NOT. THIS%GRD%ENABLED) THEN
      S = 0
      RETURN
    ENDIF

    S_UP = 0
    S_DOWN = 0
    CALL THIS%COMPUTE_LD(IX, IY, SPEC, CG, DT, U10ABS, U10DIR, S_UP)
    CALL THIS%COMPUTE_SE(IX, IY, SPEC, CG, DT, U10ABS, U10DIR, S_DOWN)
    S = S_UP + S_DOWN
    !WHERE (S .GT. 0) S = 0
  END SUBROUTINE SOURCETERM_COMPUTE
  
  
  
  
  SUBROUTINE UOST_INITIALIZE(NGRID)
    ! PARAMETERS:
    !   NGRID: TOTAL NUMBER OF GRIDS
    INTEGER, INTENT(IN) :: NGRID
    
    WRITE(*,*) 'ADVANCED OBSTRUCTIONS: INITIALIZING GRID DATA'
    ALLOCATE(GRIDDATAS(NGRID))
    WRITE(*,*) 'ADVANCED OBSTRUCTIONS: SOURCE TERM CORRECTLY INITIALIZED'
    ALLOCATE(SRCTRM)
  END SUBROUTINE UOST_INITIALIZE
  
  
  
  
  SUBROUTINE UOST_INITGRID(IGRID, GRIDNAME, NX, NY, NK, NTH, TH)
    ! PARAMETERS:
    !   IGRID: grid index as element of the list GRIDDATAS
    !   NX: number of columns of the grid
    !   NY: number of rows of the grid (for an unstructured grid it should be NY=1)
    !   NK: number of frequencies of the spectrum
    !   NTH: number of directions of the spectrum
    !   TH: directions considered in the spectrum
    INTEGER, INTENT(IN) :: IGRID, NX, NY, NK, NTH
    REAL, INTENT(IN) :: TH(:)
    CHARACTER(10), INTENT(IN) :: GRIDNAME
    CLASS(GRIDDATA), POINTER :: GRD
    
    IF ( (IGRID .LE. 0) .OR. (.NOT. ALLOCATED(GRIDDATAS)) ) THEN
      RETURN
    ENDIF
    
    GRD => GRIDDATAS(IGRID)
    CALL GRD%INIT(GRIDNAME, NX, NY, NK, NTH, TH)
  END SUBROUTINE UOST_INITGRID

  
  
  
  
  
  
  SUBROUTINE UOST_FINALIZE
    INTEGER :: I, L
  
    L = SIZE(GRIDDATAS)  
    DO I = 1,L
      CALL GRIDDATAS(I)%FINALIZE()
    ENDDO
    DEALLOCATE(GRIDDATAS)
    DEALLOCATE(SRCTRM)
  END SUBROUTINE UOST_FINALIZE
  
  
  
  
  SUBROUTINE UOST_SETGRID(IGRID)
    ! PARAMETERS:
    !   IGRID: grid index as element of the list GRIDDATAS
    INTEGER, INTENT(IN) :: IGRID
    
    ACTUALGRID => GRIDDATAS(IGRID)
    !SRCTRMPTR%GRID => GRIDDATAS(IGRID)
    CALL SRCTRM%SETGRID(GRIDDATAS(IGRID))
  END SUBROUTINE UOST_SETGRID
  
  
  
  
  SUBROUTINE UOST_LOAD(IGRID)
    ! PARAMETERS:
    !   IGRID: grid index as element of the list GRIDDATAS
    INTEGER, INTENT(IN) :: IGRID
    IF ( (IGRID .LE. 0) .OR. (.NOT. ALLOCATED(GRIDDATAS)) ) RETURN
    
    CALL GRIDDATAS(IGRID)%LOAD(100)
    !CALL LON_LAT_SPECTRALGRID_LOADGRIDSFROMFILE()
  END SUBROUTINE UOST_LOAD
  
  
  
  
  SUBROUTINE UOST_SRCTRMCOMPUTE(IX, IY, SPEC, CG, DT, U10ABS, U10DIR, S)
    ! PARAMETERS:
    !   IX, IY: coord indexes of the actual geographical cell (in unstructured grids IY=1)
    !   SPEC: spectrum to which the term will be applied
    !   CG: group velocity (array indexed as the frequency)
    !   DT: time step (for possible active generation adjustment, actually turned off)
    !   U10ABS, U10DIR: 10 m wind (for possible active generation adjustment, actually turned off)
    !   S: output source term
    INTEGER, INTENT(IN) :: IX, IY
    REAL, INTENT(IN) :: DT
    REAL, INTENT(IN) :: SPEC(SRCTRM%GRD%NSPEC), CG(SRCTRM%GRD%NK)
    REAL, INTENT(IN) :: U10ABS, U10DIR
    REAL, INTENT(OUT) :: S(SRCTRM%GRD%NSPEC)

    CALL SRCTRM%COMPUTE(IX, IY, SPEC, CG, DT, U10ABS, U10DIR, S)
  END SUBROUTINE UOST_SRCTRMCOMPUTE
  
  
  
  
END MODULE W3UOSTMD  
  
