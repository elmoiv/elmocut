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
        StringStruct(u'FileDescription', u'{2}'),
        StringStruct(u'FileVersion', u'{0}'),
        StringStruct(u'InternalName', u'{2}'),
        StringStruct(u'LegalCopyright', u'Khaled El-Morshedy (elmoiv) 2015-2021'),
        StringStruct(u'OriginalFilename', u'{2}.exe'),
        StringStruct(u'ProductName', u'{2}'),
        StringStruct(u'ProductVersion', u'{0}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''

sepc_file = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['{0}src\\\\{5}.py'],
             pathex=['{0}{5}'],
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
          name='{5}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console={4} , version='tmp.txt', icon='{0}exe\\\\icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude={2},
               name='{5}')'''

iss_file = '''#define MyAppName "{3}"
#define MyAppVersion "{1}"
#define MyAppPublisher "elmoiv"
#define MyAppURL "https://elmoiv.github.io/"
#define MyAppExeName "{3}.exe"

[Setup]
AppId={{{{{4}}}
AppName={{#MyAppName}}
AppVersion={1}
VersionInfoVersion={2}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableDirPage=yes
DisableProgramGroupPage=yes
UsedUserAreasWarning=no
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename={3} {1} x64
UninstallDisplayIcon={{app}}\\{3}.exe
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
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
{5}

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent'''

excluded_binaries = ['api-ms-win-core-console-l1-1-0.dll', 'api-ms-win-core-datetime-l1-1-0.dll', 'api-ms-win-core-debug-l1-1-0.dll', 'api-ms-win-core-errorhandling-l1-1-0.dll', 'api-ms-win-core-file-l1-1-0.dll', 'api-ms-win-core-file-l1-2-0.dll', 'api-ms-win-core-file-l2-1-0.dll', 'api-ms-win-core-handle-l1-1-0.dll', 'api-ms-win-core-heap-l1-1-0.dll', 'api-ms-win-core-interlocked-l1-1-0.dll', 'api-ms-win-core-libraryloader-l1-1-0.dll', 'api-ms-win-core-localization-l1-2-0.dll', 'api-ms-win-core-memory-l1-1-0.dll', 'api-ms-win-core-namedpipe-l1-1-0.dll', 'api-ms-win-core-processenvironment-l1-1-0.dll', 'api-ms-win-core-processthreads-l1-1-0.dll', 'api-ms-win-core-processthreads-l1-1-1.dll', 'api-ms-win-core-profile-l1-1-0.dll', 'api-ms-win-core-rtlsupport-l1-1-0.dll', 'api-ms-win-core-string-l1-1-0.dll', 'api-ms-win-core-synch-l1-1-0.dll', 'api-ms-win-core-synch-l1-2-0.dll', 'api-ms-win-core-sysinfo-l1-1-0.dll', 'api-ms-win-core-timezone-l1-1-0.dll', 'api-ms-win-core-util-l1-1-0.dll', 'api-ms-win-crt-conio-l1-1-0.dll', 'api-ms-win-crt-convert-l1-1-0.dll', 'api-ms-win-crt-environment-l1-1-0.dll', 'api-ms-win-crt-filesystem-l1-1-0.dll', 'api-ms-win-crt-heap-l1-1-0.dll', 'api-ms-win-crt-locale-l1-1-0.dll', 'api-ms-win-crt-math-l1-1-0.dll', 'api-ms-win-crt-multibyte-l1-1-0.dll', 'api-ms-win-crt-process-l1-1-0.dll', 'api-ms-win-crt-runtime-l1-1-0.dll', 'api-ms-win-crt-stdio-l1-1-0.dll', 'api-ms-win-crt-string-l1-1-0.dll', 'api-ms-win-crt-time-l1-1-0.dll', 'api-ms-win-crt-utility-l1-1-0.dll', 'd3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll', 'opengl32sw.dll', 'Qt5DBus.dll', 'Qt5Network.dll', 'Qt5Qml.dll', 'Qt5Quick.dll', 'Qt5Svg.dll', 'Qt5WebSockets.dll', 'ucrtbase.dll', 'VCRUNTIME140_1.dll', 'Qt5QmlModels.dll', 'MSVCP140_1.dll']

excluded_upx = ['qwindows.dll', 'qsvgicon.dll', 'qxdgdesktopportal.dll', 'qwindowsvistastyle.dll']

excluded_modules = ['tk', 'tcl', '_tkinter', 'tkinter', 'Tkinter', 'FixTk', 'PIL', 'tk', 'tcl', '_tkinter', 'tkinter', 'Tkinter', 'FixTk', 'matplotlib', 'IPython', 'scipy', 'eel', 'jedi', 'win32com', 'numpy', 'wcwidth', 'win32wnet', '_asyncio', '_bz2', '_decimal', '_hashlib', '_lzma', '_multiprocessing', '_overlapped', '_win32sysloader', '_cffi_backend', '_openssl', 'cryptography', 'docutils']

is_gui = not bool(input('Press Enter for GUI, or anything for Console: '))
app_name = 'elmoCut'
app_guid = '31430AA0-C0A7-4598-991B-E3B2CD961817'
version = input('Enter version: ')

try:
    sum(map(int, version.split('.')))
except:
    print('Wrong version format!')
    exit(0)

import os, shutil, time, re

constants_path = 'src\\constants.py'

# Auto update version in main.py
src_main = open(constants_path).read()
open(constants_path + '_backup', 'w').write(src_main)
new_main = re.sub(
              r"VERSION = '(\d+\.\d+\.\d+)'",
              f"VERSION = '{version}'", 
              src_main
          )
open(constants_path, 'w').write(new_main)

def version_format(s):
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
    version_format(version),
    app_name
)

sepc_file = sepc_file.format(
    CUR_DIR.replace('\\', '\\\\'),
    excluded_binaries,
    excluded_upx,
    excluded_modules,
    not is_gui,
    app_name
)

open('tmp.txt', 'w').write(version_file)
open('tmp.spec', 'w').write(sepc_file)

start = time.time()

print('>>> [PyInstaller] Converting project to exe')
os.system('pyinstaller tmp.spec --noconfirm')

app_path = f'output\\{app_name}\\'

platforms_dlls = app_path + 'PyQt5\\Qt\\plugins\\platforms\\'
bin_dlls = app_path + 'PyQt5\\Qt\\bin\\'

## Kill elmocut in case was running from old output folder
os.system('taskkill /f /im elmoCut.exe')

## Remove previous builds
if os.path.exists(app_path):
    shutil.rmtree(app_path)

os.makedirs('output', exist_ok=True)
os.rename('dist\\' + app_name, app_path)

# Compiling restart.c to restart.exe
print('>>> [GCC] Compiling restart.c to restart.exe')
os.system(f'gcc src\\tools\\restart.c -o {app_path}restart.exe')

# Moving Manuf to output
os.makedirs(app_path + 'manuf', exist_ok=True)
shutil.copy('exe\\manuf', app_path + 'manuf\\manuf')

# # UPX with Executable and restart.exe
# os.system(f'upx {app_path}{app_name}.exe')
# os.system(f'upx {app_path}restart.exe')

print('>>> Removing unnecessary files')
## Remove all platforms dll but qwindows.dll
for dll in os.listdir(platforms_dlls):
    if not 'qwindows.dll' in dll:
        os.remove(platforms_dlls + dll)

## Remove unneeded QT bin dlls
for dll in os.listdir(bin_dlls):
    if dll in excluded_binaries:
        os.remove(bin_dlls + dll)

## Remove un needed folders
for rm in [
  'dist',
  'build', 
  app_path + 'PyQt5\\Qt\\translations',
  app_path + 'PyQt5\\Qt\\plugins\\imageformats',
  app_path + 'PyQt5\\Qt\\plugins\\iconengines',
  app_path + 'PyQt5\\Qt\\plugins\\generic'
  ]:
    shutil.rmtree(rm)

for _dir in os.listdir(app_path):
    if _dir.endswith('.dist-info'):
        try:
            shutil.rmtree(os.path.join(app_path, _dir))
        except:
            pass

# Dynamically add files list to iss file
files_list = []
iss_cmd = 'Source: "{}"; DestDir: "{{app}}{}"; Flags: ignoreversion '
for item in os.listdir(app_path):
    if os.path.isdir(app_path + item):
        if any(os.path.isdir(f'{app_path}{item}\\{inner}') for inner in os.listdir(app_path + item)):
            files_list.append(iss_cmd.format(app_path + item + '\\*', f'\\{item}') + 'recursesubdirs createallsubdirs')
        else:
            files_list.append(iss_cmd.format(app_path + item + '\\*', f'\\{item}'))
    else:
        files_list.append(iss_cmd.format(app_path + item, ''))

iss_file = iss_file.format(
    CUR_DIR,
    version,
    '.'.join(map(str, version_format(version))),
    app_name,
    app_guid,
    '\n'.join(files_list)
)

open('tmp.iss', 'w').write(iss_file)

print('>>> [Inno Setup] Packaging exe inised Setup file')

# Compile ISS inno setup script
_ = os.popen('iscc tmp.iss').read()

os.remove('tmp.txt')
os.remove('tmp.spec')
os.remove('tmp.iss')

end = time.time()

print('>>> Finished in', int(end - start), 'seconds')
input('\nSee your files at "output\\"')