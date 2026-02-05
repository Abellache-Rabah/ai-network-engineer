from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List
import ipaddress
import json
import os

mcp = FastMCP("IPAM Server")

DB_FILE = os.path.join(os.path.dirname(__file__), "ipam_db.json")

def load_db():
    if not os.path.exists(DB_FILE):
        return {"subnets": {}, "allocations": {}}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@mcp.tool()
def add_subnet(name: str, cidr: str) -> str:
    """
    Register a new subnet in the IPAM database.
    
    Args:
        name: A descriptive alias (e.g., 'workstations').
        cidr: The network address in CIDR notation (e.g., '192.168.1.0/24').
    """
    db = load_db()
    try:
        ipaddress.ip_network(cidr)
    except ValueError:
        return f"Error: Invalid CIDR {cidr}"
        
    db["subnets"][name] = cidr
    save_db(db)
    return f"Added subnet {name}: {cidr}"

@mcp.tool()
def list_subnets() -> Dict[str, str]:
    """List all managed subnets."""
    db = load_db()
    return db["subnets"]

@mcp.tool()
def get_subnet_usage(subnet_name: str) -> str:
    """Calculate usage for a specific subnet."""
    db = load_db()
    subnets = db["subnets"]
    allocations = db["allocations"]
    
    if subnet_name not in subnets:
        return f"Error: Subnet '{subnet_name}' not found."
    
    cidr = subnets[subnet_name]
    net = ipaddress.ip_network(cidr)
    total_hosts = net.num_addresses - 2 # exclude net/broadcast
    
    used_count = 0
    for ip in allocations:
        if ipaddress.ip_address(ip) in net:
            used_count += 1
            
    usage_percent = (used_count / total_hosts) * 100 if total_hosts > 0 else 0
    return f"Subnet {subnet_name} ({cidr}): {used_count}/{total_hosts} used ({usage_percent:.1f}%)"

@mcp.tool()
def allocate_ip(subnet_name: str, description: str) -> str:
    """
    Allocates the NEXT available IP address in a subnet.
    
    Args:
        subnet_name: The descriptive alias of the subnet.
        description: A note about what this IP is for (e.g., 'PC3').
        
    Returns:
        str: The allocated IP address or an error if subnet is full.
    """
    db = load_db()
    subnets = db["subnets"]
    allocations = db["allocations"]
    
    if subnet_name not in subnets:
        return f"Error: Subnet '{subnet_name}' not found."

    cidr = subnets[subnet_name]
    net = ipaddress.ip_network(cidr)
    
    # Simple sequential scan
    for ip in net.hosts():
        ip_str = str(ip)
        if ip_str not in allocations:
            allocations[ip_str] = description
            save_db(db)
            return f"Allocated {ip_str} for '{description}' in {subnet_name}"
            
    return f"Error: No IPs available in {subnet_name}"

@mcp.resource("ipam://subnets/list")
def resource_subnets() -> str:
    """Returns a textual list of subnets and their CIDRs."""
    db = load_db()
    subnets = db["subnets"]
    output = ["IPAM Managed Subnets:"]
    for name, cidr in subnets.items():
        output.append(f"- {name}: {cidr}")
    return "\n".join(output)

if __name__ == "__main__":
    # Ensure DB exists
    if not os.path.exists(DB_FILE):
        save_db({"subnets": {}, "allocations": {}})
    mcp.run()
