import requests
import argparse
import sys
import concurrent.futures
import random
from urllib.parse import urlparse

# List of realistic User-Agents to bypass basic WAFs
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
]

def print_banner():
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                        v2.0 OVERKILL - Asynchronous Directory Fuzzer
    """)

def check_url(url, output_file):
    """
    Worker function to check a single URL. This will be executed by multiple threads.
    """
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    try:
        # We don't need to download the full page body, just the headers to get the status code.
        # This makes the tool INSANELY fast. (Using stream=True)
        response = requests.get(url, headers=headers, timeout=5, stream=True)
        status = response.status_code
        
        result_string = ""
        if status == 200:
            result_string = f"[+] 200 OK        : {url}"
        elif status == 403:
            result_string = f"[!] 403 FORBIDDEN : {url} (Hidden/Protected)"
        elif status in [301, 302]:
            redirect_to = response.headers.get('Location', 'Unknown')
            result_string = f"[>] {status} REDIRECT  : {url} -> {redirect_to}"
        elif status == 500:
            result_string = f"[*] 500 ERROR     : {url} (Potential Server-Side Bug)"
            
        # If we found something interesting, print it and save it
        if result_string:
            print(result_string)
            if output_file:
                with open(output_file, 'a') as f:
                    f.write(result_string + "\n")
                    
    except requests.exceptions.RequestException:
        pass # Silently ignore timeouts/connection errors for clean output

def build_wordlist(wordlist_path, extensions):
    """
    Reads the wordlist and appends extensions if provided.
    """
    try:
        with open(wordlist_path, 'r') as file:
            base_words = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[-] FATAL ERROR: Wordlist '{wordlist_path}' not found!")
        sys.exit(1)

    final_wordlist = []
    for word in base_words:
        final_wordlist.append(word) # Add the base word (e.g., 'admin')
        if extensions:
            for ext in extensions.split(','):
                ext = ext.strip()
                if not ext.startswith('.'):
                    ext = '.' + ext
                final_wordlist.append(f"{word}{ext}") # Add extended word (e.g., 'admin.php')
                
    return final_wordlist

def start_fuzzing(target_url, wordlist_path, threads, extensions, output_file):
    if not target_url.endswith('/'):
        target_url += '/'
    if not target_url.startswith('http'):
        target_url = 'http://' + target_url

    print(f"[*] Target         : {target_url}")
    print(f"[*] Wordlist       : {wordlist_path}")
    print(f"[*] Threads Engine : {threads} concurrent workers")
    if extensions:
        print(f"[*] Extensions     : {extensions}")
    if output_file:
        print(f"[*] Output File    : {output_file}")
        # Clear the output file if it exists
        open(output_file, 'w').close() 

    # 1. Build the attack payload
    payloads = build_wordlist(wordlist_path, extensions)
    urls_to_check = [target_url + word for word in payloads]
    total_requests = len(urls_to_check)

    print(f"[*] Total Payloads : {total_requests} requests generated.")
    print("[*] Launching Overkill Engine... (Press Ctrl+C to abort)\n")
    print("=" * 65)

    # 2. Ignite the Multithreading Engine
    try:
        # ThreadPoolExecutor is the secret sauce for speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            # We map the check_url function to our list of URLs
            futures = [executor.submit(check_url, url, output_file) for url in urls_to_check]
            
            # Wait for all threads to complete
            concurrent.futures.wait(futures)
            
    except KeyboardInterrupt:
        print("\n[!] User Abort Detected. Shutting down threads gracefully...")
        # Executor will automatically clean up
        sys.exit(0)
        
    print("=" * 65)
    print("[*] Scan Completed Successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decrypted Ghost v2.0 - Overkill Directory Fuzzer")
    parser.add_argument("-u", "--url", help="Target URL", required=True)
    parser.add_argument("-w", "--wordlist", help="Path to wordlist file", required=True)
    parser.add_argument("-t", "--threads", help="Number of concurrent threads (Default: 10)", type=int, default=10)
    parser.add_argument("-e", "--extensions", help="Comma-separated extensions to append (e.g., php,html,bak,zip)", default=None)
    parser.add_argument("-o", "--output", help="File to save the findings", default=None)
    
    args = parser.parse_args()
    
    print_banner()
    start_fuzzing(args.url, args.wordlist, args.threads, args.extensions, args.output)