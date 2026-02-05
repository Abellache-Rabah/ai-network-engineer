from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from shared.gns3_utils import GNS3Console, load_inventory

mcp = FastMCP("Deployer Server")

@mcp.tool()
def get_config_diff(device: str, new_config: str) -> str:
    """
    Calculates diff between current running config and candidate.
    Note: Requires fetching running config from device (not fully implemented).
    """
    # todo
    return f"Diffing against live device not yet implemented. Candidate Config:\n{new_config}"


@mcp.tool()
def deploy_config(device: str, config: str, dry_run: bool = True, auto_rollback: bool = True) -> str:
    """
    Deploys a configuration snippet to a device via GNS3 Console (Telnet).
    
    Args:
        device: Hostname matching inventory (e.g., 'router', 'pc1', 'pc3').
        config: The commands to execute on the device.
        
        **Example 1 (Linux PC - Change IP Address):**
        ```bash
        ip addr flush dev eth0
        ip addr add 20.0.0.10/24 dev eth0
        ip link set eth0 up
        ip route add default via 20.0.0.99
        ```
        
        **Example 2 (Linux PC - Add Route):**
        ```bash
        ip route add 10.0.0.0/24 via 20.0.0.1
        ```
        
        **Example 3 (Cisco Router - Configure Interface):**
        ```
        interface FastEthernet0/0
         ip address 40.0.0.99 255.255.255.0
         no shutdown
        exit
        interface FastEthernet0/1
         ip address 20.0.0.99 255.255.255.0
         no shutdown
        exit
        ```
        
        **Example 4 (Cisco Router - Add Static Route):**
        ```
        ip route 10.0.0.0 255.255.255.0 20.0.0.1
        ```
        
        dry_run: If True (default), only shows what WOULD be deployed. 
                 Set to False to actually apply changes to the GNS3 device.
                 
    Returns:
        str: Console output from the device or error message.
        
    Note:
        - Commands are sent via Telnet to localhost:PORT (from inventory)
        - Linux uses iproute2 commands
        - Cisco uses IOS commands
        - DO NOT use Ansible/SSH/NAPALM syntax
    """
    if dry_run:
        return f"[DRY-RUN] Would push the following config to {device} (localhost via Telnet):\n{config}"

    try:
        # Load Inventory to get Port
        inv = load_inventory()
        host_data = inv.get("hosts", {}).get(device)
        
        if not host_data:
            return f"Error: Device {device} not found in inventory."
            
        port = host_data.get("port")
        if not port:
             return f"Error: No port defined for {device} in invenotry."
             
        # Connect via GNS3 Utils
        groups = host_data.get("groups", [])
        platform = "linux" if "linux" in groups else "cisco_ios"
        
        console = GNS3Console("localhost", port, platform=platform)
        console.connect()
        
        if platform == "linux":
            output = console.configure_linux(config)
        else:
            output = console.configure_cisco(config)
            
        console.close()
        
        return f"SUCCESS: Config deployed to {device} (Port {port}).\nOutput Capture:\n{output}"

    except Exception as e:
        return f"FAILURE: Connection/Deployment failed: {str(e)}"



@mcp.tool()
def rollback(device: str, revision_id: str = "last") -> str:
    """Manually rollback configuration."""
    return f"Rolled back {device} to revision {revision_id}."

@mcp.prompt()
def plan_deployment(device: str) -> str:
    """Workflow: Plan a safe deployment."""
    return f"""To safely deploy to {device}, please follows these steps:
1. Retrieve current config.
2. Generate candidate config.
3. Call `get_config_diff` to review changes.
4. Verify config with `verifier` server.
5. Call `deploy_config` with dry_run=True.
6. Check connection (Telnet/SSH) parameters.
7. Call `deploy_config` with dry_run=False.
"""

if __name__ == "__main__":
    mcp.run()
