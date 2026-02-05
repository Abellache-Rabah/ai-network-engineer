import yaml
import re
from typing import Dict, Any, List

def validate_netplan(config_content: str) -> Dict[str, Any]:
    """
    Validates a Netplan YAML configuration for basic structure and common errors.
    """
    try:
        data = yaml.safe_load(config_content)
    except yaml.YAMLError as e:
        return {"valid": False, "errors": [f"YAML syntax error: {str(e)}"]}

    if not isinstance(data, dict) or 'network' not in data:
        return {"valid": False, "errors": ["Missing top-level 'network' key"]}

    network = data.get('network', {})
    version = network.get('version')
    
    errors = []
    if version not in [2]:
        errors.append(f"Unsupported or missing network version: {version}. Expected 2.")
    
    # Check for known renderer
    renderer = network.get('renderer')
    if renderer and renderer not in ['networkd', 'NetworkManager']:
        errors.append(f"Unknown renderer: {renderer}")

    # Check ethernets
    ethernets = network.get('ethernets', {})
    if ethernets:
        for name, cfg in ethernets.items():
            if not isinstance(cfg, dict):
                 errors.append(f"Invalid configuration for interface {name}")
                 continue
            
            # Check addresses
            addresses = cfg.get('addresses', [])
            if addresses:
                if not isinstance(addresses, list):
                     errors.append(f"Interface {name}: addresses must be a list")
                else:
                    for addr in addresses:
                        # Basic CIDR regex check
                        if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$', str(addr)) and not re.match(r'^[a-fA-F0-9:]+/[0-9]{1,3}$', str(addr)):
                             # weak check for v6
                             errors.append(f"Interface {name}: Invalid IP address format '{addr}'")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def validate_interfaces_file(config_content: str) -> Dict[str, Any]:
    """
    Basic check for /etc/network/interfaces style syntax
    """
    errors = []
    lines = config_content.splitlines()
    has_auto = False
    has_iface = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split()
        if parts[0] == 'auto':
            has_auto = True
        elif parts[0] == 'iface':
            has_iface = True
            if len(parts) < 4:
                errors.append(f"Line {i+1}: Incomplete iface definition")
            elif parts[2] not in ['inet', 'inet6']:
                 errors.append(f"Line {i+1}: Invalid address family '{parts[2]}'")
    
    if not has_auto and not has_iface:
        errors.append("File does not appear to contain valid interface definitions")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def verify_host_config(config_content: str, config_type: str = "netplan") -> Dict[str, Any]:
    if config_type.lower() == "netplan":
        return validate_netplan(config_content)
    elif config_type.lower() in ["interfaces", "debian"]:
        return validate_interfaces_file(config_content)
    else:
        return {"valid": False, "errors": [f"Unknown config type: {config_type}"]}
