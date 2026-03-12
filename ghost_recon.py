import requests
import argparse

# Constants for security and disclosure headers
SECURITY_HEADERS = [
    'Strict-Transport-Security',
    'Content-Security-Policy',
    'X-Content-Type-Options',
    'X-Frame-Options',
    'X-XSS-Protection',
    'Referrer-Policy'
]

DISCLOSURE_HEADERS = [
    'server', 
    'x-powered-by', 
    'x-aspnet-version', 
    'x-generator'
]

def print_banner():
    # Menambahkan huruf 'r' (Raw String) untuk menghilangkan SyntaxWarning
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                             v4.0 - Tactical Reconnaissance Module
    """)

def analyze_target(target_url):
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url

    print(f"[*] Analyzing Target: {target_url}\n")

    # Dictionary untuk menyimpan temuan, akan digunakan oleh fitur 'Playbook'
    findings = {
        'leaks': [],
        'missing_headers': [],
        'cors_vuln': False,
        'insecure_cookies': []
    }

    try:
        response = requests.get(target_url, timeout=5)
        headers_lower = {key.lower(): value for key, value in response.headers.items()}
        
        # 1. Information Disclosure
        print("[+] 1. Information Disclosure Analysis:")
        print("-" * 55)
        for leak in DISCLOSURE_HEADERS:
            if leak in headers_lower:
                print(f"    [!] WARNING: Target leaks {leak.upper()} -> {headers_lower[leak]}")
                findings['leaks'].append(f"{leak.upper()} ({headers_lower[leak]})")
        if not findings['leaks']:
            print("    [V] SECURE: No obvious backend technology leaks detected.")

        # 2. Security Headers
        print("\n[+] 2. Security Headers Audit:")
        print("-" * 55)
        for sec_header in SECURITY_HEADERS:
            if sec_header.lower() in headers_lower:
                print(f"    [V] FOUND   : {sec_header}")
            else:
                print(f"    [X] MISSING : {sec_header}")
                findings['missing_headers'].append(sec_header)

        # 3. CORS Audit
        print("\n[+] 3. Cross-Origin Resource Sharing (CORS) Audit:")
        print("-" * 55)
        acao = headers_lower.get('access-control-allow-origin')
        if acao:
            if acao == '*':
                print("    [!] CRITICAL: CORS explicitly allows all origins (*).")
                findings['cors_vuln'] = True
            else:
                print(f"    [i] INFO: CORS allowed origin restricted to: {acao}")
        else:
            print("    [V] SECURE: No overly permissive CORS header found.")

        # 4. Cookie Audit
        print("\n[+] 4. Cookie Security Audit:")
        print("-" * 55)
        if response.cookies:
            for cookie in response.cookies:
                weaknesses = []
                if not cookie.secure:
                    weaknesses.append("Missing 'Secure'")
                if not cookie.has_nonstandard_attr('HttpOnly'):
                    weaknesses.append("Missing 'HttpOnly'")
                
                if weaknesses:
                    print(f"    [!] WARNING: Cookie '{cookie.name}' -> {', '.join(weaknesses)}")
                    findings['insecure_cookies'].append(cookie.name)
                else:
                    print(f"    [V] SECURE: Cookie '{cookie.name}' is properly configured.")
        else:
            print("    [i] INFO: No cookies set by the server on this response.")
                
        # 5. THE PENTESTER'S PLAYBOOK (Rekomendasi Taktis)
        print("\n" + "=" * 55)
        print("[*] 🎯 PENTESTER'S PLAYBOOK (RECOMMENDED NEXT STEPS):")
        print("=" * 55)
        
        if findings['leaks']:
            print("    -> [RECON] Search for CVEs (exploits) specifically for:")
            for leak in findings['leaks']:
                print(f"       - {leak}")
                
        if 'X-Frame-Options' in findings['missing_headers'] and 'Content-Security-Policy' in findings['missing_headers']:
            print("    -> [ATTACK] Target is vulnerable to Clickjacking. Craft an HTML iframe payload.")
            
        if 'X-XSS-Protection' in findings['missing_headers'] or 'Content-Security-Policy' in findings['missing_headers']:
            print("    -> [ATTACK] High probability of XSS. Test input fields with payload: <script>alert(1)</script>")
            
        if findings['cors_vuln']:
            print("    -> [ATTACK] CORS Misconfiguration! Create a malicious HTML page using Fetch/XHR to steal API data.")
            
        if findings['insecure_cookies']:
            print("    -> [ATTACK] Session Hijacking risk! Exploit XSS to steal cookies via document.cookie, or use packet sniffing (MitM).")

        # Jika semuanya aman
        if not any([findings['leaks'], findings['missing_headers'], findings['cors_vuln'], findings['insecure_cookies']]):
            print("    -> [INFO] Defense-in-Depth is strong here. Move to heavy artillery:")
            print("       1. Directory Brute-forcing (look for hidden admin panels).")
            print("       2. Parameter Fuzzing (look for SQL Injection).")
            print("       3. Business Logic Abuse.")
            
    except requests.exceptions.Timeout:
        print("[-] Error: Target did not respond (Timeout).")
    except requests.exceptions.ConnectionError:
        print("[-] Error: Connection failed. Ensure the URL is valid and the server is up.")
    except Exception as e:
        print(f"[-] Unexpected Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Decrypted Ghost - Advanced Web Reconnaissance Tool",
        epilog="Example usage: python ghost_recon.py -u example.com"
    )
    parser.add_argument("-u", "--url", help="Target URL to scan", required=True)
    args = parser.parse_args()
    
    print_banner()
    analyze_target(args.url)