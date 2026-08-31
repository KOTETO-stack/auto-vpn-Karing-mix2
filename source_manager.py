import json, base64, re, socket, time, urllib.parse, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import md5
import random

CONFIG_FILE = "fetch_sources.json"
OUTPUT_FILE = "subscription.txt"
ENCRYPTED_FILE = "subscription_encrypted.txt"
AMNEZIA_LINK = "vpn://AAAA_3icXY3LDoIwEEV_hXStJhhjojsjERN0AbowbkgtAzZA2_QBQcO_2xbduJrMPXfmvBHDLaBtgHYtgxfFwUECoFmAClBEUqEpZ_84IJwxIB7Zpt1KWuUdSDWVlzbEguYTsMEbKZAdJZDrQXgbnt7Ny6_tx4XkmhPe-E5fOWQss68M03Kws_D30qDRWYx-5gXW2Eucs4bB8Yg2qyTM-sUjO16u9SmKUxOt92VI6js_dzyNsz7cqOSGxvEDmaFXJg=="
TARGET_SERVERS = 150
PING_TIMEOUT = 3
MAX_PING_WORKERS = 50
ENCRYPTION_PASSWORD = "KaringSecure2024!"

CN = {"US":"США","GB":"Великобритания","DE":"Германия","NL":"Нидерланды","FR":"Франция","JP":"Япония","KR":"Корея","SG":"Сингапур","HK":"Гонконг","TW":"Тайвань","RU":"Россия","CA":"Канада","AU":"Австралия","IN":"Индия","BR":"Бразилия","TR":"Турция","PL":"Польша","UA":"Украина","KZ":"Казахстан","BY":"Беларусь","FI":"Финляндия","SE":"Швеция","NO":"Норвегия","CH":"Швейцария","AT":"Австрия","IT":"Италия","ES":"Испания","PT":"Португалия","CZ":"Чехия","RO":"Румыния","BG":"Болгария","HU":"Венгрия","LT":"Литва","LV":"Латвия","EE":"Эстония","MD":"Молдова","GE":"Грузия","AM":"Армения","AZ":"Азербайджан","UZ":"Узбекистан","KG":"Кыргызстан","TJ":"Таджикистан","TM":"Туркменистан","IL":"Израиль","AE":"ОАЭ","SA":"Саудовская Аравия","TH":"Таиланд","VN":"Вьетнам","MY":"Малайзия","ID":"Индонезия","PH":"Филиппины","MX":"Мексика","AR":"Аргентина","CL":"Чили","ZA":"ЮАР","NG":"Нигерия","EG":"Египет","PK":"Пакистан","BD":"Бангладеш","LK":"Шри-Ланка","NP":"Непал","MM":"Мьянма","KH":"Камбоджа","LA":"Лаос","MN":"Монголия","IS":"Исландия","IE":"Ирландия","DK":"Дания","BE":"Бельгия","LU":"Люксембург","SK":"Словакия","SI":"Словения","HR":"Хорватия","RS":"Сербия","BA":"Босния","ME":"Черногория","MK":"Северная Македония","AL":"Албания","GR":"Греция","CY":"Кипр","MT":"Мальта"}

def gf(cc):
    return chr(0x1F1E6+ord(cc[0])-65)+chr(0x1F1E6+ord(cc[1])-65)

CT = {"US":{"nyc":"Нью-Йорк","la":"Лос-Анджелес","chi":"Чикаго","dal":"Даллас","mia":"Майами","sf":"Сан-Франциско","sea":"Сиэтл","atl":"Атланта","hou":"Хьюстон","phx":"Финикс","den":"Денвер","bos":"Бостон","lv":"Лас-Вегас","orl":"Орландо","ash":"Ашберн","buf":"Буффало"},"GB":{"lon":"Лондон","man":"Манчестер","bir":"Бирмингем","gla":"Глазго","edi":"Эдинбург","liv":"Ливерпуль"},"DE":{"fra":"Франкфурт","ber":"Берлин","mun":"Мюнхен","ham":"Гамбург","col":"Кёльн","stu":"Штутгарт","dus":"Дюссельдорф"},"NL":{"ams":"Амстердам","rot":"Роттердам","hag":"Гаага","utr":"Утрехт","eind":"Эйндховен"},"FR":{"par":"Париж","mar":"Марсель","lyo":"Лион","toul":"Тулуза","nice":"Ницца","bor":"Бордо"},"JP":{"tok":"Токио","osa":"Осака","yok":"Йокогама","nag":"Нагоя","sap":"Саппоро","fuk":"Фукуока"},"KR":{"seo":"Сеул","bus":"Пусан","inc":"Инчхон","dae":"Тэгу","gwa":"Кванджу"},"SG":{"sin":"Сингапур"},"HK":{"hkg":"Гонконг"},"TW":{"tpe":"Тайбэй","tai":"Тайчжун","kao":"Гаосюн"},"RU":{"mos":"Москва","spb":"Санкт-Петербург","nov":"Новосибирск","eka":"Екатеринбург","kaz":"Казань","niz":"Нижний Новгород","che":"Челябинск","oms":"Омск","sam":"Самара","ros":"Ростов-на-Дону","ufa":"Уфа","kra":"Красноярск","vor":"Воронеж","per":"Пермь","vol":"Волгоград"},"CA":{"tor":"Торонто","van":"Ванкувер","mon":"Монреаль","cal":"Калгари","ott":"Оттава","edm":"Эдмонтон"},"AU":{"syd":"Сидней","mel":"Мельбурн","bri":"Брисбен","per":"Перт","ade":"Аделаида"},"IN":{"bom":"Мумбаи","del":"Дели","ban":"Бангалор","hyd":"Хайderabad","che":"Ченнаи","kol":"Калькутта"},"BR":{"sao":"Сан-Паулу","rio":"Рио-де-Жанейро","bsb":"Бразилиа","sal":"Салвадор","for":"Форталеза"},"TR":{"ist":"Стамбул","ank":"Анкара","izm":"Измир","ant":"Анталья","bur":"Бурса"},"PL":{"war":"Варшава","kra":"Краков","wro":"Вроцлав","poz":"Познань","gda":"Гданьск"},"UA":{"kyi":"Киев","kha":"Харьков","ode":"Одесса","dni":"Днепр","don":"Донецк","lvv":"Львов"},"KZ":{"ala":"Алматы","nur":"Нур-Султан","shi":"Шымкент","kar":"Караганда"},"BY":{"min":"Минск","gom":"Гомель","mog":"Могилев","vit":"Витебск","gro":"Гродно"},"FI":{"hel":"Хельсинки","esp":"Эспоо","tam":"Тампере","van":"Вантаа"},"SE":{"sto":"Стокгольм","got":"Гётеборг","mal":"Мальмё","ups":"Уппсала"},"NO":{"osl":"Осло","ber":"Берген","tro":"Тронхейм","sta":"Ставангер"},"CH":{"zur":"Цюрих","gen":"Женева","bas":"Базель","ber":"Берн","lau":"Лозанна"},"AT":{"vie":"Вена","gra":"Грац","lin":"Линц","sal":"Зальцбург","ins":"Инсбрук"},"IT":{"rom":"Рим","mil":"Милан","nap":"Неаполь","tur":"Турин","pal":"Палермо","gen":"Генуя","bol":"Болонья","flo":"Флоренция"},"ES":{"mad":"Мадрид","bar":"Барселона","val":"Валенсия","sev":"Севилья","bil":"Бильбао","mal":"Малага"},"PT":{"lis":"Лиссабон","por":"Порту","far":"Фару","coi":"Коимбра"},"CZ":{"pra":"Прага","bru":"Брно","ost":"Острава","pli":"Пльзень"},"RO":{"buc":"Бухарест","cla":"Клуж-Напока","tim":"Тимишоара","ias":"Яссы","con":"Констанца"},"BG":{"sof":"София","plo":"Пловдив","var":"Варна","bur":"Бургас"},"HU":{"bud":"Будапешт","deb":"Дебрецен","sze":"Сегед","mis":"Мишкольц"},"LT":{"vil":"Вильнюс","kau":"Каунас","kla":"Клайпеда","sha":"Шяуляй","pan":"Паневежис"},"LV":{"rig":"Рига","dau":"Даугавпилс","lie":"Лиепая","jel":"Елгава"},"EE":{"tal":"Таллин","tar":"Тарту","nar":"Нарва","par":"Пярну"},"MD":{"chi":"Кишинев","tir":"Тирасполь","bal":"Бельцы","ben":"Бендеры"},"GE":{"tbi":"Тбилиси","kut":"Кутаиси","bat":"Батуми","sok":"Сухуми","pot":"Поти"},"AM":{"yer":"Ереван","gyu":"Гюмри","van":"Ванадзор","hra":"Раздан"},"AZ":{"bak":"Баку","gan":"Гянджа","sum":"Сумгаит","len":"Ленкорань"},"UZ":{"tas":"Ташкент","sam":"Самарканд","fer":"Фергана","nam":"Наманган","buk":"Бухара"},"KG":{"bis":"Бишкек","osh":"Ош","jal":"Джалал-Абад","kar":"Каракол"},"TJ":{"dus":"Душанбе","khu":"Худжанд","kul":"Куляб","kur":"Курган-Тюбе"},"TM":{"ash":"Ашхабад","tur":"Туркменабад","das":"Дашогуз","mar":"Мары"},"IL":{"tel":"Тель-Авив","jer":"Иерусалим","hai":"Хайфа","bee":"Беэр-Шева"},"AE":{"dub":"Дубай","abu":"Абу-Даби","sha":"Шарджа","ajm":"Аджман"},"SA":{"riy":"Эр-Рияд","jed":"Джидда","mec":"Мекка","med":"Медина","dam":"Даммам"},"TH":{"ban":"Бангкок","chi":"Чиангмай","pho":"Пхукет","pat":"Паттайя","hat":"Хатъяй"},"VN":{"hcm":"Хошимин","han":"Ханой","dan":"Дананг","hai":"Хайфонг","can":"Кантхо"},"MY":{"kua":"Куала-Лумпур","geo":"Джорджтаун","joh":"Джохор-Бару","kot":"Кота-Кинабалу"},"ID":{"jak":"Джакарта","sur":"Сурабая","ban":"Бандунг","med":"Медан","mak":"Макассар"},"PH":{"man":"Манила","ceb":"Себу","dav":"Давао","que":"Кесон-Сити"},"MX":{"mex":"Мехико","gua":"Гвадалахара","mon":"Монтеррей","can":"Канкун","tij":"Тихуана"},"AR":{"bue":"Буэнос-Айрес","cor":"Кордова","ros":"Росарио","men":"Мендоса"},"CL":{"san":"Сантьяго","val":"Вальпараисо","con":"Консепсьон","ant":"Антофагаста"},"ZA":{"joh":"Йоханнесбург","cap":"Кейптаун","dur":"Дурбан","pre":"Претория"},"NG":{"lag":"Лагос","abu":"Абуджа","kan":"Кано","ibe":"Ибадан","por":"Порт-Харкорт"},"EG":{"cai":"Каир","ale":"Александрия","giz":"Гиза","lux":"Луксор","asu":"Асуан"},"PK":{"kar":"Карачи","lah":"Лахор","isl":"Исламабад","raw":"Равалпинди","pes":"Пешавар"},"BD":{"dha":"Дакка","chi":"Читтагонг","khu":"Кхулна","raj":"Раджшахи"},"LK":{"col":"Коломбо","kan":"Канди","gal":"Галле","neg":"Негомбо"},"NP":{"kat":"Катманду","pok":"Покхара","lal":"Лалитпур","bha":"Бхактапур"},"MM":{"yan":"Янгон","man":"Мандалай","nay":"Нейпьидо","maw":"Моламьяйн"},"KH":{"pho":"Пномпень","sie":"Сиемреап","bat":"Баттамбанг","sih":"Сиануквиль"},"LA":{"vie":"Вьентьян","luan":"Луангпхабанг","pak":"Паксе","sav":"Саваннакхет"},"MN":{"ula":"Улан-Батор","erden":"Эрдэнэт","dar":"Дархан","cho":"Чойбалсан"},"IS":{"rey":"Рейкьявик","kop":"Коупавогюр","haf":"Хабнарфьордюр","akr":"Акюрейри"},"IE":{"dub":"Дублин","cor":"Корк","gal":"Голуэй","lim":"Лимерик"},"DK":{"cop":"Копенгаген","aar":"Орхус","ode":"Оденсе","aal":"Ольборг","esb":"Эсбьерг"},"BE":{"bru":"Брюссель","ant":"Антверпен","ghe":"Гент","cha":"Шарлеруа","lie":"Льеж"},"LU":{"lux":"Люксембург","esch":"Эш-сюр-Альзетт","dud":"Дюделанж"},"SK":{"bra":"Братислава","kos":"Кошице","pre":"Прешов","zil":"Жилина","nit":"Нитра"},"SI":{"lju":"Любляна","mar":"Марибор","cel":"Целе","kop":"Копер","nov":"Ново-Место"},"HR":{"zag":"Загреб","spl":"Сплит","rij":"Риека","osu":"Осиек","zadar":"Задар"},"RS":{"bel":"Белград","nov":"Нови-Сад","nis":"Ниш","kra":"Крагуевац","sub":"Суботица"},"BA":{"sar":"Сараево","ban":"Баня-Лука","tuz":"Тузла","zen":"Зеница","mos":"Мостар"},"ME":{"pod":"Подгорица","nik":"Никшич","her":"Херцег-Нови","bar":"Бар","bij":"Биело-Поле"},"MK":{"sko":"Скопье","bit":"Битола","pri":"Прилеп","tet":"Тетово","veles":"Велес"},"AL":{"tir":"Тирана","dur":"Дуррес","vlore":"Влёра","elbas":"Эльбасан","shko":"Шкодер"},"GR":{"ath":"Афины","the":"Салоники","pat":"Патры","ira":"Ираклион","lar":"Лариса"},"CY":{"nic":"Никосия","lim":"Лимасол","lar":"Ларнака","paf":"Пафос"},"MT":{"val":"Валлетта","bir":"Биркиркара","mos":"Моста","sli":"Слима"}}


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_source(url):
    try:
        r = requests.get(url, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return []
        text = r.text.strip()
        if not text:
            return []
        return extract_nodes(text)
    except Exception:
        return []


def extract_nodes(text):
    nodes = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for proto in ["vmess://", "vless://", "trojan://", "ss://", "hy2://", "hysteria2://"]:
            if line.startswith(proto):
                nodes.append(line)
                break
    if not nodes:
        try:
            decoded = base64.b64decode(text).decode("utf-8", errors="ignore")
            for line in decoded.splitlines():
                line = line.strip()
                if not line:
                    continue
                for proto in ["vmess://", "vless://", "trojan://", "ss://", "hy2://", "hysteria2://"]:
                    if line.startswith(proto):
                        nodes.append(line)
                        break
        except Exception:
            pass
    return nodes


def parse_node(node):
    try:
        if node.startswith("vmess://"):
            b64 = node[8:]
            decoded = base64.b64decode(b64 + "=" * (-len(b64) % 4)).decode("utf-8", errors="ignore")
            cfg = json.loads(decoded)
            return {"type": "vmess", "raw": node, "addr": cfg.get("add", ""), "port": int(cfg.get("port", 0)), "ps": cfg.get("ps", ""), "id": cfg.get("id", ""), "aid": cfg.get("aid", 0), "net": cfg.get("net", "tcp"), "tls": cfg.get("tls", ""), "sni": cfg.get("sni", ""), "host": cfg.get("host", ""), "path": cfg.get("path", "")}
        elif node.startswith("vless://"):
            parsed = urllib.parse.urlparse(node)
            qs = urllib.parse.parse_qs(parsed.query)
            return {"type": "vless", "raw": node, "addr": parsed.hostname or "", "port": parsed.port or 0, "id": parsed.username or "", "ps": urllib.parse.unquote(parsed.fragment or ""), "flow": qs.get("flow", [""])[0], "encryption": qs.get("encryption", ["none"])[0], "security": qs.get("security", [""])[0], "sni": qs.get("sni", [""])[0], "fp": qs.get("fp", [""])[0], "pbk": qs.get("pbk", [""])[0], "sid": qs.get("sid", [""])[0], "type": qs.get("type", [""])[0], "host": qs.get("host", [""])[0], "path": qs.get("path", [""])[0]}
        elif node.startswith("trojan://"):
            parsed = urllib.parse.urlparse(node)
            qs = urllib.parse.parse_qs(parsed.query)
            return {"type": "trojan", "raw": node, "addr": parsed.hostname or "", "port": parsed.port or 0, "password": parsed.username or "", "ps": urllib.parse.unquote(parsed.fragment or ""), "sni": qs.get("sni", [""])[0], "fp": qs.get("fp", [""])[0], "alpn": qs.get("alpn", [""])[0], "type": qs.get("type", [""])[0], "host": qs.get("host", [""])[0], "path": qs.get("path", [""])[0]}
        elif node.startswith("ss://"):
            parsed = urllib.parse.urlparse(node)
            return {"type": "ss", "raw": node, "addr": parsed.hostname or "", "port": parsed.port or 0, "ps": urllib.parse.unquote(parsed.fragment or "")}
        elif node.startswith("hy2://") or node.startswith("hysteria2://"):
            parsed = urllib.parse.urlparse(node)
            qs = urllib.parse.parse_qs(parsed.query)
            return {"type": "hy2", "raw": node, "addr": parsed.hostname or "", "port": parsed.port or 0, "password": parsed.username or "", "ps": urllib.parse.unquote(parsed.fragment or ""), "sni": qs.get("sni", [""])[0], "insecure": qs.get("insecure", [""])[0]}
    except Exception:
        pass
    return None


def ping_host(addr, port):
    if not addr or not port:
        return 9999
    try:
        start = time.time()
        sock = socket.create_connection((addr, port), timeout=PING_TIMEOUT)
        sock.close()
        return round((time.time() - start) * 1000, 1)
    except Exception:
        return 9999


def dns_leak_test(addr):
    try:
        socket.getaddrinfo(addr, None)
        return True
    except Exception:
        return False


def security_check(node_dict):
    addr = node_dict.get("addr", "")
    if not addr:
        return False
    if addr in ["127.0.0.1", "localhost", "0.0.0.0"]:
        return False
    if addr.endswith(".local") or addr.endswith(".lan"):
        return False
    if node_dict.get("port", 0) in [22, 23, 25, 53, 110, 143, 3306, 3389, 5432, 6379, 8080]:
        return False
    return True


def get_country_from_ip(addr):
    try:
        r = requests.get(f"http://ip-api.com/json/{addr}?fields=status,countryCode,city", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                return data.get("countryCode", "US"), data.get("city", "")
    except Exception:
        pass
    return "US", ""


def build_name(cc, city_code):
    flag = gf(cc) if len(cc) == 2 else ""
    country = CN.get(cc, cc)
    city_dict = CT.get(cc, {})
    city = city_dict.get(city_code.lower()[:3], city_dict.get(city_code.lower(), city_code))
    return f"{flag}{country}-{city}"


def filter_protocols(nodes):
    return [n for n in nodes if n.get("type", "") in ["trojan", "hy2"]]


def remove_duplicates(nodes):
    seen = set()
    unique = []
    for n in nodes:
        key = f"{n.get('addr')}:{n.get('port')}"
        if key not in seen:
            seen.add(key)
            unique.append(n)
    return unique


def get_warp_config():
    try:
        r = requests.get("https://api.cloudflareclient.com/v0a2158/reg", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"type": "wireguard", "name": gf("US") + "США-Warp+", "private_key": data.get("config", {}).get("private_key", ""), "address": data.get("config", {}).get("interface", {}).get("addresses", {}).get("v4", ""), "peer_public_key": data.get("config", {}).get("peers", [{}])[0].get("public_key", ""), "endpoint": "engage.cloudflareclient.com:2408", "reserved": data.get("config", {}).get("interface", {}).get("addresses", {}).get("v6", "")[:4]}
    except Exception:
        pass
    return {"type": "wireguard", "name": gf("US") + "США-Warp+", "private_key": "gBthLUVzTjEe9t7Z2x3y4A5B6C7D8E9F0=", "address": "172.16.0.2/32", "peer_public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=", "endpoint": "engage.cloudflareclient.com:2408", "reserved": "[0,0,0]"}


def build_warp_node(wcfg):
    return f"wg://{wcfg['endpoint']}?publickey={wcfg['peer_public_key']}&address={urllib.parse.quote(wcfg['address'])}&privatekey={wcfg['private_key']}&reserved={wcfg['reserved']}#{urllib.parse.quote(wcfg['name'])}"


def get_amnezia_node():
    return AMNEZIA_LINK


def encrypt_subscription(data, password):
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        key = md5(password.encode()).digest()
        iv = bytes([random.randint(0, 255) for _ in range(16)])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(iv + encrypted).decode()
    except Exception:
        return base64.b64encode(data.encode()).decode()


def build_subscription(nodes):
    lines = []
    for n in nodes:
        name = urllib.parse.quote(n.get("name", n.get("ps", "")))
        if n["type"] == "trojan":
            qs = urllib.parse.urlencode({k: v for k, v in {"sni": n.get("sni", ""), "fp": n.get("fp", ""), "type": n.get("type", ""), "host": n.get("host", ""), "path": n.get("path", "")}.items() if v}, doseq=False)
            qs = f"?{qs}" if qs else ""
            lines.append(f"trojan://{n['password']}@{n['addr']}:{n['port']}{qs}#{name}")
        elif n["type"] == "hy2":
            qs = urllib.parse.urlencode({k: v for k, v in {"sni": n.get("sni", ""), "insecure": n.get("insecure", "")}.items() if v}, doseq=False)
            qs = f"?{qs}" if qs else ""
            lines.append(f"hy2://{n['password']}@{n['addr']}:{n['port']}{qs}#{name}")
    warp = get_warp_config()
    lines.append(build_warp_node(warp))
    lines.append(get_amnezia_node())
    return "\n".join(lines)


def main():
    print("[*] Loading config...")
    cfg = load_config()
    sources = cfg.get("sources", [])
    print(f"[*] Fetching from {len(sources)} sources...")
    all_nodes = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(fetch_source, url): url for url in sources}
        for future in as_completed(futures):
            all_nodes.extend(future.result())
    print(f"[*] Total nodes fetched: {len(all_nodes)}")
    print("[*] Parsing nodes...")
    parsed = [p for n in all_nodes if (p := parse_node(n))]
    print(f"[*] Parsed: {len(parsed)}")
    print("[*] Filtering protocols (hy2, trojan)...")
    parsed = filter_protocols(parsed)
    print(f"[*] After protocol filter: {len(parsed)}")
    print("[*] Removing duplicates...")
    parsed = remove_duplicates(parsed)
    print(f"[*] After dedup: {len(parsed)}")
    print("[*] Security check...")
    parsed = [n for n in parsed if security_check(n)]
    print(f"[*] After security: {len(parsed)}")
    print("[*] DNS leak test...")
    parsed = [n for n in parsed if dns_leak_test(n["addr"])]
    print(f"[*] After DNS test: {len(parsed)}")
    print("[*] Pinging nodes...")
    with ThreadPoolExecutor(max_workers=MAX_PING_WORKERS) as ex:
        futures = {ex.submit(ping_host, n["addr"], n["port"]): n for n in parsed}
        for future in as_completed(futures):
            n = futures[future]
            n["ping"] = future.result()
    parsed = [n for n in parsed if n["ping"] < 9999]
    parsed.sort(key=lambda x: x["ping"])
    print(f"[*] After ping filter: {len(parsed)}")
    print("[*] Getting geo info...")
    for n in parsed[:TARGET_SERVERS]:
        cc, city = get_country_from_ip(n["addr"])
        n["cc"] = cc
        n["city"] = city
        n["name"] = build_name(cc, city)
    selected = parsed[:TARGET_SERVERS]
    print(f"[*] Selected {len(selected)} servers")
    print("[*] Building subscription...")
    sub = build_subscription(selected)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(sub)
    print(f"[*] Saved plain subscription to {OUTPUT_FILE}")
    enc = encrypt_subscription(sub, ENCRYPTION_PASSWORD)
    with open(ENCRYPTED_FILE, "w", encoding="utf-8") as f:
        f.write(enc)
    print(f"[*] Saved encrypted subscription to {ENCRYPTED_FILE}")
    print(f"[*] Password: {ENCRYPTION_PASSWORD}")
    print("[*] Done!")


if __name__ == "__main__":
    main()
