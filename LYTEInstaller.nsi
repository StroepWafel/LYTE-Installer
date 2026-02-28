!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "nsDialogs.nsh"
!include "WinMessages.nsh"

;--------------------------------
; General Settings
;--------------------------------
Name "LYTE"
OutFile "LYTE_Installer.exe"
InstallDir "$PROGRAMFILES64\LYTE"
InstallDirRegKey HKLM "Software\LYTE" "Install_Dir"
RequestExecutionLevel admin
Unicode True

;--------------------------------
; Modern UI Settings
;--------------------------------
!define MUI_ICON "branding\ico\install.ico"
!define MUI_UNICON "branding\ico\uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "branding\headerimage.bmp"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
; Wizard bitmap for welcome/finish pages
; Requirements: 164x314 pixels (or close), 24-bit BMP format (RGB, no alpha channel)
; IMPORTANT: MUI2 requires 24-bit RGB format. If your image appears white/blank, convert it to 24-bit RGB.
!define MUI_WELCOMEFINISHPAGE_BITMAP "branding\wizard.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "branding\wizard.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP_NOSTRETCH

; Modern UI 2 Configuration
; Note: MUI2 doesn't support MUI_BGCOLOR or MUI_TEXTCOLOR defines
; Colors are controlled by the bitmap images and Windows theme
!define MUI_INSTFILESPAGE_PROGRESSBAR "smooth"
!define MUI_INSTFILESPAGE_PROGRESSBAR_COLOR "#0078D4"

; Modern UI 2 Branding
!define MUI_WELCOMEPAGE_TITLE "Welcome to LYTE Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of LYTE.$\r$\n$\r$\nClick Next to continue."
!define MUI_FINISHPAGE_TITLE "Installation Complete"
!define MUI_FINISHPAGE_TEXT "LYTE has been successfully installed on your computer.$\r$\n$\r$\nClick Finish to exit the setup wizard."

;--------------------------------
; Variables for config options
;--------------------------------
Var AddStartMenu
Var AddDesktop
Var InstallPython
Var InstallVLC
Var InstallVCRedist
Var ComponentsPageDialog
Var PythonCheckbox
Var VLCCheckbox
Var VCRedistCheckbox
Var ComponentsLabel
Var VersionDropdown
Var SelectedVersion
Var VersionPageDialog
Var ShortcutsPageDialog
Var ShortcutsLabel

; Variables for modern UI fonts
Var ModernFont
Var ModernFontBold
Var ModernFontTitle

; Variables for uninstall
Var RemoveSettings

;--------------------------------
; Pages
;--------------------------------
!define MUI_PAGE_CUSTOMFUNCTION_SHOW .onWelcomePage
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
Page custom VersionPageCreate VersionPageLeave
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE DirectoryPageLeave
!insertmacro MUI_PAGE_DIRECTORY
Page custom ComponentsPageCreate ComponentsPageLeave
Page custom ShortcutsPageCreate ShortcutsPageLeave
!define MUI_INSTFILESPAGE_SHOW_DETAILS
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\LYTE.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch LYTE"
!define MUI_FINISHPAGE_RUN_PARAMETERS ""
!define MUI_FINISHPAGE_SHOWREADME ""
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages
;--------------------------------
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Modern UI Font Initialization
;--------------------------------
Function .onInit
  ; Create modern fonts for custom pages
  CreateFont $ModernFont "Segoe UI" "9" "400"
  CreateFont $ModernFontBold "Segoe UI" "9" "700"
  CreateFont $ModernFontTitle "Segoe UI" "12" "700"
FunctionEnd

;--------------------------------
; Welcome Page Enhancement
;--------------------------------
Function .onWelcomePage
  ; Set welcome page text colors for better visibility
  FindWindow $0 "#32770" "" $HWNDPARENT
  ${If} $0 <> 0
    ; Get the title control (ID 1037)
    GetDlgItem $1 $0 1037
    ${If} $1 <> 0
      SendMessage $1 ${WM_SETFONT} $ModernFontTitle 0
      SetCtlColors $1 0x1A1A1A transparent
    ${EndIf}
    ; Get the text control (ID 1036)
    GetDlgItem $1 $0 1036
    ${If} $1 <> 0
      SendMessage $1 ${WM_SETFONT} $ModernFont 0
      SetCtlColors $1 0x1A1A1A transparent
    ${EndIf}
  ${EndIf}
FunctionEnd

;--------------------------------
; Directory Page Functions
;--------------------------------

Function DirectoryPageLeave
  ; Validate install directory
  ${If} $INSTDIR == ""
    MessageBox MB_ICONEXCLAMATION "Please select an installation directory."
    Abort
  ${EndIf}
  
  ; Check if directory is writable
  GetTempFileName $0
  Delete $0
  FileOpen $0 "$INSTDIR\test.tmp" w
  ${If} $0 == ""
    CreateDirectory "$INSTDIR"
    IfFileExists "$INSTDIR\*.*" 0 dir_failed
      ; Directory exists
      Goto dir_done

      dir_failed:
        MessageBox MB_ICONSTOP "Cannot create directory $INSTDIR. Please choose a different location or run as administrator."
        Abort

      dir_done:
  ${EndIf}
  FileClose $0
  Delete "$INSTDIR\test.tmp"
FunctionEnd

;--------------------------------
; Version Page Functions
;--------------------------------

Function VersionPageCreate
  nsDialogs::Create 1018
  Pop $VersionPageDialog
  ${If} $VersionPageDialog == error
    Abort
  ${EndIf}

  ; Title label with modern styling
  ${NSD_CreateLabel} 0 20 100% 30 "Select LYTE Version"
  Pop $0
  SendMessage $0 ${WM_SETFONT} $ModernFontTitle 0
  SetCtlColors $0 0x1A1A1A transparent

  ; Description label
  ${NSD_CreateLabel} 0 55 100% 40 "Choose which LYTE release to download. The latest version is recommended for most users."
  Pop $0
  SendMessage $0 ${WM_SETFONT} $ModernFont 0
  SetCtlColors $0 0x666666 transparent

  ; Version dropdown with better spacing
  ${NSD_CreateDropList} 20 105 70% 20 ""
  Pop $VersionDropdown
  SendMessage $VersionDropdown ${WM_SETFONT} $ModernFont 0
  SetCtlColors $VersionDropdown 0x1A1A1A 0xFFFFFF
  
  ${NSD_CB_AddString} $VersionDropdown "latest (recommended)"
  ${NSD_CB_AddString} $VersionDropdown "1.11.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.10.1-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.10.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.9.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.8.3-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.8.2-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.8.1-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.8.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.7.2-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.7.1-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.6.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.5.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.4.1-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.4.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.3.2-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.3.1-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.3.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.2.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.0.2-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.0.1-Release"
  ${NSD_CB_AddString} $VersionDropdown "1.0.0-Release"
  ${NSD_CB_AddString} $VersionDropdown "release"
  ${NSD_CB_SelectString} $VersionDropdown "latest (recommended)"

  nsDialogs::Show
FunctionEnd

Function VersionPageLeave
  ; Capture selected LYTE version (default to latest)
  ${NSD_GetText} $VersionDropdown $SelectedVersion
  ${If} $SelectedVersion == ""
    StrCpy $SelectedVersion "latest"
  ${EndIf}
  ${If} $SelectedVersion == "latest (recommended)"
    StrCpy $SelectedVersion "latest"
  ${EndIf}
FunctionEnd

;--------------------------------
; Components Page Functions
;--------------------------------

Function ComponentsPageCreate
  nsDialogs::Create 1018
  Pop $ComponentsPageDialog
  ${If} $ComponentsPageDialog == error
    Abort
  ${EndIf}

  ; Page title with modern styling
  ${NSD_CreateLabel} 0 20 100% 30 "Select Components to Install"
  Pop $ComponentsLabel
  SendMessage $ComponentsLabel ${WM_SETFONT} $ModernFontTitle 0
  SetCtlColors $ComponentsLabel 0x1A1A1A transparent

  ; Description with improved spacing
  ${NSD_CreateLabel} 0 55 100% 40 "Choose which additional components you want to install with LYTE. Uncheck any components you don't need."
  Pop $0
  SendMessage $0 ${WM_SETFONT} $ModernFont 0
  SetCtlColors $0 0x666666 transparent

  ; Python component with better spacing
  ${NSD_CreateCheckBox} 20 105 90% 24 "Python 3.13.11 (required; needs ~7GB free space)"
  Pop $PythonCheckbox
  SendMessage $PythonCheckbox ${WM_SETFONT} $ModernFont 0
  SetCtlColors $PythonCheckbox 0x1A1A1A transparent
  ${NSD_SetState} $PythonCheckbox ${BST_CHECKED}

  ; VLC component
  ${NSD_CreateCheckBox} 20 135 90% 24 "VLC Media Player (playback support; needs ~60MB free space)"
  Pop $VLCCheckbox
  SendMessage $VLCCheckbox ${WM_SETFONT} $ModernFont 0
  SetCtlColors $VLCCheckbox 0x1A1A1A transparent
  ${NSD_SetState} $VLCCheckbox ${BST_CHECKED}

  ; VC++ Redistributable component
  ${NSD_CreateCheckBox} 20 165 90% 24 "Microsoft Visual C++ Redistributable (required by other components; needs ~16MB)"
  Pop $VCRedistCheckbox
  SendMessage $VCRedistCheckbox ${WM_SETFONT} $ModernFont 0
  SetCtlColors $VCRedistCheckbox 0x1A1A1A transparent
  ${NSD_SetState} $VCRedistCheckbox ${BST_CHECKED}

  nsDialogs::Show
FunctionEnd

Function ComponentsPageLeave
  ${NSD_GetState} $PythonCheckbox $InstallPython
  ${NSD_GetState} $VLCCheckbox $InstallVLC
  ${NSD_GetState} $VCRedistCheckbox $InstallVCRedist
FunctionEnd

;--------------------------------
; Shortcuts Page Functions
;--------------------------------

Function ShortcutsPageCreate
  nsDialogs::Create 1018
  Pop $ShortcutsPageDialog
  ${If} $ShortcutsPageDialog == error
    Abort
  ${EndIf}

  ; Title with modern styling
  ${NSD_CreateLabel} 0 20 100% 30 "Choose Shortcuts"
  Pop $ShortcutsLabel
  SendMessage $ShortcutsLabel ${WM_SETFONT} $ModernFontTitle 0
  SetCtlColors $ShortcutsLabel 0x1A1A1A transparent

  ; Description
  ${NSD_CreateLabel} 0 55 100% 40 "Select where you would like shortcuts to be created for easy access to LYTE."
  Pop $0
  SendMessage $0 ${WM_SETFONT} $ModernFont 0
  SetCtlColors $0 0x666666 transparent

  ; Start Menu checkbox with better spacing
  ${NSD_CreateCheckBox} 20 105 90% 24 "Create Start Menu shortcut"
  Pop $0
  SendMessage $0 ${WM_SETFONT} $ModernFont 0
  SetCtlColors $0 0x1A1A1A transparent
  ${NSD_SetState} $0 ${BST_CHECKED}
  ${NSD_OnClick} $0 OnStartMenuClick
  StrCpy $AddStartMenu ${BST_CHECKED}

  ; Desktop checkbox
  ${NSD_CreateCheckBox} 20 135 90% 24 "Create Desktop shortcut"
  Pop $0
  SendMessage $0 ${WM_SETFONT} $ModernFont 0
  SetCtlColors $0 0x1A1A1A transparent
  ${NSD_SetState} $0 ${BST_CHECKED}
  ${NSD_OnClick} $0 OnDesktopClick
  StrCpy $AddDesktop ${BST_CHECKED}

  nsDialogs::Show
FunctionEnd

Function ShortcutsPageLeave
  ; states already captured by click handlers; no-op placeholder
FunctionEnd

Function OnStartMenuClick
  Pop $0
  ${NSD_GetState} $0 $AddStartMenu
FunctionEnd

Function OnDesktopClick
  Pop $0
  ${NSD_GetState} $0 $AddDesktop
FunctionEnd

;--------------------------------
; Install Sections
;--------------------------------

Section "Microsoft Visual C++ Redistributable" SEC_VC
  ${If} $InstallVCRedist == ${BST_CHECKED}
    DetailPrint "Downloading Microsoft Visual C++ Redistributable..."
    SetOutPath "$PLUGINSDIR"
    
    ; Show progress
    inetc::get "https://aka.ms/vs/17/release/vc_redist.x64.exe" "$PLUGINSDIR\vc_redist.x64.exe" /end
    Pop $0
    ${If} $0 != "OK"
      MessageBox MB_ICONSTOP|MB_RETRYCANCEL "Failed to download VC++ Redistributable. Error: $0. Click Retry to try again or Cancel to skip this component." IDRETRY retry_vc_download IDCANCEL skip_vc
      Goto skip_vc
      retry_vc_download:
      inetc::get "https://aka.ms/vs/17/release/vc_redist.x64.exe" "$PLUGINSDIR\vc_redist.x64.exe" /end
      Pop $0
      ${If} $0 != "OK"
        MessageBox MB_ICONSTOP "Failed to download VC++ Redistributable after retry. Skipping this component."
        Goto skip_vc
      ${EndIf}
    ${EndIf}

    DetailPrint "Installing Microsoft Visual C++ Redistributable..."
    ExecWait '"$PLUGINSDIR\vc_redist.x64.exe" /install /quiet /norestart' $0
    ${If} $0 != 0
      MessageBox MB_ICONEXCLAMATION "VC++ Redistributable installation completed with warnings. This may not affect LYTE functionality."
    ${EndIf}
    
    skip_vc:
  ${EndIf}
SectionEnd

Section "Python 3.13.11" SEC_PYTHON
  ${If} $InstallPython == ${BST_CHECKED}
    ; Check if Python is already installed
    DetailPrint "Checking if Python is already installed..."
    ClearErrors
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.13\InstallPath" ""
    ${If} ${Errors}
      ; Try checking PATH
      nsExec::ExecToLog 'cmd /c "python --version"'
      Pop $0
      ${If} $0 == 0
        DetailPrint "Python is already installed and available in PATH."
        Goto python_installed
      ${EndIf}
      
      ; Python not found, proceed with installation
      DetailPrint "Python not found. Downloading Python installer..."
      SetOutPath "$PLUGINSDIR"
      
      inetc::get "https://www.python.org/ftp/python/3.13.11/python-3.13.11-amd64.exe" "$PLUGINSDIR\python-3.13.11-amd64.exe" /end
      Pop $0
      ${If} $0 != "OK"
        MessageBox MB_ICONSTOP|MB_RETRYCANCEL "Failed to download Python installer. Error: $0. Click Retry to try again or Cancel to skip this component." IDRETRY retry_python_download IDCANCEL skip_python
        Goto skip_python
        retry_python_download:
        DetailPrint "Retrying Python download..."
        inetc::get "https://www.python.org/ftp/python/3.13.11/python-3.13.11-amd64.exe" "$PLUGINSDIR\python-3.13.11-amd64.exe" /end
        Pop $0
        ${If} $0 != "OK"
          MessageBox MB_ICONSTOP "Failed to download Python. Skipping."
          Goto skip_python
        ${EndIf}
      ${EndIf}

      DetailPrint "Installing Python..."
      ExecWait '"$PLUGINSDIR\python-3.13.11-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_tcltk=0' $0
      ${If} $0 != 0
        ; Exit code 1638 means "Another version is already installed" - treat as success
        ${If} $0 == 1638
          DetailPrint "Python is already installed on this system (exit code 1638). Skipping installation."
          Goto python_installed
        ${Else}
          MessageBox MB_ICONSTOP "Python installation failed with exit code: $0. LYTE may not function properly without Python."
          Goto skip_python
        ${EndIf}
      ${EndIf}
    ${Else}
      DetailPrint "Python 3.13 is already installed."
      Goto python_installed
    ${EndIf}

    python_installed:
    ; Wait for Python to be available in PATH
    DetailPrint "Waiting for Python to be available..."
    Sleep 3000

    DetailPrint "Installing DearPyGui via pip..."
    
    ; Try to find Python executable in common locations
    StrCpy $1 ""
    ReadRegStr $1 HKLM "SOFTWARE\Python\PythonCore\3.13\InstallPath" ""
    ${If} $1 != ""
      ; Found Python in registry, use full path
      StrCpy $1 "$1python.exe"
      IfFileExists "$1" 0 try_path_python
      DetailPrint "Using Python from registry: $1"
      nsExec::ExecToLog '"$1" -m pip install dearpygui --upgrade'
      Pop $0
      ${If} $0 == 0
        Goto pip_success
      ${EndIf}
    ${EndIf}
    
    try_path_python:
    ; Try using python from PATH (use a new cmd session to get updated PATH)
    DetailPrint "Trying Python from PATH..."
    nsExec::ExecToLog 'cmd /c "python -m pip install dearpygui --upgrade"'
    Pop $0
    ${If} $0 == 0
      Goto pip_success
    ${EndIf}
    
    ; Try with full path using common installation location (system-wide)
    StrCpy $1 "$PROGRAMFILES64\Python313\python.exe"
    IfFileExists "$1" 0 try_user_python
    DetailPrint "Trying Python from Program Files: $1"
    nsExec::ExecToLog '"$1" -m pip install dearpygui --upgrade'
    Pop $0
    ${If} $0 == 0
      Goto pip_success
    ${EndIf}
    
    try_user_python:
    ; Try user's local Python installation
    StrCpy $1 "$LOCALAPPDATA\Programs\Python\Python313\python.exe"
    IfFileExists "$1" 0 try_py_launcher
    DetailPrint "Trying Python from user AppData: $1"
    nsExec::ExecToLog '"$1" -m pip install dearpygui --upgrade'
    Pop $0
    ${If} $0 == 0
      Goto pip_success
    ${EndIf}
    
    try_py_launcher:
    ; Try using py launcher (Python 3.13)
    DetailPrint "Trying Python launcher (py -3.13)..."
    nsExec::ExecToLog 'cmd /c "py -3.13 -m pip install dearpygui --upgrade"'
    Pop $0
    ${If} $0 == 0
      Goto pip_success
    ${EndIf}
    
    ; Try using py launcher (default Python 3)
    DetailPrint "Trying Python launcher (py -3)..."
    nsExec::ExecToLog 'cmd /c "py -3 -m pip install dearpygui --upgrade"'
    Pop $0
    ${If} $0 == 0
      Goto pip_success
    ${EndIf}
    
    ; All methods failed
    MessageBox MB_ICONEXCLAMATION "Failed to install DearPyGui via pip (exit code: $0). You may need to install it manually later.$\n$\nYou can install it by running:$\npython -m pip install dearpygui --upgrade"
    Goto pip_done
    
    pip_success:
    DetailPrint "Successfully installed DearPyGui via pip"
    
    pip_done:
    
    skip_python:
  ${EndIf}
SectionEnd

Section "VLC Media Player" SEC_VLC
  ${If} $InstallVLC == ${BST_CHECKED}
    DetailPrint "Downloading VLC installer..."
    SetOutPath "$PLUGINSDIR"
    
    inetc::get "https://mirror.aarnet.edu.au/pub/videolan/vlc/3.0.21/win64/vlc-3.0.21-win64.exe" "$PLUGINSDIR\vlc-3.0.21-win64.exe" /end
    Pop $0
    ${If} $0 != "OK"
      MessageBox MB_ICONSTOP|MB_RETRYCANCEL "Failed to download VLC installer. Error: $0. Click Retry to try again or Cancel to skip this component." IDRETRY retry_vlc_download IDCANCEL skip_vlc
      Goto skip_vlc
      retry_vlc_download:
      DetailPrint "Retrying VLC download..."
      inetc::get "https://mirror.aarnet.edu.au/pub/videolan/vlc/3.0.21/win64/vlc-3.0.21-win64.exe" "$PLUGINSDIR\vlc-3.0.21-win64.exe" /end
      Pop $0
      ${If} $0 != "OK"
        MessageBox MB_ICONSTOP "Failed to download VLC. Skipping."
        Goto skip_vlc
      ${EndIf}
    ${EndIf}

    DetailPrint "Installing VLC..."
    ExecWait '"$PLUGINSDIR\vlc-3.0.21-win64.exe" /S' $0
    ${If} $0 != 0
      MessageBox MB_ICONEXCLAMATION "VLC installation completed with warnings (exit code: $0). Video playback features may be limited."
    ${EndIf}
    
    skip_vlc:
  ${EndIf}
SectionEnd

Section "LYTE Application" SEC_MAIN
  ; Ensure installation directory exists and is writable
  DetailPrint "Preparing installation directory..."
  CreateDirectory "$INSTDIR"
  IfFileExists "$INSTDIR\*.*" 0 dir_error
  SetOutPath "$INSTDIR"
  AddSize 22000

  ; Download to temporary location first, then copy to final location
  DetailPrint "Downloading LYTE..."
  SetOutPath "$PLUGINSDIR"
  ; Build download URL based on chosen version
  StrCpy $0 $SelectedVersion
  ${If} $0 == ""
    StrCpy $0 "latest"
  ${EndIf}
  ${If} $0 == "latest"
    StrCpy $1 "https://github.com/StroepWafel/LYTE/releases/latest/download/LYTE.exe"
  ${Else}
    StrCpy $1 "https://github.com/StroepWafel/LYTE/releases/download/$0/LYTE.exe"
  ${EndIf}

  inetc::get "$1" "$PLUGINSDIR\LYTE.exe" /end
  Pop $0
  ${If} $0 != "OK"
    MessageBox MB_ICONSTOP|MB_RETRYCANCEL "Failed to download LYTE. Error: $0. Click Retry to try again or Cancel to abort installation." IDRETRY retry_lyte_download IDCANCEL abort_install
    retry_lyte_download:
    DetailPrint "Retrying LYTE download..."
    inetc::get "$1" "$PLUGINSDIR\LYTE.exe" /end
    Pop $0
    ${If} $0 != "OK"
      MessageBox MB_ICONSTOP "Failed to download LYTE. Installation aborted. (Is your internet connected?)"
      Abort
    ${EndIf}
  ${EndIf}

  ; Copy downloaded file to installation directory
  DetailPrint "Installing LYTE..."
  SetOutPath "$INSTDIR"
  CopyFiles "$PLUGINSDIR\LYTE.exe" "$INSTDIR\LYTE.exe"
  IfFileExists "$INSTDIR\LYTE.exe" 0 copy_error
  Goto install_done

  dir_error:
    MessageBox MB_ICONSTOP "Cannot create or access installation directory: $INSTDIR$\nPlease ensure you have administrator privileges and the directory is writable."
    Abort

  copy_error:
    MessageBox MB_ICONSTOP "Failed to copy LYTE.exe to installation directory. Please check permissions."
    Abort

  install_done:

  ; Create shortcuts if selected
  ${If} $AddStartMenu == ${BST_CHECKED}
    CreateDirectory "$SMPROGRAMS\LYTE"
    CreateShortcut "$SMPROGRAMS\LYTE\LYTE.lnk" "$INSTDIR\LYTE.exe" "" "$INSTDIR\LYTE.exe" 0
    CreateShortcut "$SMPROGRAMS\LYTE\Uninstall LYTE.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  ${EndIf}

  ${If} $AddDesktop == ${BST_CHECKED}
    CreateShortcut "$DESKTOP\LYTE.lnk" "$INSTDIR\LYTE.exe" "" "$INSTDIR\LYTE.exe" 0
  ${EndIf}

  ; Write uninstall info
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "DisplayName" "LYTE"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "DisplayVersion" "1.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "Publisher" "StroepWafel"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "NoRepair" 1

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  abort_install:
SectionEnd

;--------------------------------
; Finish Page Functions
;--------------------------------

Function .onInstSuccess
  ; Installation completed successfully
  DetailPrint "Installation completed successfully!"
FunctionEnd

;--------------------------------
; Install Files Page Enhancement
;--------------------------------
Function .onInstFilesPage
  ; Enhance the install files page appearance
  FindWindow $0 "#32770" "" $HWNDPARENT
  GetDlgItem $1 $0 1006  ; Detail text control
  ${If} $1 <> 0
    SendMessage $1 ${WM_SETFONT} $ModernFont 0
    SetCtlColors $1 0x1A1A1A transparent
  ${EndIf}
FunctionEnd

;--------------------------------
; Uninstaller Section
;--------------------------------
Section "Uninstall" Uninstall
  ; Remove application executable
  Delete "$INSTDIR\LYTE.exe"

  ${If} $RemoveSettings == "1"
    ; Remove settings/config files
    Delete "$INSTDIR\banned_IDs.json"
    Delete "$INSTDIR\banned_users.json"
    Delete "$INSTDIR\config.json"
    Delete "$INSTDIR\*.log"
    ; Remove logs directory if empty
    RMDir "$INSTDIR\logs"
  ${EndIf}

  ; Remove uninstaller
  Delete "$INSTDIR\uninstall.exe"

  ; Remove shortcuts
  Delete "$SMPROGRAMS\LYTE\LYTE.lnk"
  Delete "$SMPROGRAMS\LYTE\Uninstall LYTE.lnk"
  RMDir "$SMPROGRAMS\LYTE"
  Delete "$DESKTOP\LYTE.lnk"

  ; Remove registry entries
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE"
  DeleteRegKey HKLM "Software\LYTE"

  ; Remove installation directory if empty
  RMDir "$INSTDIR"

  ; Show completion message
  MessageBox MB_ICONINFORMATION "LYTE has been successfully uninstalled from your computer."
SectionEnd


;--------------------------------
; Uninstaller Init
;--------------------------------

Function un.onInit
  ; Read installation directory from registry
  ReadRegStr $INSTDIR HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE" "InstallLocation"

  ; If not found, use default
  ${If} $INSTDIR == ""
    StrCpy $INSTDIR "$PROGRAMFILES64\LYTE"
  ${EndIf}

  ; Confirm uninstall
  MessageBox MB_ICONQUESTION|MB_YESNO "Are you sure you want to completely remove LYTE and all of its components?" IDYES continue_uninstall IDNO cancel_uninstall
  cancel_uninstall:
    Abort
  continue_uninstall:

  ; Ask about removing settings
  MessageBox MB_ICONQUESTION|MB_YESNO "Do you also want to remove all settings and configuration files? (This will delete config.json, banned lists, and logs)" IDYES remove_settings IDNO keep_settings

  remove_settings:
    StrCpy $RemoveSettings "1"
    Goto done_settings

  keep_settings:
    StrCpy $RemoveSettings "0"
    Goto done_settings

  done_settings:
FunctionEnd

;--------------------------------
; Section Descriptions
;--------------------------------
; Note: Section descriptions are handled in the custom ComponentsPageCreate function






