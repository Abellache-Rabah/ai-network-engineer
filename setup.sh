#!/bin/bash
set -e

echo "=== MCP Deployment Setup ==="

# 1. Check Docker Installation
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    echo "Please install Docker first:"
    echo "  sudo apt-get update && sudo apt-get install docker.io docker-compose"
    exit 1
fi
echo "✅ Docker is installed"



# 2. Check/Install Gemini CLI
CLI_PKG="@google/gemini-cli"
if ! command -v gemini &> /dev/null; then
    echo "Installing Gemini CLI..."
    if command -v npm &> /dev/null; then
        sudo npm install -g "$CLI_PKG"
        echo "✅ Gemini CLI installed"
    else
        echo "❌ Error: npm not found. Please install Node.js/npm first."
        exit 1
    fi
else
    echo "✅ Gemini CLI already installed"
fi


# 3. Build and Start Container
echo "Building and starting Docker container..."
docker compose up -d --build

echo "Waiting for container to be ready..."
sleep 2

# 4. Generate Settings
SETTINGS_DIR="$HOME/.gemini"
SETTINGS_FILE="$SETTINGS_DIR/settings.json"
mkdir -p "$SETTINGS_DIR"
BACKUP_FILE="$SETTINGS_FILE.bak.$(date +%s)"

if [ -f "$SETTINGS_FILE" ]; then
    echo "Backing up existing settings to $BACKUP_FILE"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
fi

echo "Generating $SETTINGS_FILE..."

# We use docker exec to run the python scripts inside the container.
# Paths inside container are /app/servers/...
cat > "$SETTINGS_FILE" <<EOF
{
  "security": {
    "auth": {
      "selectedType": "oauth-personal"
    }
  },
  "mcpServers": {
    "ssh": {
      "command": "npx",
      "args": [
        "-y",
        "@idletoaster/ssh-mcp-server@latest"
      ],
      "env": {}
    },
    "verifier": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-toolbox", "python", "/app/servers/verifier/server.py"],
      "env": {}
    },
    "deployer": {
        "command": "docker",
        "args": ["exec", "-i", "mcp-toolbox", "python", "/app/servers/deployer/server.py"],
        "env": {}
    },
    "observer": {
        "command": "docker",
        "args": ["exec", "-i", "mcp-toolbox", "python", "/app/servers/observer/server.py"],
        "env": {}
    },
    "librarian": {
        "command": "docker",
        "args": ["exec", "-i", "mcp-toolbox", "python", "/app/servers/librarian/server.py"],
        "env": {}
    },
    "ipam": {
        "command": "docker",
        "args": ["exec", "-i", "mcp-toolbox", "python", "/app/servers/ipam/server.py"],
        "env": {}
    },
    "auditor": {
        "command": "docker",
        "args": ["exec", "-i", "mcp-toolbox", "python", "/app/servers/auditor/server.py"],
        "env": {}
    },
    "traffic_gen": {
        "command": "docker",
        "args": ["exec", "-i", "mcp-toolbox", "python", "/app/servers/traffic_gen/server.py"],
        "env": {}
    }
  }
}
EOF

echo "=== Setup Complete ==="
echo "You can now use the Gemini CLI with your Dockerized MCP servers."
echo "Try running: gemini"
