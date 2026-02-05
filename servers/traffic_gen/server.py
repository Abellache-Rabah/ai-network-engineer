from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import time
import sys
import os
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from shared.gns3_utils import GNS3Console, load_inventory

mcp = FastMCP("TrafficGen Server")

def get_device_connection_info(device_name):
    inv = load_inventory()
    host_data = inv.get("hosts", {}).get(device_name)
    if not host_data:
        raise ValueError(f"Device {device_name} not found in inventory")
    return host_data.get("hostname", "localhost"), host_data.get("port"), host_data.get("groups", [])

@mcp.tool()
def start_traffic_server(host: str, port: int = 5201) -> str:
    """
    Starts an iperf3 server daemon on the specified host.
    
    Args:
        host: Hostname of the device (MUST be a Linux host in inventory).
        port: Port to listen on (default 5201).
        
    Returns:
        str: Status message indicating success or failure.
    """
    try:
        hostname, console_port, groups = get_device_connection_info(host)
        if "linux" not in groups:
            return f"Error: {host} is not a Linux device. Cannot run iperf3."
            
        console = GNS3Console(hostname, console_port, platform="linux")
        console.connect()
        # Run in background/daemon mode
        console.send_command(f"iperf3 -s -p {port} -D") 
        console.close()
        return f"Started iperf3 server on {host} (Port {port}) via daemon."
    except Exception as e:
        return f"Error starting server on {host}: {str(e)}"

@mcp.tool()
def run_traffic_test(client: str, server_ip: str, duration: int = 5, bandwidth: str = "10M") -> str:
    """
    Runs an iperf3 client traffic test from a client device to a server IP.
    
    Args:
        client: Hostname of the Linux device to run the test FROM.
        server_ip: IP address of the iperf3 server to connect TO.
        duration: Duration of the test in seconds (default 5).
        bandwidth: Target bandwidth with unit (e.g., '10M', '1G').
        
    Returns:
        str: The raw iperf3 output.
    """
    try:
        hostname, console_port, groups = get_device_connection_info(client)
        if "linux" not in groups:
            return f"Error: {client} is not a Linux device."
            
        console = GNS3Console(hostname, console_port, platform="linux")
        console.connect()
        
        # Build command
        # iperf3 -c <server> -t <duration> -b <bandwidth>
        cmd = f"iperf3 -c {server_ip} -t {duration} -b {bandwidth}"
        output = console.send_command(cmd, wait_time=duration + 2)
        console.close()
        
        return f"Traffic Test Result:\n{output}"
    except Exception as e:
        return f"Error running test on {client}: {str(e)}"

@mcp.resource("traffic://last_test_result")
def get_last_result() -> str:
    """Returns the result of the last run test."""
    return "No test run yet (Persistence not implemented)."

@mcp.prompt()
def stress_test_link() -> str:
    """Workflow: Verify link capacity."""
    return """
1. Identify server and client hosts on ends of the link.
2. `start_traffic_server(server)`.
3. `run_traffic_test(client, server_ip)`.
4. Validate bandwidth matches expectation.
"""

if __name__ == "__main__":
    mcp.run()
