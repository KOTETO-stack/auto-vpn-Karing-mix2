#!/usr/bin/env python3
import asyncio
import aiohttp
import base64
import json
import time
import uuid
import random
import string
import hashlib
import os
from urllib.parse import urlparse, unquote
from datetime import datetime, timedelta

MAX_SERVERS = 150
EXCLUDE_COUNTRIES = ['UA', 'UKR', 'Ukraine', 'Украина']

COUNTRY_FLAGS = {
    'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷', 'NL': '🇳🇱',
    'SG': '🇸🇬', 'JP': '🇯🇵', 'KR': '🇰🇷', 'CA': '🇨🇦', 'AU': '🇦🇺',
    'FI': '🇫🇮', 'SE': '🇸🇪', 'NO': '🇳🇴', 'CH': '🇨🇭', 'AT': '🇦🇹',
    'PL': '🇵🇱', 'CZ': '🇨🇿', 'RO': '🇷🇴', 'BG': '🇧🇬', 'HU': '🇭🇺',
    'IT': '🇮🇹', 'ES': '🇪🇸', 'PT': '🇵🇹', 'IE': '🇮🇪', 'DK': '🇩🇰',
    'IN': '🇮🇳', 'TR': '🇹🇷', 'BR': '🇧🇷', 'MX': '🇲🇽', 'AR': '🇦🇷',
    'ZA': '🇿🇦', 'AE': '🇦🇪', 'IL': '🇮🇱', 'TH': '🇹🇭', 'VN': '🇻🇳',
    'MY': '🇲🇾', 'ID': '🇮🇩', 'PH': '🇵🇭', 'RU': '🇷🇺', 'KZ': '🇰🇿',
    'BY': '🇧🇾', 'AM': '🇦🇲', 'GE': '🇬🇪', 'AZ': '🇦🇿', 'MD': '🇲🇩',
    'LT': '🇱🇹', 'LV': '🇱🇻', 'EE': '🇪🇪', 'SK': '🇸🇰', 'SI': '🇸🇮',
    'HR': '🇭🇷', 'BA': '🇧🇦', 'RS': '🇷🇸', 'ME': '🇲🇪', 'MK': '🇲🇰',
    'AL': '🇦🇱', 'GR': '🇬🇷', 'CY': '🇨🇾', 'MT': '🇲🇹', 'IS': '🇮🇸',
    'LU': '🇱🇺'
}

COUNTRY_NAMES_RU = {
    'US': 'США', 'GB': 'Великобритания', 'DE': 'Германия', 'FR': 'Франция',
    'NL': 'Нидерланды', 'SG': 'Сингапур', 'JP': 'Япония', 'KR': 'Южная Корея',
    'CA': 'Канада', 'AU': 'Австралия', 'FI': 'Финляндия', 'SE': 'Швеция',
    'NO': 'Норвегия', 'CH': 'Швейцария', 'AT': 'Австрия', 'PL': 'Польша',
    'CZ': 'Чехия', 'RO': 'Румыния', 'BG': 'Болгария', 'HU': 'Венгрия',
    'IT': 'Италия', 'ES': 'Испания', 'PT': 'Португалия', 'IE': 'Ирландия',
    'DK': 'Дания', 'IN': 'Индия', 'TR': 'Турция', 'BR': 'Бразилия',
    'MX': 'Мексика', 'AR': 'Аргентина', 'ZA': 'ЮАР', 'AE': 'ОАЭ',
    'IL': 'Израиль', 'TH': 'Таиланд', 'VN': 'Вьетнам', 'MY': 'Малайзия',
    'ID': 'Индонезия', 'PH': 'Филиппины', 'RU': 'Россия', 'KZ': 'Казахстан',
    'BY': 'Беларусь', 'AM': 'Армения', 'GE': 'Грузия', 'AZ': 'Азербайджан',
    'MD': 'Молдова', 'LT': 'Литва', 'LV': 'Латвия', 'EE': 'Эстония',
    'SK': 'Словакия', 'SI': 'Словения', 'HR': 'Хорватия', 'BA': 'Босния',
    'RS': 'Сербия', 'ME': 'Черногория', 'MK': 'Македония', 'AL': 'Албания',
    'GR': 'Греция', 'CY': 'Кипр', 'MT': 'Мальта', 'IS': 'Исландия',
    'LU': 'Люксембург'
}

SOURCES = {
    'free_vpn_subscriptions': 'https://github.com/Au1rxx/free-vpn-subscriptions/raw/main/output/v2ray-base64.txt',
    'gfp_vless': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/vless.txt',
    'gfp_trojan': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/trojan.txt',
    'gfp_hy2': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/hy2.txt',
    'gfp_vmess': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/vmess.txt',
    'proxifly': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all.txt',
}

def generate_warp_config():
    private_key = base64.b64encode(os.urandom(32)).decode()
    account_id = str(uuid.uuid4())
    license_key = '-'.join([''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)])
    client_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    ipv6_suffix = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    ipv6 = f"2606:4700:110:{ipv6_suffix[:4]}:{ipv6_suffix[4:8]}:{ipv6_suffix[8:12]}:{ipv6_suffix[12:16]}:1"
    
    return {
        "id": account_id,
        "account": {
            "account_type": "free",
            "warp_plus": True,
            "license": license_key,
            "ttl": (datetime.now() + timedelta(days=365)).isoformat()
        },
        "config": {
            "client_id": client_id,
            "peers": [{
                "public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=",
                "endpoint": {"host": "engage.cloudflareclient.com:2408"}
            }],
            "interface": {
                "addresses": {"v4": "172.16.0.2", "v6": ipv6}
            }
        },
        "private_key": private_key,
        "public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="
    }

def decode_base64_links(data):
    try:
        decoded = base64.b64decode(data).decode('utf-8', errors='ignore')
        return [line.strip() for line in decoded.split('\n') if line.strip()]
    except:
        return []

def parse_vmess(link):
    try:
        b64 = link.replace('vmess://', '')
        json_str = base64.b64decode(b64 + '=' * (-len(b64) % 4)).decode('utf-8')
        data = json.loads(json_str)
        return {
            'protocol': 'vmess', 'ps': data.get('ps', 'Unknown'),
            'add': data.get('add', ''), 'port': str(data.get('port', '')),
            'id': data.get('id', ''), 'aid': str(data.get('aid', '0')),
            'scy': data.get('scy', 'auto'), 'net': data.get('net', 'tcp'),
            'type': data.get('type', 'none'), 'host': data.get('host', ''),
            'path': data.get('path', ''), 'tls': data.get('tls', ''),
            'sni': data.get('sni', ''), 'raw': link
        }
    except:
        return None

def parse_vless(link):
    try:
        url = link.replace('vless://', '')
        remark = 'VLESS'
        if '#' in url:
            url, remark = url.split('#', 1)
            remark = unquote(remark)
        parsed = urlparse('vless://' + url)
        query = {}
        if '?' in url:
            query_str = url.split('?')[1].split('#')[0]
            for param in query_str.split('&'):
                if '=' in param:
                    k, v = param.split('=', 1)
                    query[k] = unquote(v)
        return {
            'protocol': 'vless', 'ps': remark, 'add': parsed.hostname,
            'port': str(parsed.port), 'id': parsed.username,
            'security': query.get('security', 'none'),
            'type': query.get('type', 'tcp'), 'host': query.get('host', ''),
            'path': query.get('path', ''), 'sni': query.get('sni', ''),
            'raw': link
        }
    except:
        return None

def parse_trojan(link):
    try:
        url = link.replace('trojan://', '')
        remark = 'Trojan'
        if '#' in url:
            url, remark = url.split('#', 1)
            remark = unquote(remark)
        parsed = urlparse('trojan://' + url)
        return {
            'protocol': 'trojan', 'ps': remark, 'add': parsed.hostname,
            'port': str(parsed.port), 'password': parsed.username,
            'sni': parsed.hostname, 'raw': link
        }
    except:
        return None

def parse_hysteria2(link):
    try:
        url = link.replace('hysteria2://', '').replace('hy2://', '')
        remark = 'Hysteria2'
        if '#' in url:
            url, remark = url.split('#', 1)
            remark = unquote(remark)
        parsed = urlparse('hysteria2://' + url)
        return {
            'protocol': 'hysteria2', 'ps': remark, 'add': parsed.hostname,
            'port': str(parsed.port), 'password': parsed.username, 'raw': link
        }
    except:
        return None

def detect_country(server):
    host = server.get('add', '').lower()
    ps = server.get('ps', '').lower()
    country_map = {
        'us': 'US', 'usa': 'US', 'united states': 'US', 'america': 'US',
        'gb': 'GB', 'uk': 'GB', 'britain': 'GB', 'england': 'GB',
        'de': 'DE', 'germany': 'DE', 'fr': 'FR', 'france': 'FR',
        'nl': 'NL', 'netherlands': 'NL', 'sg': 'SG', 'singapore': 'SG',
        'jp': 'JP', 'japan': 'JP', 'kr': 'KR', 'korea': 'KR',
        'ca': 'CA', 'canada': 'CA', 'au': 'AU', 'australia': 'AU',
        'fi': 'FI', 'finland': 'FI', 'se': 'SE', 'sweden': 'SE',
        'no': 'NO', 'norway': 'NO', 'ch': 'CH', 'switzerland': 'CH',
        'at': 'AT', 'austria': 'AT', 'pl': 'PL', 'poland': 'PL',
        'cz': 'CZ', 'czech': 'CZ', 'ro': 'RO', 'romania': 'RO',
        'bg': 'BG', 'bulgaria': 'BG', 'hu': 'HU', 'hungary': 'HU',
        'it': 'IT', 'italy': 'IT', 'es': 'ES', 'spain': 'ES',
        'pt': 'PT', 'portugal': 'PT', 'ie': 'IE', 'ireland': 'IE',
        'dk': 'DK', 'denmark': 'DK', 'in': 'IN', 'india': 'IN',
        'tr': 'TR', 'turkey': 'TR', 'br': 'BR', 'brazil': 'BR',
        'mx': 'MX', 'mexico': 'MX', 'ar': 'AR', 'argentina': 'AR',
        'za': 'ZA', 'south africa': 'ZA', 'ae': 'AE', 'uae': 'AE',
        'dubai': 'AE', 'il': 'IL', 'israel': 'IL', 'th': 'TH', 'thailand': 'TH',
        'vn': 'VN', 'vietnam': 'VN', 'my': 'MY', 'malaysia': 'MY',
        'id': 'ID', 'indonesia': 'ID', 'ph': 'PH', 'philippines': 'PH',
        'ru': 'RU', 'russia': 'RU', 'kz': 'KZ', 'kazakhstan': 'KZ',
        'by': 'BY', 'belarus': 'BY', 'am': 'AM', 'armenia': 'AM',
        'ge': 'GE', 'georgia': 'GE', 'az': 'AZ', 'azerbaijan': 'AZ',
        'md': 'MD', 'moldova': 'MD', 'lt': 'LT', 'lithuania': 'LT',
        'lv': 'LV', 'latvia': 'LV', 'ee': 'EE', 'estonia': 'EE',
        'sk': 'SK', 'slovakia': 'SK', 'si': 'SI', 'slovenia': 'SI',
        'hr': 'HR', 'croatia': 'HR', 'ba': 'BA', 'bosnia': 'BA',
        'rs': 'RS', 'serbia': 'RS', 'me': 'ME', 'montenegro': 'ME',
        'mk': 'MK', 'macedonia': 'MK', 'al': 'AL', 'albania': 'AL',
        'gr': 'GR', 'greece': 'GR', 'cy': 'CY', 'cyprus': 'CY',
        'mt': 'MT', 'malta': 'MT', 'is': 'IS', 'iceland': 'IS',
        'lu': 'LU', 'luxembourg': 'LU', 'ua': 'UA', 'ukraine': 'UA',
        'kyiv': 'UA', 'kiev': 'UA'
    }
    for key, code in country_map.items():
        if key in host or key in ps:
            return code
    return 'US'

def get_city(server):
    ps = server.get('ps', '').lower()
    host = server.get('add', '').lower()
    city_patterns = {
        'new york': 'Нью-Йорк', 'ny': 'Нью-Йорк', 'nyc': 'Нью-Йорк',
        'los angeles': 'Лос-Анджелес', 'la': 'Лос-Анджелес',
        'chicago': 'Чикаго', 'miami': 'Майами', 'dallas': 'Даллас',
        'seattle': 'Сиэтл', 'san francisco': 'Сан-Франциско', 'sf': 'Сан-Франциско',
        'boston': 'Бостон', 'atlanta': 'Атланта', 'denver': 'Денвер',
        'london': 'Лондон', 'manchester': 'Манчестер', 'birmingham': 'Бирмингем',
        'frankfurt': 'Франкфурт', 'berlin': 'Берлин', 'munich': 'Мюнхен',
        'hamburg': 'Гамбург', 'cologne': 'Кёльн', 'dusseldorf': 'Дюссельдорф',
        'paris': 'Париж', 'marseille': 'Марсель', 'lyon': 'Лион',
        'amsterdam': 'Амстердам', 'rotterdam': 'Роттердам',
        'singapore': 'Сингапур', 'sg': 'Сингапур',
        'tokyo': 'Токио', 'osaka': 'Осака', 'yokohama': 'Йокогама',
        'seoul': 'Сеул', 'busan': 'Пусан',
        'toronto': 'Торонто', 'vancouver': 'Ванкувер', 'montreal': 'Монреаль',
        'sydney': 'Сидней', 'melbourne': 'Мельбурн',
        'helsinki': 'Хельсинки', 'stockholm': 'Стокгольм', 'oslo': 'Осло',
        'zurich': 'Цюрих', 'geneva': 'Женева', 'vienna': 'Вена',
        'warsaw': 'Варшава', 'krakow': 'Краков', 'prague': 'Прага',
        'bucharest': 'Бухарест', 'sofia': 'София', 'budapest': 'Будапешт',
        'rome': 'Рим', 'milan': 'Милан', 'madrid': 'Мадрид', 'barcelona': 'Барселона',
        'lisbon': 'Лиссабон', 'dublin': 'Дублин', 'copenhagen': 'Копенгаген',
        'mumbai': 'Мумбаи', 'delhi': 'Дели', 'bangalore': 'Бангалор',
        'istanbul': 'Стамбул', 'ankara': 'Анкара', 'izmir': 'Измир',
        'sao paulo': 'Сан-Паулу', 'rio': 'Рио-де-Жанейро',
        'mexico city': 'Мехико', 'buenos aires': 'Буэнос-Айрес',
        'johannesburg': 'Йоханнесбург', 'cape town': 'Кейптаун',
        'dubai': 'Дубай', 'abu dhabi': 'Абу-Даби',
        'tel aviv': 'Тель-Авив', 'jerusalem': 'Иерусалим',
        'bangkok': 'Бангкок', 'ho chi minh': 'Хошимин', 'hanoi': 'Ханой',
        'kuala lumpur': 'Куала-Лумпур', 'jakarta': 'Джакарта', 'manila': 'Манила',
        'moscow': 'Москва', 'spb': 'Санкт-Петербург', 'petersburg': 'Санкт-Петербург',
        'almaty': 'Алматы', 'astana': 'Астана', 'minsk': 'Минск',
        'yerevan': 'Ереван', 'tbilisi': 'Тбилиси', 'baku': 'Баку',
        'chisinau': 'Кишинёв', 'vilnius': 'Вильнюс', 'riga': 'Рига', 'tallinn': 'Таллин',
        'bratislava': 'Братислава', 'ljubljana': 'Любляна', 'zagreb': 'Загреб',
        'belgrade': 'Белград', 'podgorica': 'Подгорица', 'skopje': 'Скопье',
        'tirana': 'Тирана', 'athens': 'Афины', 'nicosia': 'Никосия', 'valletta': 'Валлетта',
        'reykjavik': 'Рейкьявик', 'luxembourg': 'Люксембург'
    }
    for key, city in city_patterns.items():
        if key in ps or key in host:
            return city
    return ''

def format_server_name(server):
    country = detect_country(server)
    if country in EXCLUDE_COUNTRIES or country == 'UA':
        return None
    flag = COUNTRY_FLAGS.get(country, '🌍')
    name = COUNTRY_NAMES_RU.get(country, country)
    city = get_city(server)
    if city:
        return f"{flag} {name} {city}"
    return f"{flag} {name}"

async def fetch_source(session, name, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status == 200:
                return name, await resp.text()
    except Exception as e:
        print(f"Error fetching {name}: {e}")
    return name, ''

def parse_links(text):
    links = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('vmess://'):
            s = parse_vmess(line)
            if s: links.append(s)
        elif line.startswith('vless://'):
            s = parse_vless(line)
            if s: links.append(s)
        elif line.startswith('trojan://'):
            s = parse_trojan(line)
            if s: links.append(s)
        elif line.startswith('hysteria2://') or line.startswith('hy2://'):
            s = parse_hysteria2(line)
            if s: links.append(s)
    return links

async def ping_server(session, server):
    try:
        host = server.get('add', '')
        if not host:
            return float('inf')
        start = time.time()
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, int(server.get('port', 443))),
            timeout=5
        )
        writer.close()
        await writer.wait_closed()
        return (time.time() - start) * 1000
    except:
        return float('inf')

def generate_clash_config(servers, warp_config):
    proxies = []
    proxy_names = []
    
    warp_name = "🛡️ WARP+ Защита"
    proxy_names.append(warp_name)
    proxies.append({
        'name': warp_name,
        'type': 'wireguard',
        'server': 'engage.cloudflareclient.com',
        'port': 2408,
        'ip': '172.16.0.2',
        'ipv6': warp_config['config']['interface']['addresses']['v6'],
        'private-key': warp_config['private_key'],
        'public-key': warp_config['config']['peers'][0]['public_key'],
        'reserved': [0, 0, 0],
        'udp': True
    })
    
    amnezia_name = "🔒 Amnezia WG"
    proxy_names.append(amnezia_name)
    proxies.append({
        'name': amnezia_name,
        'type': 'wireguard',
        'server': 'YOUR_AMNEZIA_SERVER_IP',
        'port': 51820,
        'ip': '10.8.1.2',
        'private-key': 'YOUR_AMNEZIA_PRIVATE_KEY',
        'public-key': 'YOUR_AMNEZIA_SERVER_PUBLIC_KEY',
        'preshared-key': 'YOUR_AMNEZIA_PRESHARED_KEY',
        'udp': True,
        'reserved': [0, 0, 0]
    })
    
    for i, server in enumerate(servers[:MAX_SERVERS]):
        name = format_server_name(server)
        if not name:
            continue
        proto = server['protocol']
        base_name = f"{name} #{i+1}"
        proxy_names.append(base_name)
        
        if proto == 'vmess':
            proxy = {
                'name': base_name, 'type': 'vmess',
                'server': server['add'], 'port': int(server['port']),
                'uuid': server['id'], 'alterId': int(server.get('aid', 0)),
                'cipher': server.get('scy', 'auto'),
                'tls': server.get('tls') == 'tls',
                'servername': server.get('sni', ''),
                'network': server.get('net', 'tcp'),
                'ws-opts': {'path': server.get('path', ''), 'headers': {'Host': server.get('host', '')}} if server.get('net') == 'ws' else {}
            }
        elif proto == 'vless':
            proxy = {
                'name': base_name, 'type': 'vless',
                'server': server['add'], 'port': int(server['port']),
                'uuid': server['id'],
                'tls': server.get('security') in ['tls', 'xtls'],
                'servername': server.get('sni', server['add']),
                'network': server.get('type', 'tcp'),
                'ws-opts': {'path': server.get('path', ''), 'headers': {'Host': server.get('host', '')}} if server.get('type') == 'ws' else {},
                'flow': server.get('flow', '')
            }
        elif proto == 'trojan':
            proxy = {
                'name': base_name, 'type': 'trojan',
                'server': server['add'], 'port': int(server['port']),
                'password': server['password'],
                'sni': server.get('sni', server['add']),
                'skip-cert-verify': False
            }
        elif proto == 'hysteria2':
            proxy = {
                'name': base_name, 'type': 'hysteria2',
                'server': server['add'], 'port': int(server['port']),
                'password': server['password'],
                'sni': server['add'],
                'skip-cert-verify': False
            }
        else:
            continue
        proxies.append(proxy)
    
    proxy_groups = [
        {
            'name': '🚀 Автовыбор (быстрейший)',
            'type': 'url-test',
            'proxies': proxy_names,
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300,
            'tolerance': 50
        },
        {
            'name': '📺 YouTube Без Рекламы',
            'type': 'select',
            'proxies': ['🚀 Автовыбор (быстрейший)'] + proxy_names
        },
        {
            'name': '📱 Telegram',
            'type': 'select',
            'proxies': ['🚀 Автовыбор (быстрейший)'] + proxy_names
        },
        {
            'name': '🎵 TikTok',
            'type': 'select',
            'proxies': ['🚀 Автовыбор (быстрейший)'] + proxy_names
        },
        {
            'name': '💬 WeChat / WhatsApp / BiP',
            'type': 'select',
            'proxies': ['🚀 Автовыбор (быстрейший)'] + proxy_names
        },
        {
            'name': '🛡️ WARP+ Защита',
            'type': 'select',
            'proxies': [warp_name]
        },
        {
            'name': '🔒 Amnezia WG',
            'type': 'select',
            'proxies': [amnezia_name]
        },
        {
            'name': '🌐 Все сервера',
            'type': 'select',
            'proxies': proxy_names
        }
    ]
    
    rules = [
        'DOMAIN-SUFFIX,googlevideo.com,📺 YouTube Без Рекламы',
        'DOMAIN-SUFFIX,youtube.com,📺 YouTube Без Рекламы',
        'DOMAIN-SUFFIX,ytimg.com,📺 YouTube Без Рекламы',
        'DOMAIN-SUFFIX,youtubei.googleapis.com,📺 YouTube Без Рекламы',
        'DOMAIN-KEYWORD,youtube,📺 YouTube Без Рекламы',
        'DOMAIN-SUFFIX,telegram.org,📱 Telegram',
        'DOMAIN-SUFFIX,telegram.me,📱 Telegram',
        'DOMAIN-SUFFIX,t.me,📱 Telegram',
        'DOMAIN-SUFFIX,tdesktop.com,📱 Telegram',
        'DOMAIN-KEYWORD,telegram,📱 Telegram',
        'DOMAIN-SUFFIX,tiktok.com,🎵 TikTok',
        'DOMAIN-SUFFIX,tiktokv.com,🎵 TikTok',
        'DOMAIN-SUFFIX,tiktokcdn.com,🎵 TikTok',
        'DOMAIN-KEYWORD,tiktok,🎵 TikTok',
        'DOMAIN-SUFFIX,wechat.com,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-SUFFIX,weixin.qq.com,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-SUFFIX,whatsapp.com,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-SUFFIX,whatsapp.net,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-SUFFIX,wa.me,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-SUFFIX,bip.com,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-KEYWORD,wechat,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-KEYWORD,whatsapp,💬 WeChat / WhatsApp / BiP',
        'DOMAIN-SUFFIX,googletagmanager.com,REJECT',
        'DOMAIN-SUFFIX,googleadservices.com,REJECT',
        'DOMAIN-SUFFIX,doubleclick.net,REJECT',
        'DOMAIN-SUFFIX,ads.youtube.com,REJECT',
        'DOMAIN-SUFFIX,google-analytics.com,REJECT',
        'DOMAIN-SUFFIX,facebook.com,REJECT',
        'DOMAIN-SUFFIX,fbcdn.net,REJECT',
        'DOMAIN-SUFFIX,instagram.com,REJECT',
        'MATCH,🌐 Все сервера'
    ]
    
    return {
        'port': 7890,
        'socks-port': 7891,
        'mixed-port': 7892,
        'allow-lan': False,
        'mode': 'rule',
        'log-level': 'info',
        'external-controller': '127.0.0.1:9090',
        'dns': {
            'enable': True,
            'listen': '0.0.0.0:53',
            'default-nameserver': ['1.1.1.1', '8.8.8.8', '9.9.9.9'],
            'nameserver': ['https://1.1.1.1/dns-query', 'https://8.8.8.8/dns-query'],
            'fallback': ['https://dns.google/dns-query', 'https://dns.quad9.net/dns-query'],
            'fallback-filter': {'geoip': True, 'geoip-code': 'RU'}
        },
        'proxies': proxies,
        'proxy-groups': proxy_groups,
        'rules': rules
    }

def generate_base64_links(servers):
    links = []
    for server in servers[:MAX_SERVERS]:
        name = format_server_name(server)
        if not name:
            continue
        raw = server.get('raw', '')
        if raw:
            if '#' in raw:
                base = raw.split('#')[0]
                links.append(f"{base}#{name.replace(' ', '%20')}")
            else:
                links.append(f"{raw}#{name.replace(' ', '%20')}")
    return '\n'.join(links)

async def main():
    print("Generating WARP+ config...")
    warp_config = generate_warp_config()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, name, url) for name, url in SOURCES.items()]
        results = await asyncio.gather(*tasks)
        
        all_servers = []
        for name, text in results:
            if text:
                servers = parse_links(text)
                print(f"Source {name}: {len(servers)} servers")
                all_servers.extend(servers)
        
        print(f"Total collected: {len(all_servers)}")
        
        filtered = [s for s in all_servers if detect_country(s) not in EXCLUDE_COUNTRIES and detect_country(s) != 'UA']
        print(f"After UA filter: {len(filtered)}")
        
        print("Pinging servers...")
        ping_tasks = [ping_server(session, s) for s in filtered]
        pings = await asyncio.gather(*ping_tasks)
        
        server_with_ping = [(s, p) for s, p in zip(filtered, pings) if p < 5000]
        server_with_ping.sort(key=lambda x: x[1])
        
        best_servers = [s for s, p in server_with_ping]
        print(f"Alive servers: {len(best_servers)}")
        
        clash_config = generate_clash_config(best_servers, warp_config)
        base64_links = generate_base64_links(best_servers)
        
        os.makedirs('output', exist_ok=True)
        
        with open('output/clash.yaml', 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)
        
        with open('output/v2ray.txt', 'w', encoding='utf-8') as f:
            f.write(base64_links)
        
        with open('output/v2ray-base64.txt', 'w', encoding='utf-8') as f:
            f.write(base64.b64encode(base64_links.encode()).decode())
        
        singbox_outbounds = [
            {"type": "selector", "tag": "Auto", "outbounds": ["WARP+", "Amnezia"]},
            {
                "type": "wireguard",
                "tag": "WARP+",
                "server": "engage.cloudflareclient.com",
                "server_port": 2408,
                "local_address": ["172.16.0.2/32", warp_config['config']['interface']['addresses']['v6']],
                "private_key": warp_config['private_key'],
                "peer_public_key": warp_config['config']['peers'][0]['public_key'],
                "reserved": [0, 0, 0]
            },
            {
                "type": "wireguard",
                "tag": "Amnezia",
                "server": "YOUR_AMNEZIA_SERVER_IP",
                "server_port": 51820,
                "local_address": ["10.8.1.2/32"],
                "private_key": "YOUR_AMNEZIA_PRIVATE_KEY",
                "peer_public_key": "YOUR_AMNEZIA_SERVER_PUBLIC_KEY",
                "reserved": [0, 0, 0]
            }
        ]
        
        for i, s in enumerate(best_servers[:MAX_SERVERS]):
            name = format_server_name(s)
            if not name:
                continue
            outbound = {
                "type": s['protocol'],
                "tag": f"{name} #{i+1}",
                "server": s['add'],
                "server_port": int(s['port'])
            }
            if s['protocol'] in ['vmess', 'vless']:
                outbound['uuid'] = s['id']
            elif s['protocol'] in ['trojan', 'hysteria2']:
                outbound['password'] = s.get('password', '')
            singbox_outbounds.append(outbound)
        
        singbox_config = {
            "log": {"level": "info"},
            "dns": {
                "servers": [
                    {"tag": "cloudflare", "address": "https://1.1.1.1/dns-query"},
                    {"tag": "google", "address": "https://8.8.8.8/dns-query"}
                ],
                "rules": [
                    {"domain_suffix": [".ru", ".рф"], "server": "cloudflare"}
                ]
            },
            "inbounds": [
                {"type": "mixed", "listen": "127.0.0.1", "listen_port": 2080}
            ],
            "outbounds": singbox_outbounds,
            "route": {
                "rules": [
                    {"domain_suffix": ["youtube.com", "googlevideo.com"], "outbound": "Auto"},
                    {"domain_suffix": ["telegram.org", "t.me"], "outbound": "Auto"},
                    "domain_suffix": ["tiktok.com", "tiktokv.com"], "outbound": "Auto"},
                    {"domain_suffix": ["wechat.com", "whatsapp.com", "bip.com"], "outbound": "Auto"}
                ]
            }
        }
        
        with open('output/sing-box.json', 'w', encoding='utf-8') as f:
            json.dump(singbox_config, f, indent=2, ensure_ascii=False)
        
        with open('output/warp-plus.json', 'w', encoding='utf-8') as f:
            json.dump(warp_config, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {min(len(best_servers), MAX_SERVERS)} servers + WARP+ config to output/")
        print(f"WARP+ License: {warp_config['account']['license']}")
        print(f"WARP+ TTL: {warp_config['account']['ttl']}")

if __name__ == '__main__':
    asyncio.run(main())
