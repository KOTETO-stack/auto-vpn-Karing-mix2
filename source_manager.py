import json
import requests
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_FILE = "fetch_sources.json"
MIN_SOURCES = 10
TIMEOUT = 15
MAX_WORKERS = 20


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def check_url(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code != 200:
            return url, False, f"status {r.status_code}"
        ct = len(r.content)
        if ct < 50:
            return url, False, f"too small ({ct}b)"
        text = r.text.strip()
        if not text:
            return url, False, "empty body"
        valid = False
        markers = ["vmess://", "vless://", "trojan://", "ss://", "hy2://", "hysteria2://", "proxies:", "Proxy:", "outbounds:"]
        for m in markers:
            if m in text:
                valid = True
                break
        if not valid:
            try:
                decoded = base64.b64decode(text).decode("utf-8", errors="ignore")
                for m in markers:
                    if m in decoded:
                        valid = True
                        break
            except Exception:
                pass
        if not valid:
            return url, False, "no proxy markers"
        return url, True, "ok"
    except requests.exceptions.Timeout:
        return url, False, "timeout"
    except requests.exceptions.ConnectionError:
        return url, False, "connection error"
    except Exception as e:
        return url, False, str(e)[:50]


def discover_github_sources():
    discovered = []
    queries = [
        "free v2ray subscription raw github",
        "free proxy list vless trojan hysteria2",
        "clash subscription free github raw"
    ]
    headers = {"Accept": "application/vnd.github.v3+json"}
    for q in queries:
        try:
            r = requests.get(
                f"https://api.github.com/search/repositories?q={q}&sort=updated&order=desc&per_page=10",
                headers=headers,
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                for item in data.get("items", []):
                    repo = item["full_name"]
                    branch = item.get("default_branch", "main")
                    candidates = [
                        f"https://raw.githubusercontent.com/{repo}/{branch}/sub",
                        f"https://raw.githubusercontent.com/{repo}/{branch}/v2",
                        f"https://raw.githubusercontent.com/{repo}/{branch}/subscribe.txt",
                        f"https://raw.githubusercontent.com/{repo}/{branch}/clash.yaml",
                        f"https://raw.githubusercontent.com/{repo}/{branch}/nodes.txt",
                        f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
                    ]
                    discovered.extend(candidates)
        except Exception:
            continue
    return list(set(discovered))


def validate_and_update():
    cfg = load_config()
    sources = cfg.get("sources", [])
    print(f"[*] Checking {len(sources)} sources...")
    alive = []
    dead = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(check_url, url): url for url in sources}
        for future in as_completed(futures):
            url, ok, msg = future.result()
            if ok:
                alive.append(url)
                print(f"  [+] {url[:60]}... -> {msg}")
            else:
                dead.append(url)
                print(f"  [-] {url[:60]}... -> {msg}")
    print(f"\n[*] Alive: {len(alive)}, Dead: {len(dead)}")
    if len(alive) < MIN_SOURCES:
        print(f"[*] Too few alive ({len(alive)} < {MIN_SOURCES}), discovering new...")
        discovered = discover_github_sources()
        new_urls = [u for u in discovered if u not in alive and u not in dead]
        print(f"[*] Discovered {len(new_urls)} candidates, checking...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            futures = {ex.submit(check_url, url): url for url in new_urls}
            for future in as_completed(futures):
                url, ok, msg = future.result()
                if ok:
                    alive.append(url)
                    print(f"  [+] NEW {url[:60]}... -> {msg}")
                else:
                    dead.append(url)
        print(f"\n[*] After discovery: Alive: {len(alive)}")
    cfg["sources"] = alive
    save_config(cfg)
    print(f"[*] Saved {len(alive)} valid sources to {CONFIG_FILE}")
    return alive


if __name__ == "__main__":
    validate_and_update()
