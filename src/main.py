import asyncio
import aiohttp
import aiofiles
import json
import base64
import os
import re
import time
import hashlib  # <-- ДОБАВЛЕН
import socket
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import unquote
from cryptography.fernet import Fernet

from dns_security import DNSLeakProtection


@dataclass
class Server:
    protocol: str
    tag: str
    host: str
    port: int
    uuid: Optional[str] = None
    password: Optional[str] = None
    sni: Optional[str] = None
    flow: Optional[str] = None
    ping_ms: float = float('inf')
    working: bool = False


AMNEZIA_FREE_B64 = "vpn://AAAA_3icXY3LDoIwEEV_hXStJhhjojsjERN0AbowbkgtAzZA2_QBQcO_2xbduJrMPXfmvBHDLaBtgHYtgxfFwUECoFmAClBEUqEpZ_84IJwxIB7Zpt1KWuUdSDWVlzbEguYTsMEbKZAdJZDrQXgbnt7Ny6_tx4XkmhPe-E5fOWQss68M03Kws_D30qDRWYx-5gXW2Eucs4bB8Yg2qyTM-sUjO16u9SmKUxOt92VI6js_dzyNsz7cqOSGxvEDmaFXJg=="

WARP_PRIVATE_KEY = os.getenv("WARP_PRIVATE_KEY", "")
WARP_RESERVED = os.getenv("WARP_RESERVED", "0,0,0")
SUB_PASSWORD = os.getenv("SUB_PASSWORD", "karing-secure-2026-key-32!!")

SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/ripaojiedian/freenode/main/sub",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/free",
    "https://raw.githubusercontent.com/wrfree/free/main/v2",
    "https://raw.githubusercontent.com/anaer/Sub/main/sub.txt",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt",
    "https://raw.githubusercontent.com/adiwzx/freenode/main/adispeed.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
]

COUNTRY_MAP = {
    "de": ("DE", "Germany", "Frankfurt"),
    "nl": ("NL", "Netherlands", "Amsterdam"),
    "sg": ("SG", "Singapore", "Singapore"),
    "us": ("US", "USA", "New York"),
    "fi": ("FI", "Finland", "Helsinki"),
    "jp": ("JP", "Japan", "Tokyo"),
    "kr": ("KR", "South Korea", "Seoul"),
    "gb": ("GB", "UK", "London"),
    "fr": ("FR", "France", "Paris"),
    "ca": ("CA", "Canada", "Toronto"),
    "au": ("AU", "Australia", "Sydney"),
    "pl": ("PL", "Poland", "Warsaw"),
    "ua": ("UA", "Ukraine", "Kyiv"),
    "tr": ("TR", "Turkey", "Istanbul"),
    "kz": ("KZ", "Kazakhstan", "Almaty"),
    "ch": ("CH", "Switzerland", "Zurich"),
    "se": ("SE", "Sweden", "Stockholm"),
    "no": ("NO", "Norway", "Oslo"),
    "dk": ("DK", "Denmark", "Copenhagen"),
    "at": ("AT", "Austria", "Vienna"),
    "cz": ("CZ", "Czechia", "Prague"),
    "ro": ("RO", "Romania", "Bucharest"),
    "bg": ("BG", "Bulgaria", "Sofia"),
    "hu": ("HU", "Hungary", "Budapest"),
    "ie": ("IE", "Ireland", "Dublin"),
    "pt": ("PT", "Portugal", "Lisbon"),
    "es": ("ES", "Spain", "Madrid"),
    "it": ("IT", "Italy", "Milan"),
    "lu": ("LU", "Luxembourg", "Luxembourg"),
    "be": ("BE", "Belgium", "Brussels"),
    "is": ("IS", "Iceland", "Reykjavik"),
    "ee": ("EE", "Estonia", "Tallinn"),
    "lv": ("LV", "Latvia", "Riga"),
    "lt": ("LT", "Lithuania", "Vilnius"),
    "md": ("MD", "Moldova", "Chisinau"),
    "ge": ("GE", "Georgia", "Tbilisi"),
    "am": ("AM", "Armenia", "Yerevan"),
    "az": ("AZ", "Azerbaijan", "Baku"),
    "uz": ("UZ", "Uzbekistan", "Tashkent"),
    "tj": ("TJ", "Tajikistan", "Dushanbe"),
    "kg": ("KG", "Kyrgyzstan", "Bishkek"),
    "tm": ("TM", "Turkmenistan", "Ashgabat"),
    "in": ("IN", "India", "Mumbai"),
    "vn": ("VN", "Vietnam", "Hanoi"),
    "th": ("TH", "Thailand", "Bangkok"),
    "my": ("MY", "Malaysia", "Kuala Lumpur"),
    "id": ("ID", "Indonesia", "Jakarta"),
    "ph": ("PH", "Philippines", "Manila"),
    "tw": ("TW", "Taiwan", "Taipei"),
    "hk": ("HK", "Hong Kong", "Hong Kong"),
}


def get_country_info(host: str):
    try:
        ip = socket.gethostbyname(host)
        first = int(ip.split(".")[0])
        if first in [5, 77, 87, 93, 95, 128, 178, 185, 213]:
            return "RU", "Russia", "Moscow"
    except:
        pass
    domain = host.lower().split(".")[-1] if "." in host else ""
    if domain in COUNTRY_MAP:
        return COUNTRY_MAP[domain]
    h = host.lower()
    for code, info in COUNTRY_MAP.items():
        if code in h:
            return info
    return "OT", "Other", "Unknown"


def parse_vless(url: str):
    m = re.match(r'vless://([^@]+)@([^:]+):(\d+)\?([^#]*)#(.+)', url)
    if not m:
        return None
    uuid, host, port, params, remark = m.groups()
    p = dict(x.split("=") for x in params.split("&") if "=" in x)
    code, country, city = get_country_info(host)
    return Server(
        protocol="vless", tag=f"[{code}] {country} {city}",
        host=host, port=int(port), uuid=uuid,
        sni=p.get("sni"), flow=p.get("flow", "xtls-rprx-vision")
    )


def parse_trojan(url: str):
    m = re.match(r'trojan://([^@]+)@([^:]+):(\d+)\?([^#]*)#(.+)', url)
    if not m:
        return None
    pwd, host, port, params, remark = m.groups()
    p = dict(x.split("=") for x in params.split("&") if "=" in p)
    code, country, city = get_country_info(host)
    return Server(
        protocol="trojan", tag=f"[{code}] {country} {city}",
        host=host, port=int(port), password=unquote(pwd),
        sni=p.get("sni")
    )


def parse_hysteria2(url: str):
    m = re.match(r'hysteria2://([^@]+)@([^:]+):(\d+)\?([^#]*)#(.+)', url)
    if not m:
        m = re.match(r'hysteria2://([^@]+)@([^:]+):(\d+)#(.+)', url)
        if not m:
            return None
        pwd, host, port, remark = m.groups()
        p = {}
    else:
        pwd, host, port, params, remark = m.groups()
        p = dict(x.split("=") for x in params.split("&") if "=" in p)
    code, country, city = get_country_info(host)
    return Server(
        protocol="hysteria2", tag=f"[{code}] {country} {city}",
        host=host, port=int(port), password=unquote(pwd),
        sni=p.get("sni")
    )


async def fetch_source(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            text = await resp.text()
            servers = []
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("vless://"):
                    s = parse_vless(line)
                elif line.startswith("trojan://"):
                    s = parse_trojan(line)
                elif line.startswith("hysteria2://"):
                    s = parse_hysteria2(line)
                else:
                    continue
                if s:
                    servers.append(s)
            return servers
    except Exception as e:
        print(f"  X {url.split('/')[-1][:40]:<40} | error")
        return []


async def ping_test(server: Server):
    try:
        start = time.time()
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(server.host, server.port), timeout=5)
        writer.close()
        await writer.wait_closed()
        return (time.time() - start) * 1000
    except:
        return float('inf')


async def check_servers(servers: List[Server]):
    print(f"Checking {len(servers)} servers...")
    pings = await asyncio.gather(*[ping_test(s) for s in servers])
    for s, ping in zip(servers, pings):
        s.ping_ms = ping
        s.working = ping < 1000
    working = [s for s in servers if s.working]
    working.sort(key=lambda x: x.ping_ms)
    return working[:150]


def build_config(servers: List[Server]):
    dns_prot = DNSLeakProtection()
    proxy_tag = servers[0].tag if servers else "Proxy"
    
    outbounds = []
    
    # WARP+ protection
    if WARP_PRIVATE_KEY and "YOUR_WARP" not in WARP_PRIVATE_KEY:
        reserved = [int(x) for x in WARP_RESERVED.split(",")]
        outbounds.append({
            "type": "wireguard",
            "tag": "Warp+ Protection",
            "server": "engage.cloudflareclient.com",
            "server_port": 2408,
            "local_address": ["172.16.0.2/32", "2606:4700:110:8a36:df92:8a0:3b6c:a/128"],
            "private_key": WARP_PRIVATE_KEY,
            "peer_public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=",
            "reserved": reserved,
            "mtu": 1280
        })
    
    # AmneziaFree
    try:
        data = AMNEZIA_FREE_B64.replace("vpn://", "")
        cfg = json.loads(base64.b64decode(data + "==").decode("utf-8", errors="ignore"))
        outbounds.append({
            "type": cfg.get("protocol", "amneziawg"),
            "tag": "AmneziaFree Backup",
            **{k: v for k, v in cfg.items() if k != "protocol"}
        })
    except:
        outbounds.append({
            "type": "shadowsocks",
            "tag": "AmneziaFree Backup",
            "server": "127.0.0.1", "server_port": 443,
            "method": "aes-256-gcm", "password": "placeholder"
        })
    
    # VPN servers
    for s in servers:
        if s.protocol == "vless":
            outbounds.append({
                "type": "vless", "tag": s.tag,
                "server": s.host, "server_port": s.port,
                "uuid": s.uuid, "flow": s.flow or "xtls-rprx-vision",
                "tls": {
                    "enabled": True, "server_name": s.sni or s.host,
                    "utls": {"enabled": True, "fingerprint": "chrome"},
                    "reality": {"enabled": False}
                }
            })
        elif s.protocol == "trojan":
            outbounds.append({
                "type": "trojan", "tag": s.tag,
                "server": s.host, "server_port": s.port,
                "password": s.password,
                "tls": {"enabled": True, "server_name": s.sni or s.host}
            })
        elif s.protocol == "hysteria2":
            outbounds.append({
                "type": "hysteria2", "tag": s.tag,
                "server": s.host, "server_port": s.port,
                "password": s.password,
                "tls": {"enabled": True, "server_name": s.sni or s.host}
            })
    
    outbounds += [
        {"type": "direct", "tag": "Direct"},
        {"type": "block", "tag": "Block"},
        {"type": "dns", "tag": "dns-out"}
    ]
    
    return {
        "log": {"level": "warn"},
        "dns": dns_prot.build_dns_config(proxy_tag),
        "inbounds": [
            {"type": "mixed", "tag": "mixed-in", "listen": "127.0.0.1", "listen_port": 2080},
            dns_prot.get_tun_config()
        ],
        "outbounds": outbounds,
        "route": {
            "rules": dns_prot.build_route_rules(proxy_tag),
            "final": proxy_tag,
            "auto_detect_interface": True,
            "override_android_vpn": True
        }
    }


def encrypt(data: str, pwd: str) -> str:
    key = base64.urlsafe_b64encode(hashlib.sha256(pwd.encode()).digest()[:32])
    return base64.urlsafe_b64encode(Fernet(key).encrypt(data.encode())).decode()


async def main():
    print(f"[{time.strftime('%H:%M:%S')}] Starting update...")
    
    async with aiohttp.ClientSession() as session:
        all_srv = []
        for url in SOURCES:
            srv = await fetch_source(session, url)
            all_srv.extend(srv)
            print(f"  + {url.split('/')[-1][:40]:<40} | {len(srv)} servers")
        
        seen = set()
        unique = []
        for s in all_srv:
            k = f"{s.host}:{s.port}"
            if k not in seen:
                seen.add(k)
                unique.append(s)
        
        working = await check_servers(unique)
        print(f"Working (top-150): {len(working)}")
        
        cfg = build_config(working)
        js = json.dumps(cfg, indent=2, ensure_ascii=False)
        
        os.makedirs("output", exist_ok=True)
        
        async with aiofiles.open("output/subscription.json", "w", encoding="utf-8") as f:
            await f.write(js)
        
        async with aiofiles.open("output/subscription.enc", "w") as f:
            await f.write(encrypt(js, SUB_PASSWORD))
        
        info = {
            "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(working),
            "servers": [{"tag": s.tag, "host": s.host, "port": s.port, "ping": round(s.ping_ms, 1), "protocol": s.protocol} for s in working]
        }
        async with aiofiles.open("output/info.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(info, indent=2, ensure_ascii=False))
        
        print(f"[{time.strftime('%H:%M:%S')}] Done! Saved to output/")
        print(f"  Password: {SUB_PASSWORD[:12]}...")


if __name__ == "__main__":
    asyncio.run(main())
