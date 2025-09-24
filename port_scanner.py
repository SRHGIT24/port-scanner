# ===============================================n# Simple Port Scanner (Educational Demo)n# Author: Your Namen# Usage: python3 port_scanner.py --host localhost --start 7990 --end 8010n# NOTE: Run this only on your own machine (localhost).n# IPs in example outputs are sanitized (xx.xxx.xxx).n# ===============================================n
#!/usr/bin/env python3
# Simple multithreaded port scanner with optional banner grabbing and JSON output.
# Safe-demo note: test on localhost (localhost) only.
import socket, argparse, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def scan_tcp_port(host_ip, port, timeout=0.8, do_banner=False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        code = s.connect_ex((host_ip, port))
        if code == 0:
            banner = None
            if do_banner:
                try:
                    s.settimeout(0.6)
                    data = s.recv(1024)
                    banner = data.decode('utf-8', errors='replace').strip() if data else None
                except Exception:
                    banner = None
            s.close()
            return port, True, banner
        s.close()
        return port, False, None
    except Exception:
        try: s.close()
        except Exception: pass
        return port, False, None

def scan_udp_port(host_ip, port, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(b'', (host_ip, port))
        try:
            s.recvfrom(1024)
            s.close()
            return port, True
        except socket.timeout:
            s.close()
            return port, False
    except Exception:
        try: s.close()
        except Exception: pass
        return port, False

def main():
    p = argparse.ArgumentParser(description="Simple enhanced port scanner")
    p.add_argument('--host', required=True, help='Target host (e.g. localhost)')
    p.add_argument('--start', type=int, default=1)
    p.add_argument('--end', type=int, default=1024)
    p.add_argument('--threads', type=int, default=200)
    p.add_argument('--udp', action='store_true')
    p.add_argument('--timeout', type=float, default=0.8)
    p.add_argument('--banner', action='store_true')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    try:
        ip = socket.gethostbyname(args.host)
    except Exception as e:
        print(f"Unable to resolve {args.host}: {e}")
        return

    ports = list(range(args.start, args.end + 1))
    print(f"Scanning {args.host} ({ip}) ports {args.start}-{args.end} with {args.threads} threads. UDP={args.udp} banner={args.banner}")
    t0 = datetime.now()
    results = {'host': args.host, 'ip': ip, 'start_port': args.start, 'end_port': args.end,
               'scan_start': t0.isoformat(), 'open_tcp': [], 'open_udp': []}

    # TCP scan
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futs = {ex.submit(scan_tcp_port, ip, p, args.timeout, args.banner): p for p in ports}
        for f in as_completed(futs):
            port, open_, banner = f.result()
            if open_:
                entry = {'port': port}
                if args.banner and banner:
                    entry['banner'] = banner
                results['open_tcp'].append(entry)

    # UDP (optional)
    if args.udp:
        with ThreadPoolExecutor(max_workers=args.threads) as ex:
            futs = {ex.submit(scan_udp_port, ip, p, args.timeout + 0.2): p for p in ports}
            for f in as_completed(futs):
                port, open_ = f.result()
                if open_:
                    results['open_udp'].append({'port': port})

    elapsed = (datetime.now() - t0).total_seconds()
    results['scan_end'] = datetime.now().isoformat()
    results['elapsed_seconds'] = elapsed

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nScan completed in {elapsed:.2f}s")
        if results['open_tcp']:
            print("Open TCP ports:")
            for e in sorted(results['open_tcp'], key=lambda x: x['port']):
                line = f" - {e['port']}"
                if 'banner' in e and e['banner']:
                    line += f"  banner: {e['banner']}"
                print(line)
        else:
            print("No open TCP ports found (in the scanned range).")
        if args.udp:
            if results['open_udp']:
                print("Open UDP ports (best-effort):", ', '.join(str(e['port']) for e in results['open_udp']))
            else:
                print("No open UDP ports discovered (or filtered).")

if __name__ == '__main__':
    main()
