#!/usr/bin/env python3
import requests
import yaml
import json
import base64
from datetime import datetime
import os

def convert_v2ray_to_clash(v2ray_url):
    """Convert V2Ray URL to Clash format"""
    try:
        if v2ray_url.startswith('vmess://'):
            encoded_data = v2ray_url[8:]
            padding = 4 - len(encoded_data) % 4
            if padding != 4:
                encoded_data += '=' * padding
            
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            v2ray_config = json.loads(decoded_data)
            
            clash_config = {
                'name': v2ray_config.get('ps', f"vmess-{v2ray_config.get('add', 'server')}").replace(' ', '-'),
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

def fetch_v2ray_sources():
    """Fetch from multiple free V2Ray sources"""
    sources = {
        'free_v2ray': 'https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/vmess_configs.txt',
        'v2ray_list': 'https://raw.githubusercontent.com/mianfeifq/share/main/data2024101.txt',
        'free_config': 'https://raw.githubusercontent.com/freefq/free/master/v2'
    }
    
    all_proxies = []
    
    for source_name, url in sources.items():
        try:
            print(f"Fetching from {source_name}...")
            response = requests.get(url, timeout=10)
            v2ray_urls = response.text.strip().split('\n')
            
            for v2ray_url in v2ray_urls:
                if v2ray_url.strip().startswith('vmess://'):
                    clash_config = convert_v2ray_to_clash(v2ray_url.strip())
                    if clash_config and clash_config['server']:
                        # Add source tag to name
                        clash_config['name'] = f"{source_name}-{clash_config['name']}"[:50]
                        all_proxies.append(clash_config)
                        
            print(f"✓ {source_name}: {len([x for x in all_proxies if x['name'].startswith(source_name)])} proxies")
            
        except Exception as e:
            print(f"✗ Failed to fetch {source_name}: {e}")
    
    return all_proxies

def main():
    print("🚀 Starting proxy update...")
    
    # Fetch all proxies
    all_proxies = fetch_v2ray_sources()
    
    if all_proxies:
        # Remove duplicates based on server+port
        unique_proxies = []
        seen = set()
        
        for proxy in all_proxies:
            key = (proxy['server'], proxy['port'])
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        print(f"📊 Total unique proxies: {len(unique_proxies)}")
        
        # Create akun.yaml
        akun_config = {
            'proxies': unique_proxies,
            'proxy-groups': [
                {
                    'name': '🚀 AUTO-SELECT',
                    'type': 'url-test',
                    'proxies': [p['name'] for p in unique_proxies],
                    'url': 'http://www.gstatic.com/generate_204',
                    'interval': 300
                },
                {
                    'name': '🌐 PROXY',
                    'type': 'select',
                    'proxies': [p['name'] for p in unique_proxies] + ['DIRECT', 'REJECT']
                }
            ]
        }
        
        # Save akun.yaml
        with open('akun.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(akun_config, f, allow_unicode=True, sort_keys=False)
        
        # Save individual provider files
        with open('providers/free_v2ray.yaml', 'w', encoding='utf-8') as f:
            yaml.dump({'proxies': unique_proxies}, f, allow_unicode=True)
        
        print("✅ Update completed successfully!")
    else:
        print("❌ No proxies were fetched")

if __name__ == "__main__":
    main()
