import argparse
import sys
import time
import requests
from scapy.all import ARP, Ether, srp
import concurrent.futures

def print_banner():
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                   v11.0 MILITARY GRADE - LOCAL LAN NET-REAPER
    """)

def get_vendor(mac_address):
    """Mendeteksi Merek Perangkat dari MAC Address API"""
    try:
        url = f"https://api.macvendors.com/{mac_address}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.text
        return "Unknown Device (Mungkin fitur Private MAC / Acak diaktifkan)"
    except:
        return "Unknown (Timeout)"

def scan_network(ip_range):
    print_banner()
    print(f"[*] Mengaktifkan Sonar ARP ke target subnet: {ip_range}")
    print(f"[*] Memindai perangkat... (Mohon tunggu)\n")
    print("-" * 80)
    print(f"{'IP ADDRESS':<18} | {'MAC ADDRESS':<20} | {'VENDOR / PERANGKAT'}")
    print("-" * 80)

    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    try:
        answered_list = srp(arp_request_broadcast, timeout=3, verbose=False)[0]
    except PermissionError:
        print("[-] FATAL ERROR: Wajib dijalankan dengan akses Administrator!")
        sys.exit(1)
    except Exception as e:
        print(f"[-] ERROR Npcap: {e}")
        sys.exit(1)

    # Mengekstrak daftar perangkat
    devices = [{"ip": el[1].psrc, "mac": el[1].hwsrc} for el in answered_list]

    # Mode Mengendap-endap (Sequential dengan jeda 1 detik agar tidak diblokir API)
    for dev in devices:
        try:
            url = f"https://api.macvendors.com/{dev['mac']}"
            resp = requests.get(url, timeout=5)
            
            if resp.status_code == 200:
                vendor = resp.text
            elif resp.status_code == 429:
                vendor = "API Rate-Limited (Tunggu sebentar)"
            else:
                vendor = "Private MAC (Disamarkan)"
        except:
            vendor = "Koneksi API Gagal"
            
        print(f"{dev['ip']:<18} | {dev['mac']:<20} | {vendor}")
        time.sleep(1) # Kunci utama agar tidak diblokir server MacVendors

    print("-" * 80)
    print(f"[*] Sapuan selesai. Ditemukan {len(devices)} perangkat yang terhubung.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ghost Net-Reaper - Local LAN Watchdog")
    parser.add_argument("-t", "--target", help="Target Subnet (contoh: 192.168.1.0/24)", required=True)
    args = parser.parse_args()
    
    scan_network(args.target)