## Project summary

**Simple Port Scanner (Python)** — a small educational tool that scans TCP ports (with optional UDP), performs basic banner grabbing, and can output results as JSON. Built to demonstrate core networking concepts (sockets, ports), I/O concurrency with threads, and safe testing practices.

**Key points**
- Safe demo outputs in `/examples/` were produced by scanning **localhost** only and have been sanitized (IP addresses replaced with `xx.xxx.xxx`). Do **not** scan systems you do not own or have permission to test.
- Run locally with:  
  `python3 -m http.server 8000 --bind localhost` (server)  
  `python3 port_scanner.py --host localhost --start 7990 --end 8010 --threads 50 --timeout 1.0 --banner`

**Tech stack**
- Language: Python 3  
- Standard libs: `socket`, `argparse`, `json`, `datetime`  
- Concurrency: `concurrent.futures.ThreadPoolExecutor` (threads)  
- No external dependencies; runs on a standard Python 3 install.

