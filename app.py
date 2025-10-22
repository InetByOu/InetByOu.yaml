import requests
import yaml
import json
import base64

def convert_v2ray_to_clash(v2ray_url):
    """
    Konversi V2Ray URL ke format Clash YAML
    """
    try:
        # Decode base64 URL
        if v2ray_url.startswith('vmess://'):
            encoded_data = v2ray_url[8:]
            # Tambah padding jika perlu
            padding = 4 - len(encoded_data) % 4
            if padding != 4:
                encoded_data += '=' * padding
            
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            v2ray_config = json.loads(decoded_data)
            
            # Mapping ke format Clash
            clash_config = {
                'name': v2ray_config.get('ps', f"vmess-{v2ray_config.get('add', 'server')}"),
                'type': 'vmess',
                'server': v2ray_config.get('add'),
                'port': int(v2ray_config.get('port')),
                'uuid': v2ray_config.get('id'),
                'alterId': int(v2ray_config.get('aid', 0)),
                'cipher': 'auto',
                'tls': v2ray_config.get('tls') == 'tls',
                'network': v2ray_config.get('net', 'tcp')
            }
            
            # Handle websocket
            if v2ray_config.get('net') == 'ws':
                clash_config['ws-opts'] = {
                    'path': v2ray_config.get('path', '/'),
                    'headers': {
                        'Host': v2ray_config.get('host', '')
                    }
                }
            
            return clash_config
            
    except Exception as e:
        print(f"Error converting: {e}")
        return None

def fetch_and_convert_v2ray_list(url):
    """
    Fetch dan konversi semua config dari URL
    """
    try:
        response = requests.get(url)
        v2ray_urls = response.text.strip().split('\n')
        
        clash_proxies = []
        for v2ray_url in v2ray_urls:
            if v2ray_url.strip().startswith('vmess://'):
                clash_config = convert_v2ray_to_clash(v2ray_url.strip())
                if clash_config:
                    clash_proxies.append(clash_config)
                    print(f"✓ Converted: {clash_config['name']}")
                else:
                    print(f"✗ Failed: {v2ray_url[:50]}...")
        
        return clash_proxies
        
    except Exception as e:
        print(f"Error fetching: {e}")
        return []

# Main execution
if __name__ == "__main__":
    v2ray_list_url = "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/vmess_configs.txt"
    
    print("Fetching V2Ray configurations...")
    clash_proxies = fetch_and_convert_v2ray_list(v2ray_list_url)
    
    if clash_proxies:
        # Buat config YAML lengkap
        clash_config = {
            'proxies': clash_proxies,
            'proxy-groups': [
                {
                    'name': '🚀 AUTO-SELECT',
                    'type': 'url-test',
                    'proxies': [p['name'] for p in clash_proxies],
                    'url': 'http://www.gstatic.com/generate_204',
                    'interval': 300
                },
                {
                    'name': '🌐 PROXY',
                    'type': 'select',
                    'proxies': [p['name'] for p in clash_proxies] + ['DIRECT', 'REJECT']
                }
            ],
            'rules': [
                'GEOIP,CN,DIRECT',
                'MATCH,🌐 PROXY'
            ]
        }
        
        # Save ke file
        with open('akun.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)
        
        print(f"\n✅ Successfully converted {len(clash_proxies)} configurations to akun.yaml")
    else:
        print("❌ No configurations were converted")