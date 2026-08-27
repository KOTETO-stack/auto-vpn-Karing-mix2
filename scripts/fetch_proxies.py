#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Public Proxy Fetcher - 100+ Sources"""
import re, json, base64, urllib.request, socket, time, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SOURCES = [
    "https://raw.githubusercontent.com/mheidari988/ProxyList/main/proxylist.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/VLESS.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/free_proxy_ss/v2ray",
    "https://raw.githubusercontent.com/Lonely233233/sub/main/v2ray",
    "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/v2raysub.txt",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/master/sub/share/all3",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg",
    "https://raw.githubusercontent.com/v2raydy/v2ray/main/subscribe/v2ray",
    "https://raw.githubusercontent.com/ZYFXZ/V2Ray/main/v2ray",
    "https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/2024-v2ray.txt",
    "https://raw.githubusercontent.com/codingbox/Free-Node-Merge/main/node.txt",
    "https://raw.githubusercontent.com/snakem982/proxypool/main/source/v2ray.txt",
    "https://raw.githubusercontent.com/misakaio/helloworld/master/subscribe/v2ray",
    "https://raw.githubusercontent.com/adiwzx/freenode/main/adispeed.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/ripaojiedian/freenode/main/sub",
    "https://raw.githubusercontent.com/mianfeifq/share/main/data/2026_v2ray.txt",
    "https://raw.githubusercontent.com/hkaa0/permalink/main/proxy/V2RAY",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription1",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription2",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription3",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription4",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription5",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yml",
    "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
    "https://raw.githubusercontent.com/moneyfly1/sublist/main/clash.yml",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.yml",
    "https://raw.githubusercontent.com/Lonely233233/sub/main/clash",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/clash/clash.provider.yaml",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.yml",
    "https://raw.githubusercontent.com/vpei/Free-Node-Merge/main/o/all.yaml",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/clash.yaml",
    "https://raw.githubusercontent.com/anaer/Sub/main/clash.yml",
    "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/clashsub.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/clash",
    "https://raw.githubusercontent.com/ripaojiedian/freenode/main/clash",
    "https://raw.githubusercontent.com/hkaa0/permalink/main/proxy/Clash",
    "https://raw.githubusercontent.com/mianfeifq/share/main/data/2026_clash.txt",
    "https://raw.githubusercontent.com/zyfxz/V2Ray/main/clash",
    "https://raw.githubusercontent.com/v2raydy/v2ray/main/subscribe/clash",
    "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/clash",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/master/sub/share/all4clash",
    "https://raw.githubusercontent.com/codingbox/Free-Node-Merge/main/clash.yml",
    "https://raw.githubusercontent.com/snakem982/proxypool/main/source/clash.yaml",
    "https://raw.githubusercontent.com/misakaio/helloworld/master/subscribe/clash",
    "https://raw.githubusercontent.com/adiwzx/freenode/main/adispeed.yaml",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Base64_Sub.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt",
    "https://raw.githubusercontent.com/mheidari988/ProxyList/main/proxylist.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/VLESS.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/free_proxy_ss/v2ray",
    "https://raw.githubusercontent.com/Lonely233233/sub/main/v2ray",
    "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/v2raysub.txt",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/master/sub/share/all3",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg",
    "https://raw.githubusercontent.com/v2raydy/v2ray/main/subscribe/v2ray",
    "https://raw.githubusercontent.com/ZYFXZ/V2Ray/main/v2ray",
    "https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/2024-v2ray.txt",
    "https://raw.githubusercontent.com/codingbox/Free-Node-Merge/main/node.txt",
    "https://raw.githubusercontent.com/snakem982/proxypool/main/source/v2ray.txt",
    "https://raw.githubusercontent.com/misakaio/helloworld/master/subscribe/v2ray",
    "https://raw.githubusercontent.com/adiwzx/freenode/main/adispeed.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/ripaojiedian/freenode/main/sub",
    "https://raw.githubusercontent.com/mianfeifq/share/main/data/2026_v2ray.txt",
    "https://raw.githubusercontent.com/hkaa0/permalink/main/proxy/V2RAY",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription6",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription7",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription8",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription9",
    "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription10",
]

SOURCES = list(dict.fromkeys(SOURCES))

COUNTRY_FLAGS = {
    "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪", "NL": "🇳🇱", "FR": "🇫🇷",
    "SG": "🇸🇬", "JP": "🇯🇵", "KR": "🇰🇷", "CA": "🇨🇦", "AU": "🇦🇺",
    "FI": "🇫🇮", "SE": "🇸🇪", "NO": "🇳🇴", "CH": "🇨🇭", "AT": "🇦🇹",
    "IT": "🇮🇹", "ES": "🇪🇸", "PL": "🇵🇱", "RO": "🇷🇴", "BG": "🇧🇬",
    "CZ": "🇨🇿", "HU": "🇭🇺", "TR": "🇹🇷", "IN": "🇮🇳", "BR": "🇧🇷",
    "MX": "🇲🇽", "AR": "🇦🇷", "ZA": "🇿🇦", "AE": "🇦🇪", "IL": "🇮🇱",
}

CITY_NAMES = {
    "US": "Нью-Йорк", "GB": "Лондон", "DE": "Франкфурт", "NL": "Амстердам",
    "FR": "Париж", "SG": "Сингапур", "JP": "Токио", "KR": "Сеул",
    "CA": "Торонто", "AU": "Сидней", "FI": "Хельсинки", "SE": "Стокгольм",
    "NO": "Осло", "CH": "Цюрих", "AT": "Вена", "IT": "Милан",
    "ES": "Мадрид", "PL": "Варшава", "RO": "Бухарест", "BG": "София",
    "CZ": "Прага", "HU": "Будапешт", "TR": "Стамбул", "IN": "Мумбаи",
    "BR": "Сан-Паулу", "MX": "Мехико", "AR": "Буэнос-Айрес", "ZA": "Йоханнесбург",
    "AE": "Дубай", "IL": "Тель-Авив",
}

BANNED = {"UA", "RU", "BY", "IR", "KP", "SY"}
BANNED_KW = ["ukraine", "ukrainian", "kyiv", "kiev", "moscow", "russia", "belarus", "minsk"]
ALLOWED = {"vless", "trojan", "hysteria2", "hy2", "vmess", "hysteria", "hy"}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "v2rayN/1.0"})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[!] {url}: {e}"); return ""

def b64decode(data):
    try: return base64.b64decode(data + "==").decode("utf-8", errors="ignore")
    except: return ""

def extract(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        dec = b64decode(line)
        if dec and "://" in dec:
            for s in dec.splitlines():
                s = s.strip()
                if "://" in s: out.append(s)
        elif "://" in line: out.append(line)
    return out

def get_country(ip):
    try:
        req = urllib.request.Request(f"https://ipapi.co/{ip}/json/", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
            d = json.loads(r.read().decode())
            return d.get("country_code", "UN"), d.get("city", "Unknown")
    except: return "UN", "Unknown"

def alive(ip, port, t=3):
    try:
        with socket.create_connection((ip, port), timeout=t): return True
    except: return False

def parse(url):
    try:
        proto = url.split("://")[0].lower()
        if proto not in ALLOWED: return None
        if proto in ("hysteria", "hy"): proto = "hysteria2"
        rest = url.split("://", 1)[1]
        if proto == "vmess":
            cfg = json.loads(b64decode(rest))
            ip = cfg.get("add", ""); port = int(cfg.get("port", 0))
            cc, city = get_country(ip)
            return {"protocol": "vmess", "ip": ip, "port": port, "country": cc, "city": city, "raw": url, "cfg": cfg}
        else:
            m = re.match(r"[^@]+@([^:]+):(\\d+).*", rest)
            if not m: return None
            ip, port = m.group(1), int(m.group(2))
            cc, city = get_country(ip)
            return {"protocol": proto, "ip": ip, "port": port, "country": cc, "city": city, "raw": url}
    except: return None

def ok(p):
    if not p: return False
    if p.get("country", "UN") in BANNED: return False
    raw = p.get("raw", "").lower(); ip = p.get("ip", "").lower()
    for kw in BANNED_KW:
        if kw in raw or kw in ip: return False
    return True

def name(p):
    cc = p.get("country", "UN")
    city = p.get("city", "Unknown")
    if city == "Unknown" or not city: city = CITY_NAMES.get(cc, "Unknown")
    return f"{COUNTRY_FLAGS.get(cc, '🏳️')}{cc} {city} | {p.get('protocol','vpn').upper()} | Макс скорость"

def build_outbounds(proxies):
    out = []
    for p in proxies[:150]:
        n = name(p); raw = p["raw"]
        if p["protocol"] == "vmess":
            cfg = p.get("cfg", {})
            out.append({
                "tag": n, "protocol": "vmess",
                "settings": {"vnext": [{"address": cfg.get("add",""), "port": int(cfg.get("port",443)),
                                        "users": [{"id": cfg.get("id",""), "alterId": int(cfg.get("aid",0)), "security": cfg.get("scy","auto")}]}]},
                "streamSettings": {"network": cfg.get("net","tcp"), "security": cfg.get("tls",""),
                                   "tlsSettings": {"serverName": cfg.get("sni", cfg.get("host",""))} if cfg.get("tls") else None}
            })
        else:
            out.append({"tag": n, "protocol": p["protocol"], "url": raw})
    return out

def main():
    all_raw = []
    for src in SOURCES:
        print(f"[+] {src}")
        text = fetch(src)
        if text:
            proxies = extract(text)
            print(f"    Найдено: {len(proxies)}")
            all_raw.extend(proxies)
        time.sleep(0.3)
    print(f"[+] Всего: {len(all_raw)}")
    parsed = []
    for raw in set(all_raw):
        p = parse(raw)
        if ok(p) and alive(p["ip"], p["port"]):
            p["alive"] = True; parsed.append(p)
            print(f"    [OK] {p['country']} {p['ip']}:{p['port']} ({p['protocol']})")
    parsed.sort(key=lambda x: x["country"])
    parsed = parsed[:150]
    with open("data/all_proxies.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    karing = {
        "outbounds": build_outbounds(parsed),
        "dns": {"servers": ["https://dns.adguard-dns.com/dns-query", "https://dns.google/dns-query"]},
        "routing": {"rules": [
            {"domain": ["geosite:category-ads-all"], "outbound": "block"},
            {"domain": ["youtube.com", "googlevideo.com"], "outbound": "direct"},
            {"ip": ["geoip:private"], "outbound": "direct"}
        ]}
    }
    with open("configs/karing_sub.json", "w", encoding="utf-8") as f:
        json.dump(karing, f, ensure_ascii=False, indent=2)
    with open("configs/BLACK_VLESS_RUS_mobile.txt", "w", encoding="utf-8") as f:
        for p in parsed: f.write(p["raw"] + "\n")
    print(f"[+] Готово! {len(parsed)} прокси сохранено.")

if __name__ == "__main__":
    main()
