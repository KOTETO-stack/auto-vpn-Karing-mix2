#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Amnezia Free Config Fetcher"""
import json

AMNEZIA_ENDPOINTS = [
    ("amnezia-jp-1.amnezia.net", 51820),
    ("amnezia-sg-1.amnezia.net", 51820),
    ("amnezia-de-1.amnezia.net", 51820),
    ("amnezia-nl-1.amnezia.net", 51820),
    ("amnezia-uk-1.amnezia.net", 51820),
]

def generate_template(host, port):
    return f"""[Interface]\nPrivateKey = ВСТАВЬ_ПРИВАТНЫЙ_КЛЮЧ\nAddress = 10.8.1.2/32\nDNS = 1.1.1.1, 8.8.8.8\nJc = 120\nJmin = 23\nJmax = 911\nS1 = 0\nS2 = 0\nH1 = 1\nH2 = 2\nH3 = 3\nH4 = 4\n\n[Peer]\nPublicKey = AmneziaFreePublicKeyPlaceholder\nAllowedIPs = 0.0.0.0/0\nEndpoint = {host}:{port}\nPersistentKeepalive = 25\n"""

def main():
    print("[+] Генерация Amnezia Free конфигов...")
    configs = []
    for host, port in AMNEZIA_ENDPOINTS:
        cfg = generate_template(host, port)
        fname = f"amnezia_{host.split('.')[0]}.conf"
        with open(f"configs/{fname}", "w", encoding="utf-8") as f:
            f.write(cfg)
        configs.append({"host": host, "port": port, "file": fname})
        print(f"    [+] {fname}")
    with open("configs/amnezia_meta.json", "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)
    print("[!] ВАЖНО: Замени ВСТАВЬ_ПРИВАТНЫЙ_КЛЮЧ на реальный из AmneziaVPN!")

if __name__ == "__main__":
    main()
