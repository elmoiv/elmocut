#define MyAppName "elmoCut"
#define MyAppVersion "1.1.1"
#define MyAppPublisher "elmoiv"
#define MyAppURL "https://elmoiv.github.io/"
#define MyAppExeName "elmoCut.exe"

[Setup]
AppId={{31430AA0-C0A7-4598-991B-E3B2CD961817}
AppName={#MyAppName}
AppVersion=1.1.1
VersionInfoVersion=1.1.1.0
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
UsedUserAreasWarning=no
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename=elmoCut 1.1.1 x64
UninstallDisplayIcon={app}\elmoCut.exe
WizardSmallImageFile=C:\Users\user\Desktop\elmocut\exe\setup_img.bmp
SolidCompression=yes
Compression=lzma2/ultra64
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273
WizardStyle=modern

[InstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "output\elmoCut\base_library.zip"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\certifi\*"; DestDir: "{app}\certifi"; Flags: ignoreversion 
Source: "output\elmoCut\charset_normalizer\*"; DestDir: "{app}\charset_normalizer"; Flags: ignoreversion 
Source: "output\elmoCut\elmoCut.exe"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\libcrypto-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\libffi-7.dll"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\libssl-1_1.dll"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\manuf\*"; DestDir: "{app}\manuf"; Flags: ignoreversion 
Source: "output\elmoCut\pyexpat.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\PyQt6\*"; DestDir: "{app}\PyQt6"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "output\elmoCut\python3.dll"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\python310.dll"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\pywin32_system32\*"; DestDir: "{app}\pywin32_system32"; Flags: ignoreversion 
Source: "output\elmoCut\select.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\VCRUNTIME140.dll"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\win32\*"; DestDir: "{app}\win32"; Flags: ignoreversion 
Source: "output\elmoCut\_ctypes.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\_overlapped.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\_queue.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\_ssl.pyd"; DestDir: "{app}"; Flags: ignoreversion 
Source: "output\elmoCut\_uuid.pyd"; DestDir: "{app}"; Flags: ignoreversion 

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent shellexec