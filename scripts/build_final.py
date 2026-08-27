#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final Config Builder"""
import json, os, base64

def load(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def main():
    print("[+] Сборка финального конфига...")
    karing = load("configs/karing_sub.json") or {"outbounds": [], "dns": {}, "routing": {}}
    
    warp = load("configs/warp_outbound.json")
    if warp:
        karing["outbounds"].insert(0, warp)
        print("[+] WARP+ добавлен")
    
    amnezia = load("configs/amnezia_meta.json")
    if amnezia:
        for srv in amnezia:
            karing["outbounds"].append({
                "tag": f"🔒 Amnezia {srv['host']}",
                "protocol": "wireguard",
                "settings": {
                    "secretKey": "PLACEHOLDER_PRIVATE_KEY",
                    "address": ["10.8.1.2/32"],
                    "peers": [{"publicKey": "AmneziaFreePublicKeyPlaceholder",
                               "allowedIPs": ["0.0.0.0/0"],
                               "endpoint": f"{srv['host']}:{srv['port']}",
                               "keepAlive": 25}],
                    "mtu": 1280
                }
            })
        print("[+] Amnezia добавлена")
    
    karing["dns"] = {
        "servers": ["https://dns.adguard-dns.com/dns-query", "https://dns.google/dns-query"],
        "hosts": {"dns.adguard-dns.com": "94.140.14.14", "dns.google": "8.8.8.8"}
    }
    karing["routing"] = {
        "domainStrategy": "IPIfNonMatch",
        "rules": [
            {"type": "field", "domain": ["geosite:category-ads-all"], "outboundTag": "block"},
            {"type": "field", "domain": ["geosite:google", "geosite:youtube", "domain:googlevideo.com", "domain:ytimg.com"], "outboundTag": "🛡️ WARP+ Защита"},
            {"type": "field", "domain": ["domain:openai.com", "domain:chatgpt.com", "domain:anthropic.com", "domain:claude.ai"], "outboundTag": "🛡️ WARP+ Защита"},
            {"type": "field", "domain": ["domain:t.me", "domain:telegram.org", "domain:telesco.pe"], "outboundTag": "🇸🇬SG Сингапур | TROJAN | Макс скорость"},
            {"type": "field", "domain": ["domain:tiktok.com", "domain:tiktokv.com", "domain:tiktokcdn.com"], "outboundTag": "🇺🇸US Нью-Йорк | VMESS | Макс скорость"},
            {"type": "field", "domain": ["domain:wechat.com", "domain:whatsapp.net", "domain:whatsapp.com"], "outboundTag": "🇸🇬SG Сингапур | TROJAN | Макс скорость"},
            {"type": "field", "ip": ["geoip:private", "geoip:cn"], "outboundTag": "direct"}
        ]
    }
    
    with open("configs/FINAL_KARING.json", "w", encoding="utf-8") as f:
        json.dump(karing, f, ensure_ascii=False, indent=2)
    
    b64 = base64.b64encode(json.dumps(karing).encode()).decode()
    with open("configs/FINAL_KARING.txt", "w", encoding="utf-8") as f:
        f.write(b64)
    
    print("[+] Финальный конфиг: configs/FINAL_KARING.json")
    print("[+] Base64 подписка: configs/FINAL_KARING.txt")

if __name__ == "__main__":
    main()
