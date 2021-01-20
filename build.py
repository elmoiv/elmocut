version_file = '''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={1},
    prodvers={1},
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'elmoiv Apps'),
        StringStruct(u'FileDescription', u'elmoCut lets you spoof everyone on your network'),
        StringStruct(u'FileVersion', u'{0}'),
        StringStruct(u'InternalName', u'elmocut'),
        StringStruct(u'LegalCopyright', u'Khaled El-Morshedy (elmoiv) 2015-2021'),
        StringStruct(u'OriginalFilename', u'elmocut.exe'),
        StringStruct(u'ProductName', u'elmoCut'),
        StringStruct(u'ProductVersion', u'{0}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''

sepc_file = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['{0}src\\\\elmocut.py'],
             pathex=['{0}elmocut'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes={3},
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

excluded_binaries = {1}

a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='elmocut',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console={4} , version='tmp.txt', icon='{0}exe\\\\icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude={2},
               name='elmocut')'''

iss_file = '''#define MyAppName "elmoCut"
#define MyAppVersion "{1}"
#define MyAppPublisher "elmoiv"
#define MyAppURL "https://elmoiv.github.io/"
#define MyAppExeName "elmocut.exe"

[Setup]
AppId={{{{31430AA0-C0A7-4598-991B-E3B2CD961817}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableDirPage=yes
DisableProgramGroupPage=yes
UsedUserAreasWarning=no
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename=elmoCut Installer
UninstallDisplayIcon={{app}}\\elmocut.exe
WizardSmallImageFile={0}exe\\setup_img.bmp
SolidCompression=yes
Compression=lzma2/ultra64
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "{0}output\\elmocut\\elmocut.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\_ctypes.pyd"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\_queue.pyd"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\_socket.pyd"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\base_library.zip"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\elmocut.exe.manifest"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\msvcp140.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\pyexpat.pyd"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\python3.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\python37.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\pywintypes37.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\Qt5Core.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\Qt5Gui.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\Qt5Widgets.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\select.pyd"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\VCRUNTIME140.dll"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\win32api.pyd"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\win32gui.pyd"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{0}output\\elmocut\\PyQt5\\*"; DestDir: "{{app}}\\PyQt5"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{0}output\\elmocut\\manuf\\*"; DestDir: "{{app}}\\manuf"; Flags: ignoreversion
Source: "{0}output\\elmocut\\include\\*"; DestDir: "{{app}}\\include"; Flags: ignoreversion

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent'''

excluded_binaries = ['api-ms-win-core-console-l1-1-0.dll', 'api-ms-win-core-datetime-l1-1-0.dll', 'api-ms-win-core-debug-l1-1-0.dll', 'api-ms-win-core-errorhandling-l1-1-0.dll', 'api-ms-win-core-file-l1-1-0.dll', 'api-ms-win-core-file-l1-2-0.dll', 'api-ms-win-core-file-l2-1-0.dll', 'api-ms-win-core-handle-l1-1-0.dll', 'api-ms-win-core-heap-l1-1-0.dll', 'api-ms-win-core-interlocked-l1-1-0.dll', 'api-ms-win-core-libraryloader-l1-1-0.dll', 'api-ms-win-core-localization-l1-2-0.dll', 'api-ms-win-core-memory-l1-1-0.dll', 'api-ms-win-core-namedpipe-l1-1-0.dll', 'api-ms-win-core-processenvironment-l1-1-0.dll', 'api-ms-win-core-processthreads-l1-1-0.dll', 'api-ms-win-core-processthreads-l1-1-1.dll', 'api-ms-win-core-profile-l1-1-0.dll', 'api-ms-win-core-rtlsupport-l1-1-0.dll', 'api-ms-win-core-string-l1-1-0.dll', 'api-ms-win-core-synch-l1-1-0.dll', 'api-ms-win-core-synch-l1-2-0.dll', 'api-ms-win-core-sysinfo-l1-1-0.dll', 'api-ms-win-core-timezone-l1-1-0.dll', 'api-ms-win-core-util-l1-1-0.dll', 'api-ms-win-crt-conio-l1-1-0.dll', 'api-ms-win-crt-convert-l1-1-0.dll', 'api-ms-win-crt-environment-l1-1-0.dll', 'api-ms-win-crt-filesystem-l1-1-0.dll', 'api-ms-win-crt-heap-l1-1-0.dll', 'api-ms-win-crt-locale-l1-1-0.dll', 'api-ms-win-crt-math-l1-1-0.dll', 'api-ms-win-crt-multibyte-l1-1-0.dll', 'api-ms-win-crt-process-l1-1-0.dll', 'api-ms-win-crt-runtime-l1-1-0.dll', 'api-ms-win-crt-stdio-l1-1-0.dll', 'api-ms-win-crt-string-l1-1-0.dll', 'api-ms-win-crt-time-l1-1-0.dll', 'api-ms-win-crt-utility-l1-1-0.dll', 'd3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll', 'opengl32sw.dll', 'Qt5DBus.dll', 'Qt5Network.dll', 'Qt5Qml.dll', 'Qt5Quick.dll', 'Qt5Svg.dll', 'Qt5WebSockets.dll', 'ucrtbase.dll']

excluded_upx = ['qwindows.dll', 'qsvgicon.dll', 'qxdgdesktopportal.dll', 'qwindowsvistastyle.dll']

excluded_modules = ['tk', 'tcl', '_tkinter', 'tkinter', 'Tkinter', 'FixTk', 'PIL', 'tk', 'tcl', '_tkinter', 'tkinter', 'Tkinter', 'FixTk', 'matplotlib', 'IPython', 'scipy', 'eel', 'cryptography', 'jedi', 'win32com', 'numpy', 'wcwidth', 'win32wnet', 'unicodedata', '_asyncio', '_bz2', '_decimal', '_hashlib', '_lzma', '_multiprocessing', '_overlapped', '_win32sysloader', '_ssl']

is_gui = True
version = '0.1'

import os, shutil, time

def verison_fromat(s):
    # Convert xx.xx.xx.xx -> (xx, xx, xx, xx)
    e = [0, 0, 0, 0]
    for n, i in enumerate(s.split('.')):
            e[n] = int(i)
    return tuple(e)

CUR_DIR = os.path.dirname(__file__)

if CUR_DIR:
    os.chdir(CUR_DIR)
    CUR_DIR += '\\'

# Execute Pyinstaller
version_file = version_file.format(
    version,
    verison_fromat(version)
)

sepc_file = sepc_file.format(
    CUR_DIR.replace('\\', '\\\\'),
    excluded_binaries,
    excluded_upx,
    excluded_modules,
    not is_gui
)

iss_file = iss_file.format(
    CUR_DIR,
    version
)

open('tmp.txt', 'w').write(version_file)
open('tmp.spec', 'w').write(sepc_file)
open('tmp.iss', 'w').write(iss_file)

start = time.time()

print('>>> Running PyInstaller')
os.system('pyinstaller tmp.spec --log-level "ERROR"')

app_path = 'output\\elmocut\\'
platforms_dlls = app_path + 'PyQt5\\Qt\\plugins\\platforms\\'

## Remove previous builds
if os.path.exists(app_path):
    shutil.rmtree(app_path)

os.makedirs('output', exist_ok=True)

## Move manuf mac database
os.rename('dist\\elmocut', app_path)
os.makedirs(app_path + 'manuf', exist_ok=True)
shutil.copy('exe\\manuf', app_path + 'manuf\\manuf')

print('>>> Removing unnecessary files')
## Remove all platforms dll but qwindows.dll
for dll in os.listdir(platforms_dlls):
    if not 'qwindows.dll' in dll:
        os.remove(platforms_dlls + dll)

## Remove un needed folders
for rm in ['dist', 'build', app_path + 'PyQt5\\Qt\\translations', app_path + 'PyQt5\\Qt\\plugins\\imageformats']:
    shutil.rmtree(rm)

print('>>> Compiling Setup file')
# Compile ISS inno setup script
_ = os.popen('iscc tmp.iss').read()

os.remove('tmp.txt')
os.remove('tmp.spec')
os.remove('tmp.iss')

end = time.time()

print('>>> Finished in', int(end - start), 'seconds')
input('\nSee your files at "output\\"')