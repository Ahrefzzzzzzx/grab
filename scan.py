import requests
from concurrent.futures import ThreadPoolExecutor
import threading

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

lock = threading.Lock()  # agar thread aman saat menulis ke file

def is_wordpress(domain, scheme="http"):
    try:
        url = f"{scheme}://{domain}/wp-login.php"
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        content = r.text.lower()
        if (
            'wordpress' in content or
            '/wp-content/' in content or
            'meta name="generator" content="wordpress' in content
        ):
            print(f"[✔] WordPress ditemukan: {domain} ({scheme.upper()})")
            return True
    except:
        pass
    return False

def scan_domain(domain):
    domain = domain.strip()
    if not domain:
        return

    for scheme in ['http', 'https']:
        try:
            test_url = f"{scheme}://{domain}"
            r = requests.get(test_url, headers=headers, timeout=15)
            if r.status_code in [200, 301, 302]:
                if is_wordpress(domain, scheme):
                    with lock:
                        with open("wordpress_found.txt", "a") as f:
                            f.write(domain + "\n")
                    return
        except:
            continue

    # jika gagal konek atau bukan WP
    with lock:
        with open("gagal_scan.txt", "a") as f:
            f.write(domain + "\n")

def main():
    input_file = input("Masukkan nama file domain (misal all_domains.txt): ").strip()
    if not input_file:
        input_file = "all_domains.txt"

    try:
        with open(input_file, "r") as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File '{input_file}' tidak ditemukan.")
        return

    print(f"[~] Total domain yang akan discan: {len(domains)}")
    print("[⚙] Mulai scan...")

    with open("wordpress_found.txt", "w") as f:
        f.write("")  # kosongkan file hasil lama

    with open("gagal_scan.txt", "w") as f:
        f.write("")  # kosongkan file gagal lama

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(scan_domain, domains)

    print("[✓] Selesai scan!")
    print("[📄] WordPress ditemukan disimpan di: wordpress_found.txt")
    print("[📄] Domain gagal konek / bukan WordPress disimpan di: gagal_scan.txt")

if __name__ == "__main__":
    main()
