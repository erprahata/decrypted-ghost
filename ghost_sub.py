import socket
import argparse
import sys
import concurrent.futures
import time

def print_banner():
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                        v1.0 STEALTH - Asynchronous Subdomain Enumerator
    """)

def check_subdomain(subdomain, target_domain, output_file):
    """
    Fungsi worker: Menyelesaikan DNS untuk melihat apakah subdomain memiliki IP.
    """
    # Menggabungkan subdomain dengan domain utama (contoh: dev + . + target.com)
    full_domain = f"{subdomain}.{target_domain}"
    
    try:
        # Menanyakan ke DNS Resolver alamat IP dari domain tersebut
        ip_address = socket.gethostbyname(full_domain)
        
        result_string = f"[+] FOUND : {full_domain:<30} | IP: {ip_address}"
        print(result_string)
        
        if output_file:
            with open(output_file, 'a') as f:
                f.write(result_string + "\n")
                
        return full_domain, ip_address
        
    except socket.gaierror:
        # Jika DNS gagal resolve (domain tidak ada), lewati secara diam-diam
        return None
    except KeyboardInterrupt:
        sys.exit(0)

def start_enum(target_domain, wordlist_path, threads, output_file):
    print_banner()
    
    # Membersihkan input user (menghilangkan http:// atau www.)
    target_clean = target_domain.replace("http://", "").replace("https://", "").replace("www.", "").split('/')[0]

    try:
        with open(wordlist_path, 'r') as file:
            subdomains = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[-] FATAL ERROR: Wordlist '{wordlist_path}' tidak ditemukan!")
        sys.exit(1)

    print("-" * 65)
    print(f"[*] Target Domain  : {target_clean}")
    print(f"[*] Wordlist       : {wordlist_path} ({len(subdomains)} payloads)")
    print(f"[*] Threads Engine : {threads} concurrent workers")
    if output_file:
        print(f"[*] Output File    : {output_file}")
        open(output_file, 'w').close() 
    print("-" * 65)
    print("[*] Initiating Stealth DNS Resolution... (Press Ctrl+C to abort)\n")

    start_time = time.time()
    found_subdomains = []

    try:
        # Menyalakan mesin pemburu berkecepatan tinggi
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            # Memetakan fungsi
            futures = [executor.submit(check_subdomain, sub, target_clean, output_file) for sub in subdomains]
            
            # KODE YANG DIPERBAIKI: Mengambil hasil (result) dari setiap thread yang sudah selesai
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result: # Jika result tidak None (artinya subdomain ditemukan)
                    found_subdomains.append(result)
            
    except KeyboardInterrupt:
        print("\n[!] User Abort Detected. Shutting down threads gracefully...")
        sys.exit(0)

    end_time = time.time()
    
    print("\n" + "=" * 65)
    print(f"[*] Enumeration Completed in {round(end_time - start_time, 2)} seconds.")
    print(f"[*] Total Subdomains Found : {len(found_subdomains)}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decrypted Ghost v1.0 - Subdomain Enumerator")
    parser.add_argument("-u", "--url", help="Target Domain (contoh: target.com)", required=True)
    parser.add_argument("-w", "--wordlist", help="Path ke file wordlist", required=True)
    parser.add_argument("-t", "--threads", help="Jumlah Threads (Default: 50)", type=int, default=50)
    parser.add_argument("-o", "--output", help="File untuk menyimpan hasil", default=None)
    
    args = parser.parse_args()
    start_enum(args.url, args.wordlist, args.threads, args.output)