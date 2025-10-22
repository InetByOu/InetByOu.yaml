import requests, yaml, base64, json

URL = "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/vmess_configs.txt"

def parse_vmess(line):
    if not line.startswith("vmess://"):
        return None
    data = json.loads(base64.b64decode(line[8:]).decode())
    return {
        "name": data.get("ps", "Unnamed"),
        "type": "vmess",
        "server": data.get("add"),
        "port": int(data.get("port", 443)),
        "uuid": data.get("id"),
        "alterId": int(data.get("aid", 0)),
        "cipher": "auto",
        "tls": True if data.get("tls") == "tls" else False,
        "network": data.get("net", "tcp"),
        "udp": True,
        "skip-cert-verify": True
    }

def main():
    text = requests.get(URL).text.strip().splitlines()
    proxies = [parse_vmess(line) for line in text if line.startswith("vmess://")]
    proxies = [p for p in proxies if p]

    akun_yaml = {"proxies": proxies}
    with open("akun.yaml", "w") as f:
        yaml.dump(akun_yaml, f, allow_unicode=True)

    config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": True,
        "mode": "Rule",
        "log-level": "info",
        "external-controller": "127.0.0.1:9090",
        "proxy-groups": [{
            "name": "AUTO",
            "type": "select",
            "proxies": [p["name"] for p in proxies]
        }],
        "rules": [
            "MATCH,AUTO"
        ]
    }
    with open("config.yaml", "w") as f:
        yaml.dump(config, f, allow_unicode=True)

if __name__ == "__main__":
    main()
