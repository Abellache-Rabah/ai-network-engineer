import socket
import time
import re
import yaml
import os

def load_inventory():
    # Helper to find inventory relative to this file or cwd
    paths = [
        "../../shared/inventory.yaml",
        "../shared/inventory.yaml",
        "shared/inventory.yaml"
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r') as f:
                return yaml.safe_load(f)
    return {}

class GNS3Console:
    def __init__(self, hostname, port, platform="cisco_ios"):
        self.hostname = hostname
        self.port = port
        self.platform = platform
        self.sock = None

    def connect(self):
        self.sock = socket.create_connection((self.hostname, self.port), timeout=20)
        # Wake up console
        self.sock.send(b"\r\n")
        time.sleep(1)
        self.read_until_prompt()

    def send_command(self, cmd, wait_time=1.0):
        if not self.sock:
            self.connect()
        
        self.sock.send(cmd.encode('utf-8') + b"\r\n")
        time.sleep(wait_time)
        return self.read_buffer()

    def read_buffer(self):
        out = b""
        self.sock.settimeout(0.5)
        try:
            while True:
                data = self.sock.recv(4096)
                if not data: break
                out += data
        except socket.timeout:
            pass
        return out.decode('utf-8', errors='ignore')

    def read_until_prompt(self):
        # Naive approach: read anything pending
        return self.read_buffer()

    def configure_cisco(self, config_str):
        output = ""
        # Ensure we are in a clean state
        self.send_command("end", wait_time=0.5)
        self.send_command("\r\n", wait_time=0.5)
        
        # Enter privileged mode
        self.send_command("enable", wait_time=0.5)
        
        # Enter config mode
        self.send_command("configure terminal", wait_time=0.5)
        
        for line in config_str.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            
            # Skip commands that we already sent or shouldn't send in loop
            if stripped.lower() in ["enable", "configure terminal", "conf t", "end", "exit"]:
                continue
                
            # Send command with sufficient delay for GNS3
            output += self.send_command(stripped, wait_time=0.5)
        
        # Exit and save
        self.send_command("end", wait_time=0.5)
        self.send_command("write memory", wait_time=1.0)
        self.send_command("\r\n", wait_time=1.0)
        return output

    def configure_linux(self, config_str):
        output = ""
        # Linux doesn't need enable/conf t
        # We assume the config_str is a series of shell commands
        # or we try to be smart. For now, simple shell execution.
        
        for line in config_str.splitlines():
            if line.strip():
                output += self.send_command(line, wait_time=0.5)
        
        return output

    def ping(self, target_ip):
        # VPCS or Router ping
        if self.platform == "linux" or "pc" in str(self.port): # VPCS/Linux
             # VPCS ping: ping 10.0.0.1
             # Linux: ping -c 4 10.0.0.1
             cmd = f"ping {target_ip} -c 2" if self.platform == "linux" else f"ping {target_ip}"
             out = self.send_command(cmd, wait_time=3.0)
             return out
             out = self.send_command(f"ping {target_ip}", wait_time=3.0)
             return out

    def get_interfaces(self):
        """
        Returns a list of interfaces from the device with details.
        Only implemented for Cisco so far.
        """
        if self.platform != "cisco_ios":
             # For mock/linux, return empty or mock? 
             # Ideally we should support linux too (ip addr) but user focused on router.
            return []

        # Send command
        # Ensure we are out of config mode
        self.send_command("end", wait_time=0.5)
        output = self.send_command("show ip interface brief", wait_time=1.0)
        
        # Parse output
        interfaces = []
        for line in output.splitlines():
            # Typical output:
            # Interface                  IP-Address      OK? Method Status                Protocol
            # FastEthernet0/0            unassigned      YES unset  administratively down down    
            parts = line.split()
            if len(parts) >= 5 and parts[0] != "Interface" and not parts[0].startswith("R1"):
                 # Simple heuristic to get interface name
                 if parts[0][0].isalpha(): 
                     # Check if Status is "administratively down" (2 words) or "up" (1 word)
                     # Method is at index 3. Status starts at index 4.
                     # Protocol is the last one.
                     
                     name = parts[0]
                     ip = parts[1]
                     # Status parsing is tricky because of spaces.
                     # But usually Protocol is last.
                     protocol = parts[-1]
                     
                     # Status is everything between Method and Protocol?
                     # Method is parts[3]. 
                     # Status = " ".join(parts[4:-1])
                     status = " ".join(parts[4:-1])
                     
                     interfaces.append({
                         "name": name,
                         "ip": ip,
                         "status": status,
                         "protocol": protocol
                     })
        
        return interfaces

    def close(self):
        if self.sock:
            self.sock.close()
