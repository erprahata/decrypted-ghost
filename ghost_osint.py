import os
import requests
import argparse
import sys
import concurrent.futures
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
except ImportError:
    print("[-] FATAL ERROR: Library 'phonenumbers' belum di-install.")
    print("[-] Jalankan perintah: pip install phonenumbers")
    sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                   v10.0 MAXIMUM GRADE - FULL OSINT & SOCMINT SUITE
    """)

# ==========================================
# MODULE 1: USERNAME TRACKER
# ==========================================
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Twitter/X": "https://nitter.net/{}", 
    "Instagram": "https://www.picuki.com/profile/{}", # Menggunakan OSINT Proxy agar tidak diblokir Meta
    "TikTok": "https://urlebird.com/user/{}/", # Menggunakan OSINT Proxy untuk Bypass WAF TikTok
    "Spotify": "http://googleusercontent.com/spotify.com/5{}",
    "Blogger": "https://{}.blogspot.com",
    "WordPress": "https://{}.wordpress.com",
    "Patreon": "https://www.patreon.com/{}"
}

def check_username(platform, url_template, username):
    url = url_template.format(username)
    # Menyamar sebagai browser Chrome modern
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=6)
        # Khusus beberapa situs, 200 OK adalah tanda valid
        if response.status_code == 200:
            return f"[+] {platform:<12} : {url}"
    except requests.exceptions.RequestException:
        pass
    return None

def hunt_username(username, threads=20):
    print(f"\n[*] Menjalankan Sherlock Engine untuk username: '{username}'")
    print(f"[*] Melacak di platform standar... (Mohon tunggu)\n")
    print("-" * 65)
    
    found = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_username, plat, url, username) for plat, url in PLATFORMS.items()]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(result)
                found += 1
                
    print("-" * 65)
    print(f"[*] 1. AUTOMATED SCAN: Target '{username}' terdeteksi di {found} platform.")
    
    # === FITUR BARU: GOOGLE DORK PIVOTING ===
    print("\n[+] 2. DEEP SEARCH (GOOGLE DORKS) UNTUK PLATFORM SULIT:")
    print("    Platform seperti Instagram, TikTok, dan LinkedIn memiliki WAF Anti-Bot kelas berat.")
    print("    Gunakan link di bawah ini untuk memaksa Google mencari profil tersebut:")
    print(f"    [>] Instagram : https://www.google.com/search?q=site:instagram.com+\"{username}\"")
    print(f"    [>] TikTok    : https://www.google.com/search?q=site:tiktok.com+\"{username}\"")
    print(f"    [>] LinkedIn  : https://www.google.com/search?q=site:linkedin.com/in/+\"{username}\"")
    print(f"    [>] Facebook  : https://www.google.com/search?q=site:facebook.com+\"{username}\"")
    print("-" * 65)

# ==========================================
# MODULE 2: EXIF FORENSICS
# ==========================================
def parse_exif_rational(val):
    if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
        if val.denominator == 0: return 0.0
        return float(val.numerator) / float(val.denominator)
    elif isinstance(val, tuple) or isinstance(val, list):
        if val[1] == 0: return 0.0
        return float(val[0]) / float(val[1])
    else:
        return float(val)

def get_decimal_from_dms(dms, ref):
    try:
        degrees = parse_exif_rational(dms[0])
        minutes = parse_exif_rational(dms[1])
        seconds = parse_exif_rational(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if isinstance(ref, bytes):
            ref = ref.decode('utf-8', errors='ignore')
        if str(ref).upper() in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return 0.0

def get_exif_data(image_path):
    print(f"\n[*] Memulai Ekstraksi Forensik pada file: '{image_path}'\n")
    print("-" * 65)
    try:
        image = Image.open(image_path)
        exif_raw = image._getexif()
        if not exif_raw:
            print("[-] AMAN: Tidak ada metadata EXIF tersembunyi di gambar ini.")
            return

        exif_data = {TAGS.get(k, k): v for k, v in exif_raw.items()}

        print("[+] METADATA PERANGKAT & WAKTU:")
        for tag in ['Make', 'Model', 'Software', 'DateTimeOriginal']:
            if tag in exif_data: print(f"    > {tag:<20} : {exif_data[tag]}")

        if 'GPSInfo' in exif_data:
            print("\n[!!!] CRITICAL: TITIK KOORDINAT SATELIT (GPS) DITEMUKAN!")
            gps_info = {GPSTAGS.get(k, k): v for k, v in exif_data['GPSInfo'].items()}
            lat_dms = gps_info.get('GPSLatitude')
            lat_ref = gps_info.get('GPSLatitudeRef', 'N')
            lon_dms = gps_info.get('GPSLongitude')
            lon_ref = gps_info.get('GPSLongitudeRef', 'E')

            if lat_dms and lon_dms:
                lat_dec = get_decimal_from_dms(lat_dms, lat_ref)
                lon_dec = get_decimal_from_dms(lon_dms, lon_ref)
                if lat_dec == 0.0 and lon_dec == 0.0:
                    print("    [-] File memiliki tag GPS, tetapi datanya kosong (0/0).")
                else:
                    print(f"    > Latitude  : {lat_dec}\n    > Longitude : {lon_dec}")
                    print(f"    > Google Maps : http://googleusercontent.com/maps.google.com/6{lat_dec},{lon_dec}")
        else:
            print("\n[-] Aman: Tidak ada tag GPSInfo di gambar ini.")
    except Exception as e:
        print(f"[-] ERROR: Eksekusi gagal. ({e})")
    print("-" * 65)

# ==========================================
# MODULE 3: IP / DOMAIN GEOLOCATION
# ==========================================
def track_ip(target):
    print(f"\n[*] Melacak Geolocation untuk: '{target}'\n")
    print("-" * 65)
    target_clean = target.replace("http://", "").replace("https://", "").split('/')[0]
    try:
        response = requests.get(f"http://ip-api.com/json/{target_clean}", timeout=5).json()
        if response['status'] == 'success':
            print("[+] LOKASI SERVER / TARGET DITEMUKAN:")
            print(f"    > IP Address   : {response['query']}")
            print(f"    > ISP / Host   : {response['isp']} ({response['org']})")
            print(f"    > Location     : {response['city']}, {response['country']}")
            print(f"    > Google Maps  : http://googleusercontent.com/maps.google.com/7{response['lat']},{response['lon']}")
        else:
            print(f"[-] Gagal melacak IP: {response.get('message', 'Unknown Error')}")
    except Exception as e:
        print(f"[-] ERROR saat menghubungi API pelacak: {e}")
    print("-" * 65)

# ==========================================
# MODULE 4: PHONE NUMBER OSINT
# ==========================================
def track_phone(phone_number):
    print(f"\n[*] Menganalisis Nomor Telepon: '{phone_number}'\n")
    print("-" * 65)
    if not phone_number.startswith('+'):
        phone_number = "+" + phone_number

    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        is_valid = phonenumbers.is_valid_number(parsed_number)
        
        print("[+] 1. ANALISIS REGISTRASI & JARINGAN:")
        print(f"    > Format Internasional : {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
        print(f"    > Status Validitas     : {'VALID (Aktif)' if is_valid else 'TIDAK VALID'}")
        
        if is_valid:
            region = geocoder.description_for_number(parsed_number, "id")
            telecom = carrier.name_for_number(parsed_number, "id")
            print(f"    > Wilayah/Negara       : {region if region else 'Tidak Diketahui'}")
            print(f"    > Provider / Operator  : {telecom if telecom else 'Tidak Terdeteksi (VoIP)'}")
            
            pure_number = str(parsed_number.country_code) + str(parsed_number.national_number)
            print("\n[+] 2. OSINT PIVOTING (TAUTAN PELACAKAN LANJUTAN):")
            print(f"    [>] Cek Profil WhatsApp   : https://wa.me/{pure_number}")
            print(f"    [>] Cek Profil Telegram   : https://t.me/+{pure_number}")
            print(f"    [>] Database Truecaller   : https://www.truecaller.com/search/global/{pure_number}")
            print(f"    [>] Google Dork (Jejak)   : https://www.google.com/search?q=\"%2B{pure_number}\"+OR+\"{pure_number}\"")

    except phonenumbers.phonenumberutil.NumberParseException as e:
        print(f"[-] ERROR: Format nomor tidak dikenali. ({e})")
        
    print("-" * 65)

# ==========================================
# MODULE 5: WAYBACK MACHINE (ARCHIVE TRACKER)
# ==========================================
def track_archive(url):
    print(f"\n[*] Menghubungi Mesin Waktu Internet (Wayback Machine) untuk: '{url}'\n")
    print("-" * 65)
    
    if not url.startswith('http'):
        url = 'http://' + url
        
    api_url = f"http://archive.org/wayback/available?url={url}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10).json()
        
        if 'archived_snapshots' in response and 'closest' in response['archived_snapshots']:
            data = response['archived_snapshots']['closest']
            print("[+] JEJAK SEJARAH DITEMUKAN!")
            print(f"    > Status Arsip     : TERSEDIA")
            print(f"    > Tanggal Snapshot : {data['timestamp'][:4]}-{data['timestamp'][4:6]}-{data['timestamp'][6:8]}")
            print(f"    > Link Arsip Web   : {data['url']}")
            print("\n    [!] Buka link di atas untuk melihat tampilan website di masa lalu meskipun sekarang sudah dihapus.")
        else:
            print("[-] Jejak Sejarah Kosong: Belum ada arsip untuk domain/URL ini di Wayback Machine.")
            
    except Exception as e:
        print(f"[-] ERROR saat menghubungi server arsip: {e}")
    print("-" * 65)

# ==========================================
# INTERACTIVE COMMAND MENU
# ==========================================
def main_menu():
    while True:
        clear_screen()
        print_banner()
        print(" [1] SOCMINT Username Tracker (Melacak Jejak IG, TikTok, Steam, dll)")
        print(" [2] EXIF Image Forensics     (Mengekstrak Metadata & GPS Foto)")
        print(" [3] IP & Domain Geolocation  (Melacak Lokasi Fisik Server/IP)")
        print(" [4] Phone Number OSINT       (Melacak Provider & Tautan Identitas)")
        print(" [5] Wayback Archive Tracker  (Melacak Sejarah URL yang Dihapus)")
        print(" --------------------------------------------------")
        print(" [0] Keluar ke Terminal")
        print("==================================================")
        
        choice = input(" Ghost-OSINT> Masukkan pilihan (0-5): ").strip()

        if choice == '1':
            target = input("\n [>] Masukkan Username (contoh: DecryptedGhost): ").strip()
            if target: hunt_username(target)
        elif choice == '2':
            target = input("\n [>] Nama file foto (contoh: target.jpg): ").strip()
            if target: get_exif_data(target)
        elif choice == '3':
            target = input("\n [>] Masukkan IP / Domain (contoh: target.com): ").strip()
            if target: track_ip(target)
        elif choice == '4':
            target = input("\n [>] Masukkan Nomor HP (contoh: +628123456789): ").strip()
            if target: track_phone(target)
        elif choice == '5':
            print("\n [*] Fitur ini sangat berguna untuk melihat isi website/postingan yang sudah di-take down.")
            target = input(" [>] Masukkan URL/Domain (contoh: target.com/page): ").strip()
            if target: track_archive(target)
        elif choice == '0':
            print("[*] OSINT Module dimatikan. Keluar dari radar...")
            sys.exit(0)
        else:
            print("[-] Pilihan tidak valid.")
            
        input("\n[Eksekusi Selesai. Tekan Enter untuk kembali ke Menu...]")

if __name__ == "__main__":
    main_menu()