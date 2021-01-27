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

## Screenshot
<p align=center>
  <img src="https://github.com/elmoiv/elmocut/blob/main/data/preview.png" alt="elmoCut icon">
</p>

## Description
elmoCut aims to make arp spoofing easy for all users with all the hard work done under the hood. One of it's main feauters is to use as low CPU and RAM usage as possible while offering nearly the same results as other closed source spoofers.

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

## Building from source

## Manual
<table>
  <tr>
    <td><samp>Button</samp></td>
    <td><samp>Description</samp></td>
    <td><samp>Notes</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/scan_easy.png?raw=true" alt="ARP Scan" width="80px"></td>
    <td><samp>Perform ARP Scan</samp></td>
    <td><samp>Fast but not all devices are detected</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/scan_hard.png?raw=true" alt="Ping Scan" width="80px"></td>
    <td><samp>Perform Ping Scan</samp></td>
    <td><samp>Slower than ARP but all devices are detected</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/kill.png?raw=true" alt="ARP Scan" width="80px"></td>
    <td><samp>Block the selected device from accessing internet</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/unkill.png?raw=true" alt="ARP Scan" width="80px"></td>
    <td><samp>Allow the Blocked device to access internet</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/killall.png?raw=true" alt="ARP Scan" width="80px"></td>
    <td><samp>Block all connected devices</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/unkillall.png?raw=true" alt="ARP Scan" width="80px"></td>
    <td><samp>Allow all blocked devices</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/settings.png?raw=true" alt="ARP Scan" width="80px"></td>
    <td><samp>View elmoCut settings window</samp></td>
    <td><samp>-</samp></td>
  </tr>
  <tr>
    <td><img src="https://github.com/elmoiv/elmocut/blob/main/assets/about.png?raw=true" alt="ARP Scan" width="80px"></td>
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
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/MIT_logo.svg/321px-MIT_logo.svg.png" width=100>
elmoCut is Free Software: You can use, study share and improve it at your will. Specifically you can redistribute and/or modify it under the terms of the MIT License as published by the Massachusetts Institute of Technology.
