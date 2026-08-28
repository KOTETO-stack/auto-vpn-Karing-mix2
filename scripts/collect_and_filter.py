#!/usr/bin/env python3
"""
VPN Auto-Collector for Karing iOS
Собирает, пингует, проверяет сервера из публичных источников
"""

import asyncio
import aiohttp
import base64
import json
import re
import subprocess
import time
from urllib.parse import urlparse
from datetime import datetime

# === НАСТРОЙКИ ===
MAX_SERVERS = 150
EXCLUDE_COUNTRIES = ['UA', 'UKR', 'Ukraine', 'Украина']
TARGET_PROTOCOLS = ['vless', 'trojan', 'hysteria2', 'vmess']
PING_TIMEOUT = 5
MAX_PING_MS = 500

# Публичные источники (только интернет, не Telegram)
SOURCES = {
    'free_vpn_subscriptions': 'https://github.com/Au1rxx/free-vpn-subscriptions/raw/main/output/v2ray-base64.txt',
    'gfp_vless': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/vless.txt',
    'gfp_trojan': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/trojan.txt',
    'gfp_hy2': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/hy2.txt',
    'gfp_vmess': 'https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/vmess.txt',
    'proxifly': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all.txt',
}

# Флаги стран для отображения
COUNTRY_FLAGS = {
    'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪', 'FR': '🇫🇷', 'NL': '🇳🇱',
    'SG': '🇸🇬', 'JP': '🇯🇵', 'KR': '🇰🇷', 'CA': '🇨🇦', 'AU': '🇦🇺',
    'FI': '🇫🇮', 'SE': '🇸🇪', 'NO': '🇳🇴', 'CH': '🇨🇭', 'AT': '🇦🇹',
    'PL': '🇵🇱', 'CZ': '🇨🇿', 'RO': '🇷🇴', 'BG': '🇧🇬', 'HU': '🇭🇺',
    'IT': '🇮🇹', 'ES': '🇪🇸', 'PT': '🇵🇹', 'IE': '🇮🇪', 'DK': '🇩🇰',
    'IN': '🇮🇳', 'TR': '🇹🇷', 'BR': '🇧🇷', 'MX': '🇲🇽', 'AR': '🇦🇷',
    'ZA': '🇿🇦', 'AE': '🇦🇪', 'IL': '🇮🇱', 'TH': '🇹🇭', 'VN': '🇻🇳',
    'MY': '🇲🇾', '
