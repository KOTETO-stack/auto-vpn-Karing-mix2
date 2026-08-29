import asyncio
import aiohttp
import socket
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class DNSLeakTest:
    is_leaking: bool
    dns_servers: List[str]
    issues: List[str]


class DNSLeakProtection:
    """DNS leak protection - all queries through tunnel"""
    
    SECURE_DNS = [
        {"tag": "cloudflare-doh", "address": "https://1.1.1.1/dns-query", "detour": "proxy"},
        {"tag": "cloudflare-dot", "address": "tls://1.1.1.1", "detour": "proxy"},
        {"tag": "quad9-doh", "address": "https://9.9.9.9/dns-query", "detour": "proxy"},
    ]
    
    LOCAL_DNS = [
        {"tag": "yandex-dns", "address": "77.88.8.8", "detour": "direct"},
        {"tag": "local-fallback", "address": "223.5.5.5", "detour": "direct"},
    ]
    
    RU_DOMAINS = {
        ".ru", ".xn--p1ai", ".su", ".moscow", ".spb",
        "yandex", "vk", "ok", "mail", "sberbank",
        "avito", "wildberries", "ozon", "gosuslugi",
        "tinkoff", "alfa", "vtb", "gazprombank",
        "rutube", "kinopoisk",
        "2gis", "cian", "domclick", "hh", "habr",
    }
    
    BLOCKED_SERVICES = {
        "youtube", "googlevideo", "ytimg", "youtu",
        "twitter", "x.com", "instagram", "facebook",
        "tiktok", "telegram", "t.me", "discord",
        "netflix", "spotify", "medium", "linkedin",
        "bbc", "dw", "rferl", "meduza", "dozhd",
        "whatsapp", "signal", "viber", "line",
    }

    def build_dns_config(self, proxy_tag: str = "Proxy") -> Dict:
        servers = []
        
        for dns in self.SECURE_DNS:
            servers.append({
                "tag": dns["tag"],
                "address": dns["address"],
                "detour": proxy_tag,
                "strategy": "prefer_ipv4"
            })
        
        for dns in self.LOCAL_DNS:
            servers.append({
                "tag": dns["tag"],
                "address": dns["address"],
                "detour": "Direct",
                "strategy": "prefer_ipv4"
            })
        
        servers.append({
            "tag": "fakeip",
            "address": "fakeip",
            "inet4_range": "198.18.0.0/15"
        })
        
        rules = [
            {"rule_set": "blocked-services", "server": "cloudflare-doh"},
            {"rule_set": "russian-domains", "server": "yandex-dns"},
            {"outbound": "Direct", "server": "yandex-dns"},
            {"outbound": proxy_tag, "server": "cloudflare-doh"},
        ]
        
        return {
            "servers": servers,
            "rules": rules,
            "final": "cloudflare-doh",
            "independent_cache": True,
            "reverse_mapping": True,
            "fakeip": {
                "enabled": True,
                "inet4_range": "198.18.0.0/15",
                "inet6_range": "fc00::/18"
            }
        }

    def build_route_rules(self, proxy_tag: str = "Proxy") -> List[Dict]:
        return [
            {"protocol": "dns", "outbound": "dns-out"},
            
            {"domain_keyword": ["googleads","googlesyndication","doubleclick","adsystem","advertising","analytics"], "outbound": "Block"},
            {"domain_suffix": ["googlesyndication.com","googleadservices.com","doubleclick.net","facebook.com/tr","google-analytics.com"], "outbound": "Block"},
            
            {"domain_suffix": ["youtube.com","youtu.be","googlevideo.com","ytimg.com","youtubei.googleapis.com"], "outbound": proxy_tag},
            {"domain_suffix": ["tiktok.com","tiktokcdn.com","musical.ly"], "outbound": proxy_tag},
            {"domain_suffix": ["telegram.org","t.me","tdesktop.com","telega.one"], "outbound": proxy_tag},
            {"ip_cidr": ["149.154.160.0/20","91.108.4.0/22","91.108.8.0/22","91.108.12.0/22","91.108.16.0/22","91.108.20.0/22","91.108.56.0/22","95.161.64.0/20"], "outbound": proxy_tag},
            
            {"domain_suffix": ["instagram.com","cdninstagram.com","fbcdn.net","facebook.com","twitter.com","x.com","twimg.com"], "outbound": proxy_tag},
            {"domain_suffix": ["discord.com","discordapp.com","discord.gg"], "outbound": proxy_tag},
            
            {"domain_suffix": ["whatsapp.com","whatsapp.net","signal.org","signal.me","viber.com","line.me","wechat.com","weixin.qq.com"], "outbound": proxy_tag},
            {"domain_keyword": ["bip"], "outbound": proxy_tag},
            
            {"domain_suffix": ["netflix.com","nflxvideo.net","spotify.com","hulu.com","disneyplus.com","hbomax.com"], "outbound": proxy_tag},
            {"domain_suffix": ["openai.com","chatgpt.com","anthropic.com","claude.ai"], "outbound": proxy_tag},
            {"domain_suffix": ["github.com","githubassets.com","githubusercontent.com"], "outbound": proxy_tag},
            {"domain_suffix": ["google.com","googleapis.com","gstatic.com","googleusercontent.com"], "outbound": proxy_tag},
            
            {"domain_suffix": [".ru",".xn--p1ai",".su"], "outbound": "Direct"},
            {"domain": ["vk.com","vk.ru","ok.ru","yandex.ru","ya.ru","yandex.net","mail.ru","avito.ru","wildberries.ru","ozon.ru","gosuslugi.ru","sberbank.ru","tinkoff.ru","alfa.ru","vtb.ru"], "outbound": "Direct"},
            
            {"ip_is_private": True, "outbound": "Direct"},
            {"outbound": proxy_tag}
        ]

    async def test_dns_leak(self, proxy_url: str = None) -> DNSLeakTest:
        dns_servers = set()
        issues = []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": "Mozilla/5.0"}
                
                if proxy_url:
                    async with session.get("https://dnsleaktest.com/api/servers", proxy=proxy_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        data = await resp.json()
                        dns_servers = {s["ip"] for s in data.get("servers", [])}
                else:
                    async with session.get("https://dnsleaktest.com/api/servers", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        data = await resp.json()
                        dns_servers = {s["ip"] for s in data.get("servers", [])}
            
            ru_dns = {"77.88.8.8", "77.88.8.1", "94.198.55.1", "94.198.55.2"}
            provider_dns = {"192.168.", "10.", "172.16."}
            
            is_leaking = False
            for dns in dns_servers:
                if any(str(dns).startswith(p) for p in provider_dns):
                    issues.append(f"Provider DNS detected: {dns}")
                    is_leaking = True
                if dns in ru_dns:
                    issues.append(f"Russian DNS detected: {dns}")
            
            if not dns_servers:
                issues.append("Could not detect DNS servers")
                
        except Exception as e:
            issues.append(f"Test error: {e}")
            is_leaking = True
        
        return DNSLeakTest(is_leaking=is_leaking, dns_servers=list(dns_servers), issues=issues)

    def get_tun_config(self) -> Dict:
        return {
            "type": "tun",
            "tag": "tun-in",
            "inet4_address": "172.19.0.1/30",
            "inet6_address": "fdfe:dcba:9876::1/126",
            "auto_route": True,
            "strict_route": True,
            "stack": "system",
            "sniff": True,
            "sniff_override_destination": True
        }
