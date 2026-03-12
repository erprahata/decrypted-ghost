import os
import subprocess
import sys

# === SIHIR WARNA (ANSI ESCAPE CODES) ===
class C:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    # Mengaktifkan dukungan ANSI di Windows CMD/PowerShell secara paksa
    if os.name == 'nt':
        os.system('') 

def print_master_banner():
    # Banner utama kita buat warna Hijau Terang dan Bold
    print(C.BOLD + C.GREEN + r"""
    ██████╗ ███████╗ ██████╗██████╗ ██╗   ██╗██████╗ ████████╗███████╗██████╗ 
    ██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
    ██║  ██║█████╗  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   █████╗  ██║  ██║
    ██║  ██║██╔══╝  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔══╝  ██║  ██║
    ██████╔╝███████╗╚██████╗██║  ██║   ██║   ██║        ██║   ███████╗██████╔╝
    ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚══════╝╚═════╝ 
        """ + C.CYAN + "--- GHOST TOOLKIT: THE ULTIMATE COMMAND CENTER v4.5 ---" + C.RESET)

def show_pentest_guide():
    clear_screen()
    print_master_banner()
    print(C.MAGENTA + "=" * 70)
    print(" 🎯 THE GHOST METHODOLOGY: RECOMMENDED WORKFLOW")
    print("=" * 70 + C.RESET)
    print(C.CYAN + "  [1] PASSIVE RECON " + C.WHITE + ": Baca perlindungan WAF dan Security Headers.")
    print(C.CYAN + "  [2] ORIGIN UNMASK " + C.WHITE + ": Cari subdomain bocor untuk temukan IP Asli.")
    print(C.CYAN + "  [3] INFRA SCAN    " + C.WHITE + ": Scan IP Asli untuk cari Port terbuka (L4).")
    print(C.CYAN + "  [4] PATH DISCOVERY" + C.WHITE + ": Fuzzing direktori cari file sensitif (/.env).")
    print(C.CYAN + "  [5] EXPLOITATION  " + C.WHITE + ": Tembak payload XSS & SQLi ke parameter target.")
    print(C.CYAN + "  [6] OSINT MODULE  " + C.WHITE + ": Lacak target (Username, HP, EXIF, IP, Archive).")
    print(C.CYAN + "  [7] LAN SWEEPER   " + C.WHITE + ": Petakan topologi fisik jaringan WiFi lokal.")
    print(C.CYAN + "  [8] AES CRYPTOR   " + C.WHITE + ": Kunci/Buka file rahasia dengan enkripsi militer.")
    print(C.MAGENTA + "=" * 70 + C.RESET)
    input(C.YELLOW + "\n[Tekan Enter untuk kembali ke Menu Utama...]" + C.RESET)

def execute_tool(command):
    print(C.BOLD + C.BLUE + f"\n[*] Executing: {command}" + C.RESET)
    print(C.BLUE + "-" * 60 + C.RESET)
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print(C.RED + "\n[!] Eksekusi dibatalkan oleh user." + C.RESET)
    print(C.BLUE + "-" * 60 + C.RESET)
    input(C.YELLOW + "\n[Eksekusi Selesai. Tekan Enter untuk kembali...]" + C.RESET)

def main_menu():
    while True:
        clear_screen()
        print_master_banner()
        print(C.WHITE + " [" + C.CYAN + "1" + C.WHITE + "] Tactical Reconnaissance Module (ghost_recon.py)")
        print(" [" + C.CYAN + "2" + C.WHITE + "] Layer 4 Port Scanner         (ghost_port.py)")
        print(" [" + C.CYAN + "3" + C.WHITE + "] Stealth Subdomain Enumerator (ghost_sub.py)")
        print(" [" + C.CYAN + "4" + C.WHITE + "] Active Directory Fuzzer      (ghost_dir.py)")
        print(" [" + C.RED + "5" + C.WHITE + "] Active Vulnerability Injector(ghost_inject.py) " + C.RED + "[DANGER]" + C.WHITE)
        print(" [" + C.MAGENTA + "6" + C.WHITE + "] OSINT & SOCMINT Harvester    (ghost_osint.py)")
        print(" [" + C.CYAN + "7" + C.WHITE + "] Local LAN Net-Reaper         (ghost_net.py)")
        print(" [" + C.YELLOW + "8" + C.WHITE + "] AES Data Vault Cryptor       (ghost_crypt.py)")
        print(C.BLUE + " --------------------------------------------------" + C.RESET)
        print(C.WHITE + " [" + C.GREEN + "G" + C.WHITE + "] Tampilkan Panduan Eksekusi (Pentest Guide)")
        print(" [" + C.RED + "0" + C.WHITE + "] Keluar / Exit Program")
        print(C.BLUE + "==================================================" + C.RESET)
        
        # Prompt input dengan warna kuning agar mencolok
        choice = input(C.BOLD + C.GREEN + " Ghost-CMD> " + C.YELLOW + "Masukkan pilihan (0-8 / G): " + C.RESET).strip().upper()

        if choice == '1':
            target = input(C.CYAN + " [>] Masukkan Target URL (contoh: target.com): " + C.RESET)
            if target: execute_tool(f"python ghost_recon.py -u {target}")
            
        elif choice == '2':
            target = input(C.CYAN + " [>] Masukkan IP/Domain (contoh: 192.168.1.1): " + C.RESET)
            threads = input(" [>] Jumlah Threads (Enter untuk default 100): " + C.RESET)
            cmd = f"python ghost_port.py -u {target}"
            if threads: cmd += f" -t {threads}"
            if target: execute_tool(cmd)
            
        elif choice == '3':
            target = input(C.CYAN + " [>] Masukkan Target Domain (contoh: target.com): " + C.RESET)
            wordlist = input(" [>] File Wordlist (Enter default 'subdomain.txt'): " + C.RESET) or "subdomain.txt"
            threads = input(" [>] Jumlah Threads (Enter untuk default 50): " + C.RESET)
            cmd = f"python ghost_sub.py -u {target} -w {wordlist}"
            if threads: cmd += f" -t {threads}"
            if target: execute_tool(cmd)
            
        elif choice == '4':
            target = input(C.CYAN + " [>] Masukkan Target URL (contoh: http://target.com/): " + C.RESET)
            wordlist = input(" [>] File Wordlist (Enter default 'wordlist.txt'): " + C.RESET) or "wordlist.txt"
            threads = input(" [>] Jumlah Threads (Enter untuk default 20): " + C.RESET)
            exts = input(" [>] Ekstensi tambahan? (opsional, contoh: php,zip): " + C.RESET)
            cmd = f"python ghost_dir.py -u {target} -w {wordlist}"
            if threads: cmd += f" -t {threads}"
            if exts: cmd += f" -e {exts}"
            if target: execute_tool(cmd)
            
        elif choice == '5':
            print(C.RED + " [*] PERHATIAN: Pastikan URL memiliki parameter (?id=1) atau gunakan kata FUZZ" + C.RESET)
            target = input(C.CYAN + " [>] Target URL (contoh: target.com/?q=1): " + C.RESET)
            threads = input(" [>] Jumlah Threads (Enter untuk default 10): " + C.RESET)
            cmd = f"python ghost_inject.py -u \"{target}\""
            if threads: cmd += f" -t {threads}"
            if target: execute_tool(cmd)
            
        elif choice == '6':
            print(C.MAGENTA + "\n [*] Memasuki Sub-Sistem OSINT & SOCMINT..." + C.RESET)
            execute_tool("python ghost_osint.py")
            
        elif choice == '7':
            print(C.RED + "\n [*] WAJIB DIJALANKAN SEBAGAI ADMINISTRATOR!" + C.RESET)
            target = input(C.CYAN + " [>] Masukkan Target Subnet (contoh: 192.168.1.0/24): " + C.RESET)
            if target: execute_tool(f"python ghost_net.py -t {target}")
            
        elif choice == '8':
            target = input(C.YELLOW + "\n [>] File/Folder Target: ")
            password = input(" [>] Password Rahasia: ")
            mode = input(" [>] Mode (encrypt/decrypt): " + C.RESET).strip().lower()
            if target and password and mode in ['encrypt', 'decrypt']:
                execute_tool(f"python ghost_crypt.py -t \"{target}\" -p \"{password}\" -m {mode}")
            else:
                print(C.RED + " [-] Input tidak lengkap atau mode salah!" + C.RESET)
                
        elif choice == 'G':
            show_pentest_guide()
            
        elif choice == '0':
            clear_screen()
            print(C.RED + "[*] Decrypted Ghost Toolkit dihentikan. Mematikan seluruh radar..." + C.RESET)
            sys.exit(0)
            
        else:
            print(C.RED + "[-] Pilihan tidak valid." + C.RESET)
            import time
            time.sleep(1)

if __name__ == "__main__":
    main_menu()