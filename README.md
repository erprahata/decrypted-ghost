# 👻 Decrypted Ghost Toolkit
**v4.5 Ultimate Command Center - Cyberpunk Edition**

Decrypted Ghost Toolkit is a powerful, multi-layered cybersecurity framework designed for penetration testing, network reconnaissance, and Open-Source Intelligence (OSINT). Built entirely in Python, it features an asynchronous multithreading engine for high-speed execution and an interactive, colorized CLI menu.

---

## 🎯 Arsenal / Features

The toolkit is divided into 8 primary military-grade modules:

1. **Passive Reconnaissance:** Analyzes WAF (Cloudflare) and missing Security Headers.
2. **Layer 4 Port Scanner:** High-speed asynchronous TCP connect scan for infrastructure profiling.
3. **Stealth Subdomain Enumerator:** DNS-based origin unmasking using custom wordlists.
4. **Active Directory Fuzzer:** Multithreaded hidden path discovery (`/.env`, `/admin`, `/backup.zip`).
5. **Active Vulnerability Injector:** Fuzzes URL parameters (Query & RESTful Paths) with XSS and SQLi payloads, featuring a built-in heuristic analysis engine.
6. **OSINT & SOCMINT Harvester:** * Tracks usernames across platforms (bypassing Meta & TikTok WAFs via dorking).
   * Extracts EXIF metadata and translates raw GPS to Google Maps coordinates.
   * Traces IP & Domain Geolocation physically.
   * Validates phone numbers and generates pivoting intelligence links.
   * Recovers dead websites via Wayback Machine Archiving.
7. **Local LAN Net-Reaper:** Sweeps local WiFi networks to map physical topologies (IP, MAC, and Vendor detection via ARP).
8. **AES Data Vault Cryptor:** Secures personal files/folders using military-grade AES-256 encryption & PBKDF2HMAC key derivation.

---

## 🛠️ Installation & Setup

Ensure you have **Python 3.8+** installed on your system. 

**1. Clone the repository:**
```bash
git clone https://github.com/erprahata/decrypted-ghost.git
cd decrypted-ghost
```

**2. Install the required dependencies:**
```bash
pip install requests scapy cryptography pillow phonenumbers
```
> **Note for Windows Users:** To run the Local LAN Net-Reaper (Module 7), you must have [Npcap](https://npcap.com/#download) installed with *"WinPcap API-compatible Mode"* enabled.

**3. Prepare your Wordlists:**
Ensure you have `wordlist.txt` (for directory fuzzing) and `subdomain.txt` (for subdomain enumeration) in the root directory.

---

## 🚀 Usage

Launch the interactive Master Console to access all modules:

```bash
python decrypted_ghost.py
```
Follow the on-screen colorful prompts to navigate through the toolkit.

---

## ⚠️ Legal Disclaimer

> **EDUCATIONAL PURPOSES ONLY.**
>
> This toolkit is developed strictly for educational purposes, ethical hacking, and authorized security auditing. The creator is NOT responsible for any misuse, damage, or illegal activities caused by this tool. By using Decrypted Ghost Toolkit, you agree to use it only on systems, networks, and applications where you have explicit permission to test.