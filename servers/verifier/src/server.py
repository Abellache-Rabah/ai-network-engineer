from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import logging

# Relative imports if running as package, but for direct script execution we might need path hacks
# or just assume running from root with `python -m src.server`
try:
    from .batfish_utils import BatfishConnector
    from .host_utils import verify_host_config as verify_host
except ImportError:
    # Fallback for when running directly or if package structure varies
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from batfish_utils import BatfishConnector
    from host_utils import verify_host_config as verify_host

# Initialize FastMCP
mcp = FastMCP("Network Verifier")

# Initialize Batfish Connector
# TODO: Get host from environment variable
BATFISH_HOST = "localhost"
bf_connector = BatfishConnector(host=BATFISH_HOST)

@mcp.tool()
def verify_device_config(config_content: str, hostname: str = "device1", platform: str = "cisco_ios") -> str:
    """
    Verifies a network device configuration using Batfish.
    
    Args:
        config_content: The full text of the configuration file to analyze.
        hostname: A name for the device (used for internal file naming).
        platform: The platform of the device. Supported:
                  - 'cisco_ios'
                  - 'juniper'
                  - 'arista'
                  - 'cisco_nxos'
    
    Returns:
        str: A JSON-formatted string containing verification feedback, 
             including parsing errors and structural warnings.
    """
    try:
        # Determine filename extension based on platform
        ext = ".cfg"
        if "juniper" in platform.lower():
            ext = ".conf"
        
        filename = f"{hostname}{ext}"
        
        results = bf_connector.verify_config(config_content, filename=filename, platform=platform)
        
        # Format output for the user
        if results["status"] == "error":
            return f"Error connecting to Batfish or initializing snapshot: {results['message']}"
        
        output = []
        output.append(f"Analysis for {hostname} ({platform}):")
        
        # Check parsing
        parse_status = results.get("parse_status", [])
        if parse_status:
            for item in parse_status:
                status = item.get('Status', 'Unknown')
                output.append(f"- Parse Status: {status}")
                if status != 'PASSED':
                     output.append(f"  File: {item.get('File_Name')}")
        
        # Check specific issues
        issues = results.get("issues", [])
        if issues:
            output.append("- Issues Found:")
            for issue in issues:
                output.append(f"  Line {issue.get('Line')}: {issue.get('Description')}")
        else:
            output.append("- No initialization issues found.")

        # Check for undefined references (can add this as an optional step or default)
        # undefined = bf_connector.get_undefined_references()
        # if undefined:
        #     output.append(f"- Found {len(undefined)} undefined references.")
        
        return "\n".join(output)

    except Exception as e:
        return f"Unexpected error during verification: {str(e)}"

@mcp.tool()
def verify_host_config(config_content: str, config_type: str = "netplan") -> str:
    """
    Verifies a host network configuration (e.g., Linux/Debian).
    
    Args:
        config_content: The full text of the configuration file.
        config_type: The format of the configuration. 
                     - 'netplan': For YAML netplan files.
                     - 'interfaces': For /etc/network/interfaces style.
    
    Returns:
        str: 'Configuration is VALID' or specific syntax error details.
    """
    result = verify_host(config_content, config_type)
    
    if result["valid"]:
        return f"Configuration ({config_type}) is VALID."
    else:
        errors = "\n".join([f"- {e}" for e in result["errors"]])
        return f"Configuration ({config_type}) is INVALID:\n{errors}"

if __name__ == "__main__":
    mcp.run()
