from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, Any, List
import yaml
import os

mcp = FastMCP("Librarian Server")

# Inventory Source
INVENTORY_PATH = os.path.join(os.path.dirname(__file__), "../../shared/inventory.yaml")

def load_inventory() -> Dict:
    try:
        with open(INVENTORY_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {"error": "Inventory not found"}

import glob

# Knowledge Base (RAG)
DOCS_PATH = os.path.join(os.path.dirname(__file__), "../../shared/docs")

@mcp.tool()
def search_docs(query: str) -> List[str]:
    """Search the knowledge base files for documentation."""
    results = []
    query = query.lower()
    
    if not os.path.exists(DOCS_PATH):
        return ["Documentation directory not found."]

    md_files = glob.glob(os.path.join(DOCS_PATH, "*.md"))
    
    for file_path in md_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if query in content.lower():
                    filename = os.path.basename(file_path)
                    # Extract a snippet context
                    idx = content.lower().find(query)
                    start = max(0, idx - 50)
                    end = min(len(content), idx + 200)
                    snippet = content[start:end].replace("\n", " ")
                    results.append(f"[{filename}]: ...{snippet}...")
        except Exception:
            continue
    
    if not results:
        return ["No documents found matching query."]
    return results

@mcp.tool()
def get_device_info(device_name: str) -> str:
    """Retrieve details for a specific device from Source of Truth."""
    inv = load_inventory()
    hosts = inv.get("hosts", {})
    
    # Case insensitive lookup
    target_lower = device_name.lower()
    for hostname, data in hosts.items():
        if hostname.lower() == target_lower:
             return str(data)
             
    return f"Device {device_name} not found in inventory."

@mcp.tool()
def list_devices() -> List[str]:
    """List all device names in the inventory."""
    inv = load_inventory()
    # Safely get keys from hosts
    return list(inv.get("hosts", {}).keys())

@mcp.resource("librarian://topology/definition")
def get_topology() -> str:
    """Returns the defining network topology (Source of Truth)."""
    inv = load_inventory()
    return yaml.dump(inv)

@mcp.resource("librarian://topology/physical")
def get_physical_topology() -> str:
    """Returns the PHYSICAL cabling and connection map (Ground Truth)."""
    topo_path = os.path.join(os.path.dirname(__file__), "../../shared/topology_physical.yaml")
    try:
        with open(topo_path, 'r') as f:
            return f.read()
    except Exception:
        return "Physical topology file not found."

# --- Source of Truth Management ---

def deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges 'updates' into 'base'.
    Warning: This modifies 'base' in place!
    """
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

@mcp.tool()
def get_source_of_truth() -> str:
    """
    Returns the raw YAML content of the Source of Truth (inventory.yaml).
    Use this to read the current network state.

    Returns:
        str: The raw YAML content of the inventory file.
    """
    try:
        with open(INVENTORY_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading Source of Truth: {str(e)}"

@mcp.tool()
def update_source_of_truth(updates: str) -> str:
    """
    Updates the Source of Truth (inventory.yaml) using a Deep Merge strategy.
    
    Args:
        updates: A YAML string containing ONLY the fields effectively changing.
                 The structure must EXACTLY match the hierarchy in inventory.yaml.
                 
                 Example (Update IP of pc3):
                 ```yaml
                 hosts:
                   pc3:
                     data:
                       ip: 20.0.0.99
                 ```
                 
                 Example (Add new group):
                 ```yaml
                 groups:
                   new_group:
                     platform: linux
                 ```
    
    Returns:
        str: A success message or error description.
    """
    try:
        # 1. Parse updates
        update_dict = yaml.safe_load(updates)
        if not update_dict or not isinstance(update_dict, dict):
            return "Error: Updates must be a valid YAML dictionary."

        # 2. Load current state
        current_inv = load_inventory()
        if "error" in current_inv:
             return f"Error loading current inventory: {current_inv['error']}"

        # 3. Deep Merge
        merged_inv = deep_merge(current_inv, update_dict)

        # 4. Save Back
        # We manually dump to preserve block style if possible, but standard yaml.dump is used for now.
        with open(INVENTORY_PATH, 'w') as f:
            yaml.dump(merged_inv, f, sort_keys=False)
            
        return "Successfully updated Source of Truth (inventory.yaml)."

    except yaml.YAMLError as e:
        return f"Invalid YAML provided: {e}"
    except Exception as e:
        return f"Error updating Source of Truth: {e}"

if __name__ == "__main__":
    mcp.run()
