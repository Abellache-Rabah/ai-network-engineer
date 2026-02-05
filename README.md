# LLM Network Agent - Modular AI-Powered Network Configuration Agent

An AI agent that acts as a **Network Engineer**, managing network infrastructure using a **modular architecture of MCP (Model Context Protocol) servers**. Add or remove MCP servers based on your specific needs.


## 🎯 What It Does

Configure and manage network devices (Cisco routers, Linux hosts) in a GNS3 simulation environment using natural language commands through an AI agent.

**Example:** "Change PC3's IP address to 10.0.0.15/24" → Agent allocates IP via IPAM → Updates inventory → Deploys config → Verifies connectivity

## 🏗️ Architecture

7 MCP servers working together:

- **Librarian** - Source of truth (inventory.yaml)
- **IPAM** - IP address management
- **Verifier** - Pre-deployment validation
- **Deployer** - Configuration deployment
- **Observer** - Network monitoring
- **Auditor** - Security compliance
- **TrafficGen** - Traffic testing

> [!IMPORTANT]
> When changing the network topology in GNS3 (adding/removing devices or links), you must **manually modify** `shared/inventory.yaml` to match the new topology.

## 📋 Requirements

- **Docker** (required)
- **GNS3** simulation environment
- **Cisco IOS router image** (for GNS3 - you need to provide this)
- **Gemini CLI** or Claude Desktop (for AI integration)
- **Node.js/npm** (for Gemini CLI)

## 🚀 Quick Start

### 1. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- ✅ Check Docker installation
- ✅ Install Gemini CLI (if needed)
- ✅ Build and start Docker containers
- ✅ Generate Gemini settings with all MCP servers

### 2. Import GNS3 Project

1. Open GNS3
2. Import `Test_project.gns3project`
3. Ensure you have a **Cisco IOS router image** configured in GNS3
4. Start the topology

### 3. Configure AI Client

**For Gemini:**
The setup script automatically creates `~/.gemini/settings.json` with all MCP servers.

**For Claude Desktop:**
Copy MCP server configurations from generated settings to your Claude config:
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### 4. Start Using

```bash
gemini
```

**Important:** When the CLI starts, type **`@GEMINI.md`** to load the system prompt and agent rules.

Try: *"Show me all devices in the network"* or *"Change PC1 IP to 192.168.1.10/24"*

## 🎥 Video Demonstration

Check out `demonstration.mp4` for a complete walkthrough of the system in action.

## ⚠️ Troubleshooting

**If MCP servers aren't working:**

1. **Check Gemini settings:** Make sure `~/.gemini/settings.json` has all 7 MCP servers configured
2. **Verify Docker:** Run `docker ps` and confirm `mcp-toolbox` container is running
3. **Restart Gemini:** Exit and restart the Gemini CLI
4. **Check logs:** Run `docker logs mcp-toolbox`

**If setup.sh fails:**

```bash
# Manually install Docker first
sudo apt-get update && sudo apt-get install docker.io docker-compose

# Then run setup.sh again
./setup.sh
```

## 📚 Documentation

- **GEMINI.md** - AI agent system prompt and workflow
- **MCP_SERVERS_GUIDE.md** - Detailed guide for each MCP server

## 🏛️ Project Structure

```
.
├── servers/           # 7 MCP servers
│   ├── librarian/
│   ├── ipam/
│   ├── deployer/
│   ├── verifier/
│   ├── observer/
│   ├── auditor/
│   └── traffic_gen/
├── shared/            # Common utilities & inventory
│   ├── inventory.yaml
│   ├── gns3_utils.py
│   └── topology_physical.yaml
├── setup.sh           # Automated setup
└── docker-compose.yml
```

## 🤝 Contributing

This project demonstrates AI-powered network automation. Feel free to extend it with additional MCP servers or integration with other network simulation platforms.

## 👥 Authors

- **Abellache Rabah** - abellache.rabah@outlook.com
- **Sabrina Sahouli** - sabrinasahouli2001@gmail.com

## 📄 License

MIT License - See LICENSE file for details

---

## ⚠️ Disclaimer

**This project is for educational and demonstration purposes only.**

This is a simulation/demonstration project that has **NOT been tested in production environments** and is **NOT recommended for production use**. It is intended solely for learning, research, and demonstration of AI-powered network automation concepts. 
