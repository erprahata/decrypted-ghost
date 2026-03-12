import socket
import argparse
import sys
import concurrent.futures
from datetime import datetime

# Dictionary untuk menebak layanan (service) berdasarkan port standar
COMMON_SERVICES = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    111: "RPCBIND", 135: "MSRPC", 139: "NETBIOS-SSN", 143: "IMAP",
    443: "HTTPS", 445: "MICROSOFT-DS (SMB)", 993: "IMAPS", 995: "POP3S",
    1723: "PPTP", 3306: "MYSQL", 3389: "RDP", 5900: "VNC",
    8080: "HTTP-PROXY", 8443: "HTTPS-ALT"
}

def print_banner():
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                             v3.0 OVERKILL - Asynchronous Port Scanner
    """)

def scan_port(ip, port):
    """
    Fungsi worker: Mencoba melakukan TCP Connect ke satu port spesifik.
    """
    try:
        # AF_INET = IPv4, SOCK_STREAM = TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Timeout super singkat (0.5 detik) agar scanning sangat cepat
        sock.settimeout(0.5) 
        
        # connect_ex mengembalikan 0 jika berhasil konek (port terbuka)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            service = COMMON_SERVICES.get(port, "UNKNOWN")
            print(f"[+] OPEN PORT : {port:<5} | SERVICE: {service}")
            return port
            
    except KeyboardInterrupt:
        sys.exit(0)
    except socket.gaierror:
        pass # Abaikan error resolusi hostname di level thread
    except socket.error:
        pass # Abaikan error socket lainnya (seperti koneksi ditolak)
        
    return None

def start_engine(target, start_port, end_port, threads):
    print_banner()
    
    # Resolusi Domain ke IP Address
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"[-] FATAL ERROR: Hostname '{target}' tidak dapat di-resolve (pastikan domain aktif).")
        sys.exit(1)

    print("-" * 65)
    print(f"[*] Target IP      : {target_ip} ({target})")
    print(f"[*] Port Range     : {start_port} - {end_port}")
    print(f"[*] Threads Engine : {threads} concurrent workers")
    print(f"[*] Scan Started   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 65)
    print("[*] Initiating Layer 4 TCP Connect Scan...\n")

    open_ports = []
    ports_to_scan = range(start_port, end_port + 1)

    try:
        # Menghidupkan mesin Multithreading
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            # Memetakan fungsi scan_port ke seluruh port target
            futures = {executor.submit(scan_port, target_ip, port): port for port in ports_to_scan}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
                    
    except KeyboardInterrupt:
        print("\n[!] User Abort Detected. Shutting down threads...")
        sys.exit(0)

    print("\n" + "=" * 65)
    print(f"[*] Scan Completed : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] Total Open     : {len(open_ports)} ports found.")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decrypted Ghost v3.0 - Overkill Port Scanner")
    parser.add_argument("-u", "--url", help="Target Domain atau IP Address (contoh: erprahata.my.id atau 192.168.1.1)", required=True)
    parser.add_argument("-s", "--start", help="Starting Port (Default: 1)", type=int, default=1)
    parser.add_argument("-e", "--end", help="Ending Port (Default: 1024)", type=int, default=1024)
    parser.add_argument("-t", "--threads", help="Jumlah Threads (Default: 100)", type=int, default=100)
    
    # Hapus prefix 'http://' atau 'https://' jika user tidak sengaja memasukkannya
    args = parser.parse_args()
    target_clean = args.url.replace("http://", "").replace("https://", "").split('/')[0]
    
    start_engine(target_clean, args.start, args.end, args.threads)