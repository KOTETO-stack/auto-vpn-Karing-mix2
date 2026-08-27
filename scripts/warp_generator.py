#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WARP+ Key Generator & Config Builder"""
import os, json, base64, urllib.request, urllib.error, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

CF_API = "https://api.cloudflareclient.com/v0a2158"
CF_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "okhttp/3.12.1",
    "CF-Client-Version": "a-6.10-2158",
}
CF_PUBLIC_KEY = "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="

def generate_private_key():
    key = bytearray(os.urandom(32))
    key[0] &= 248; key[31] &= 127; key[31] |= 64
    return bytes(key)

def scalar_mult_base(scalar):
    import nacl.bindings
    s = bytearray(scalar); s[0] &= 248; s[31] &= 127; s[31] |= 64
    return nacl.bindings.crypto_scalarmult_base(bytes(s))

def register_device():
    private_key = generate_private_key()
    public_key = scalar_mult_base(private_key)
    pubkey_b64 = base64.b64encode(public_key).decode()
    privkey_b64 = base64.b64encode(private_key).decode()
    data = json.dumps({
        "key": pubkey_b64, "install_id": "", "fcm_token": "",
        "tos": "2024-01-01T00:00:00.000Z", "model": "PC",
        "serial_number": "", "locale": "ru_RU"
    }).encode()
    req = urllib.request.Request(f"{CF_API}/reg", data=data, headers=CF_HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            reg = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[!] Ошибка регистрации: {e.code}"); return None
    return {"id": reg.get("id",""), "token": reg.get("token",""),
            "private_key": privkey_b64, "public_key": pubkey_b64}

def get_warp_config(reg_info):
    if not reg_info: return None
    req = urllib.request.Request(
        f"{CF_API}/reg/{reg_info['id']}",
        headers={**CF_HEADERS, "Authorization": f"Bearer {reg_info['token']}"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[!] Ошибка: {e}"); return None
    cfg = data.get("config", {}); peers = cfg.get("peers", [{}])[0]
    iface = cfg.get("interface", {}); addrs = iface.get("addresses", {})
    return {
        "id": reg_info["id"], "token": reg_info["token"],
        "private_key": reg_info["private_key"], "public_key": reg_info["public_key"],
        "peer_public_key": peers.get("public_key", CF_PUBLIC_KEY),
        "endpoint": peers.get("endpoint", {}).get("v4", "engage.cloudflareclient.com:2408"),
        "v4": addrs.get("v4", "172.16.0.2"), "v6": addrs.get("v6", "")}

def add_warp_plus(config, license_key=""):
    if not license_key or not config: return config
    data = json.dumps({"license": license_key}).encode()
    req = urllib.request.Request(
        f"{CF_API}/reg/{config['id']}/account", data=data,
        headers={**CF_HEADERS, "Authorization": f"Bearer {config['token']}"}, method="PUT")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            config["warp_plus"] = True; config["license"] = license_key
            config["account_type"] = result.get("account_type", "free")
            print("[+] WARP+ активирован")
    except Exception as e:
        print(f"[!] WARP+ не активирован: {e}"); config["warp_plus"] = False
    return config

def build_wireguard_conf(config, filename="warp.conf"):
    if not config: return
    v6 = f"Address = {config['v6']}/128\n" if config.get("v6") else ""
    conf = f"""[Interface]\nPrivateKey = {config['private_key']}\nAddress = {config['v4']}/32\n{v6}DNS = 1.1.1.1, 1.0.0.1, 2606:4700:4700::1111\nMTU = 1280\n\n[Peer]\nPublicKey = {config['peer_public_key']}\nAllowedIPs = 0.0.0.0/0, ::/0\nEndpoint = {config['endpoint']}\nPersistentKeepalive = 25\n"""
    with open(f"configs/{filename}", "w", encoding="utf-8") as f:
        f.write(conf)
    print(f"[+] WireGuard: configs/{filename}")

def build_json_config(config, filename="warp_plus.json"):
    if not config: return
    data = {
        "id": config["id"],
        "account": {"account_type": config.get("account_type","free"),
                    "warp_plus": config.get("warp_plus", False),
                    "license": config.get("license", "")},
        "config": {"client_id": "",
                   "peers": [{"public_key": config["peer_public_key"],
                              "endpoint": {"host": config["endpoint"]}}],
                   "interface": {"addresses": {"v4": config["v4"], "v6": config.get("v6","")}}}
    }
    with open(f"configs/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] JSON: configs/{filename}")

def build_v2ray_outbound(config):
    if not config: return None
    addrs = [config["v4"] + "/32"]
    if config.get("v6"): addrs.append(config["v6"] + "/128")
    return {
        "tag": "🛡️ WARP+ Защита",
        "protocol": "wireguard",
        "settings": {
            "secretKey": config["private_key"], "address": addrs,
            "peers": [{"publicKey": config["peer_public_key"],
                        "allowedIPs": ["0.0.0.0/0", "::/0"],
                        "endpoint": config["endpoint"], "keepAlive": 25}],
            "mtu": 1280}}

def main():
    print("[+] WARP генерация...")
    try: import nacl.bindings
    except ImportError: print("[!] pip install PyNaCl"); return
    reg = register_device()
    if not reg: return
    cfg = get_warp_config(reg)
    if not cfg: return
    license_key = os.environ.get("WARP_LICENSE", "").strip()
    if license_key: cfg = add_warp_plus(cfg, license_key)
    else: print("[!] Без WARP+ (добавь WARP_LICENSE в GitHub Secrets)"); cfg["warp_plus"] = False
    build_wireguard_conf(cfg, "warp.conf")
    build_json_config(cfg, "warp_plus.json")
    outbound = build_v2ray_outbound(cfg)
    with open("configs/warp_outbound.json", "w", encoding="utf-8") as f:
        json.dump(outbound, f, ensure_ascii=False, indent=2)
    print("[+] WARP готов!")

if __name__ == "__main__":
    main()
