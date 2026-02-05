from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from shared.gns3_utils import GNS3Console, load_inventory

mcp = FastMCP("Observer Server")

@mcp.tool()
def check_reachability(source_device: str, target_ip: str) -> str:
    """
    Checks ping reachability from a source device to a target IP.
    
    Args:
        source_device: Name of the device to ping FROM (must exist in inventory).
        target_ip: IP address to ping TO.
        
    Returns:
        str: SUCCESS or FAILURE message with raw ping output.
    """
    try:
        inv = load_inventory()
        host_data = inv.get("hosts", {}).get(source_device)
        if not host_data:
            return f"Error: Device {source_device} not in inventory."
            
        port = host_data.get("port")
        groups = host_data.get("groups", [])
        platform = "linux" if "linux" in groups else "cisco_ios"
        
        console = GNS3Console("localhost", port, platform=platform)
        console.connect()
        output = console.ping(target_ip)
        console.close()
        
        # Analyze output
        success = False
        if "!!!!" in output or "bytes from" in output or "0% packet loss" in output:
             success = True
             
        if success:
            return f"SUCCESS: {output}"
        else:
            return f"FAILURE: {output}"

    except Exception as e:
        return f"Error running ping: {str(e)}"

@mcp.tool()
def get_interface_health(device: str, interface: str) -> str:
    """
    Retrieves the operational status and protocol status of an interface.
    
    Args:
        device: Hostname in inventory.
        interface: Exact interface name (e.g., 'FastEthernet0/0').
        
    Returns:
        str: Status details (up/down/admin down) or error message.
    """
    try:
        inv = load_inventory()
        host_data = inv.get("hosts", {}).get(device)
        if not host_data:
            return f"Error: Device {device} not found in inventory."
            
        port = host_data.get("port")
        groups = host_data.get("groups", [])
        platform = "linux" if "linux" in groups else "cisco_ios"
        
        console = GNS3Console("localhost", port, platform=platform)
        console.connect()
        
        # Get real interfaces
        real_interfaces = console.get_interfaces()
        console.close()
        
        if not real_interfaces:
            # Fallback for Linux or if parsing failed
            if platform == "linux":
                return "Linux interface health check not implemented yet (use ping)."
            return "Error: Could not retrieve interfaces from Router."

        # Find requested interface
        # Try exact match first
        target = next((i for i in real_interfaces if i["name"] == interface), None)
        
        if not target:
            available_names = [i["name"] for i in real_interfaces]
            return f"Error: Interface '{interface}' not found. Available interfaces: {', '.join(available_names)}"
            
        status = target["status"]
        protocol = target["protocol"]
        return f"Interface {interface}: Status={status}, Protocol={protocol}. IP={target['ip']}."

    except Exception as e:
        return f"Error connecting to device: {str(e)}"

@mcp.tool()
def detect_link_failures() -> List[str]:
    """
    Compares live state against inventory.
    """
    failures = []
    try:
        inv = load_inventory()
        hosts = inv.get("hosts", {})
        
        for dev_name, data in hosts.items():
            groups = data.get("groups", [])
            # Only check Cisco routers for now as they support get_interfaces
            if "cisco" not in groups:
                 continue

            res = get_interface_health(dev_name, "Ethernet0/0") # Basic check for main interface?
            # Ideally we check ALL interfaces expected to be up. 
            # This is a simplification.
            if "Error" in res or "down" in res.lower():
                 failures.append(f"Issue on {dev_name}: {res}")
                 
    except Exception as e:
        return [f"Error running failure detection: {str(e)}"]

    if not failures:
        return ["All monitored devices appear reachable/healthy."]
    return failures

@mcp.prompt()
def monitor_critical_links() -> str:
    """Workflow: Monitor network health."""
    return """
1. Call `librarian` to get `topology/definition`.
2. Call `detect_link_failures`.
3. If failures found, Plan fix.
    """

if __name__ == "__main__":
    mcp.run()
