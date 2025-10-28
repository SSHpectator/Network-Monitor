import psutil
from rich.console import Console
from rich.table import Table

def lister():
    conn = psutil.net_connections(kind="inet4")
    
    rows = []
    for c in conn:
        laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
        raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ""

        rows.append({
            "local":laddr,
            "remote":raddr
            })

    return rows

import requests
def retrieve_ip_owner(ip):

    base_path = f"http://ip-api.com/json/{ip}"

    try:
        req = requests.get(base_path, timeout=(2,3)) #(connessione, risposta)
        
        data = req.json()
        if data.get("status") == "success" and ip != "127.0.0.1":
            return data.get("org") or data.get("isp") or "Nothing"
        elif ip=="127.0.0.1" or ip=="192.168.1.1":
            return "Local Host"
        else:
            return "Unknown\n"
    except requests.exceptions.Timeout:
        return "Timeout"
    except Exception as e:
        return f"Error {e}\n"

def main():
    console = Console()
    table = Table(title="Network Monitor Tool")

    table.add_column("Local IP", justify="left", style="cyan", no_wrap=True)
    table.add_column("Remote IP", style="magenta")
    table.add_column("Org/ISP", justify="center", style="red")

    """
    Use cache to store in a dict 
    ip already seen, to sped up
    """
    cache = {}
    for r in lister():
        if not r['remote']:
            continue
        remote = r['remote']
        ip = remote.split(":",1)[0]
        
        if ip in cache:
            org = cache[ip]
        else:
            org = retrieve_ip_owner(ip)
            cache[ip] = org
        table.add_row(f"{r['local']}",f"{remote}",f"{org}")
    
    console.print(table)

if __name__ == "__main__":
    main()