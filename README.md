<h1 align="center">
  <br>
  <a href="https://github.com/elmoiv/elmocut"><img src="https://github.com/elmoiv/elmocut/blob/main/data/icon.png" alt="elmoCut icon"></a>
  <br>
  elmoCut
  <br>
</h1>
<h4 align="center">Eye candy ARP spoofer for Windows</h4>

<p align=center>
  <a target="_blank" href="http://hits.dwyl.io/elmoiv/elmocut" title="Latest release">
    <img src="http://hits.dwyl.io/elmoiv/elmocut.svg">
  </a>
  <a target="_blank" href="https://github.com/elmoiv/elmocut/releases/latest" title="Latest release">
    <img src="https://img.shields.io/github/v/release/elmoiv/elmocut">
  </a>
  <a target="_blank" href="https://github.com/elmoiv/elmocut/releases/latest" title="Downloads">
    <img src="https://img.shields.io/github/downloads/elmoiv/elmocut/total.svg">
  </a>
  <a target="_blank" href="LICENSE" title="License: MIT">
    <img src="https://img.shields.io/github/license/elmoiv/elmocut">
  </a>
</p>

<hr>
<p align="center">
  <a href="#screenshots">Screenshots</a> &bull;
  <a href="#description">Description</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#limitations">Limitations</a> &bull;
  <a href="#download">Download</a> &bull;
  <a href="#requirements">Requirements</a> &bull;
  <a href="#run">Run</a> &bull;
  <a href="#build">Build</a> &bull;
  <a href="#manual">Manual</a> &bull;
  <a href="#todo">TODO</a> &bull;
  <a href="#contribution">Contribution</a> &bull;
  <a href="#license">License</a>
</p>
<hr>

## Screenshots

<table>
  <tr>
    <th colspan="3">
      <samp><h3>Main window</h3></samp>
    </th>
  </tr>
  <tr>
    <th colspan="3">
      <img src="https://github.com/elmoiv/elmocut/blob/main/data/preview.png?raw=true" alt="Settings window">
    </th>
  </tr>
  <tr>
    <th>
      <samp><h3>Settings window</h3></samp>
    </th>
    <th>
      <samp><h3>Tray Icon</h3></samp>
    </th>
    <th>
      <samp><h3>Tray menu</h3></samp>
    </th>
  </tr>
  <tr>
    <th>
      <img src="https://github.com/elmoiv/elmocut/blob/main/data/preview-settings.png" alt="Settings window">
    </th>
    <th>
      <img src="https://github.com/elmoiv/elmocut/blob/main/data/preview-tray.png" alt="Tray icon">
    </th>
    <th>
      <img src="https://github.com/elmoiv/elmocut/blob/main/data/preview-tray-menu.png" alt="Tray icon menu">
    </th>
  </tr>
</table>

## Description
elmoCut aims to make arp spoofing easy for all users with all the hard work done under the hood.

One of it's main feauters is to use as low CPU and RAM usage as possible while offering nearly the same results as other closed source spoofers.

## Features
- Clean UI
- One click to block all devices.
- Re-kill devices that changed their ip during block.
- Remember killed devices before exit.
- Start with windows.
- Run minimized in the background.

## Limitations
- Can only search for 255 devices (255.255.255.0 subnet masks)
- Works only on default interface.
- Both scan types are manaul.

## Download
<a href="https://github.com/elmoiv/elmocut/releases/latest">
  <img src="https://github.com/elmoiv/elmocut/blob/main/data/download.png" alt="download elmoCut" width=50>
</a>

## Requirements
  - Npcap: [Download](https://nmap.org/npcap/dist/npcap-1.10.exe)
  - x64 Microsoft Windows >= 7
 
## Run
 - Install requirements via pip: `pip install -r requirements.txt`
 - Ensure that `pyuic5` is in PATH
 - Click on `RUN.bat`

## Build
 - **Required**:
    - PyInstaller: `pip install pyinstaller`
 - **Optionals**:
    - UPX: [Download](https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip)
    - Inno Setup: [Download](https://files.jrsoftware.org/is/6/innosetup-6.0.3.exe)

***Make sure that all of the above are in PATH in order to build elmoCut without issues***

Now run: `python build.py`

## Manual
<table>
  <tr>
    <th><samp>Button</samp></th>
    <th><samp>Description</samp></th>
    <th><samp>Notes</samp></th>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/scan_easy.png" alt="ARP Scan" width="80px"></td>
    <td><samp>Perform ARP Scan</samp></td>
    <td><samp>Fast but not all devices are detected</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/scan_hard.png" alt="Ping Scan" width="80px"></td>
    <td><samp>Perform Ping Scan</samp></td>
    <td><samp>Slower than ARP but all devices are detected</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/kill.png" alt="ARP Scan" width="80px"></td>
    <td><samp>Block the selected device from accessing internet</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/unkill.png" alt="ARP Scan" width="80px"></td>
    <td><samp>Allow the Blocked device to access internet</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/killall.png" alt="ARP Scan" width="80px"></td>
    <td><samp>Block all connected devices</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/unkillall.png" alt="ARP Scan" width="80px"></td>
    <td><samp>Allow all blocked devices</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/settings.png" alt="ARP Scan" width="80px"></td>
    <td><samp>View elmoCut settings window</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/about.png" alt="ARP Scan" width="80px"></td>
    <td><samp>view elmoCut about window</samp></td>
    <td><samp>-</samp></td>
  </tr>
</table>

## TODO
- [ ] Protect elmoCut user from other spoofers.
- [ ] Select between available interfaces.
- [ ] Control connected devices limit.
- [ ] Background live connection checker.
- [ ] Background live devices discovery.
- [ ] Extend scan for all subnet masks.

## Contribution
Please contribute! If you want to fix a bug, suggest improvements, or add new features to the project, just [open an issue](https://github.com/elmoiv/elmocut/issues) or send me a pull request.

## License
<img src="https://github.com/elmoiv/elmocut/blob/main/data/mit.png" width=100>
elmoCut is Free Software: You can use, study share and improve it at your will. Specifically you can redistribute and/or modify it under the terms of the MIT License as published by the Massachusetts Institute of Technology.
