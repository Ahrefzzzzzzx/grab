import requests
import json
import time
import threading

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

tld_list = [
    'com', 'org', 'net', 'info', 'biz', 'name', 'pro', 'xyz', 'top', 'online',
    'site', 'club', 'store', 'blog', 'app', 'dev', 'shop', 'tech', 'web', 'fun',
    'io', 'ai', 'me', 'cloud', 'digital', 'design', 'agency', 'media',

    'id', 'my', 'co', 'us', 'uk', 'au', 'ca', 'de', 'fr', 'es', 'it', 'jp',
    'kr', 'cn', 'sg', 'in', 'br', 'ru', 'za', 'ng', 'ke', 'tz', 'gh', 'vn',
    'ph', 'th', 'pk', 'bd', 'ir', 'sa', 'ae', 'qa', 'kw', 'om', 'lk', 'np',
    'mm', 'kh', 'la', 'mn', 'nz', 'tw', 'hk', 'mu', 'ug', 'zw', 'zm', 'mw',
    'sn', 'dz', 'tn', 'ma', 'cm', 'et', 'ao', 'sd', 'ly', 'eg',

    'ac.id', 'co.id', 'net.id', 'or.id', 'web.id', 'sch.id', 'go.id', 'mil.id', 'ponpes.id'
]

lock = threading.Lock()  # untuk akses file aman jika multithread

def get_domains_from_crtsh(tld, retries=3):
    print(f"[+] Ambil domain dari crt.sh untuk TLD: {tld}")
    url = f"https://crt.sh/?q=%25.{tld}&output=json"
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=70)
            if r.status_code != 200:
                print(f"[!] Response status {r.status_code} dari crt.sh untuk TLD {tld}")
                time.sleep(3)
                continue
            if not r.text.strip():
                print(f"[!] Response crt.sh kosong untuk TLD {tld}")
                time.sleep(3)
                continue
            data = json.loads(r.text)
            domains = set()
            for entry in data:
                name_value = entry.get('name_value', '')
                for d in name_value.split('\n'):
                    if tld in d:
                        domains.add(d.strip().lower())
            return domains
        except Exception as e:
            print(f"[!] Gagal ambil data crt.sh (attempt {attempt}) untuk TLD {tld}: {e}")
            time.sleep(3)
    return set()

def write_domains_realtime(domains, filename="all_domains.txt"):
    with lock:
        with open(filename, "a") as f:
            for domain in domains:
                f.write(domain + "\n")

def main():
    # hapus file dulu supaya gak append ke data lama
    open("all_domains.txt", "w").close()

    all_domains = set()

    for tld in tld_list:
        domains = get_domains_from_crtsh(tld)
        new_domains = domains - all_domains
        if new_domains:
            write_domains_realtime(new_domains)
            all_domains.update(new_domains)
            print(f"[+] {len(new_domains)} domain baru disimpan dari TLD {tld}")
        else:
            print(f"[+] Tidak ada domain baru dari TLD {tld}")
        time.sleep(2)

    print(f"[✓] Total domain unik terkumpul: {len(all_domains)}")
    print("[✓] Semua domain sudah disimpan di all_domains.txt secara realtime")

if __name__ == "__main__":
    main()
