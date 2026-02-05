from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List

mcp = FastMCP("Auditor Server")

# Vulnerability DB
CVE_DB = {
    "16.03.01": ["CVE-2023-1234: SSH Exploit"],
    "4.21.0F": [] # Safe
}

GOLDEN_CONFIG_RULES = [
    {"pattern": "p service password-encryption", "description": "Passwords must be encrypted"},
    {"pattern": "ntp server", "description": "NTP must be configured"},
    {"pattern": "no ip http server", "description": "HTTP server must be disabled"}
]

@mcp.tool()
def check_compliance(device_config: str) -> List[str]:
    """
    Checks device configuration against golden rules.
    
    Active Golden Rules:
    1. 'p service password-encryption' must be present.
    2. 'ntp server' must be configured.
    3. 'no ip http server' must be present.
    
    Args:
        device_config: The full running config of the device.
        
    Returns:
        list[str]: A list of violation strings or a single compliance message.
    """
    violations = []
    for rule in GOLDEN_CONFIG_RULES:
        if rule["pattern"] not in device_config:
            violations.append(f"VIOLATION: Missing '{rule['pattern']}' ({rule['description']})")
            
    if not violations:
        return ["COMPLIANT: Config passes all golden rules."]
    return violations

@mcp.tool()
def scan_vulnerabilities(device_version: str) -> List[str]:
    """
    Checks device OS version against the internal CVE database.
    
    Args:
        device_version: The version string (e.g., '16.03.01').
        
    Returns:
        list[str]: Known vulnerabilities or safe status.
    """
    return CVE_DB.get(device_version, ["Unknown version or no known vulnerabilities."])

@mcp.prompt()
def audit_network_security() -> str:
    """Workflow: Comprehensive security audit."""
    return """
1. For each device in inventory:
    a. Retrieve running config (Observer).
    b. Call `check_compliance`.
    c. Retrieve version.
    d. Call `scan_vulnerabilities`.
2. Generate Audit Report.
"""

if __name__ == "__main__":
    mcp.run()
