# Network Configuration Verification MCP Server

An MCP server that provides tools to verify network configurations.

## Features

-   **Device Configuration Verification**: Uses [Batfish](https://www.batfish.org/) to verify configurations for Cisco, Juniper, Arista, etc.
-   **Host Configuration Verification**: Validates Linux host network configurations (Debian/Netplan).

## Tools

1.  `verify_device_config(config_content, hostname, platform)`
    -   Verifies device configs using Batfish.
    -   Requires Batfish service running.
2.  `verify_host_config(config_content, config_type)`
    -   Basic validation for `netplan` or `interfaces` files.

## Setup

### Prerequisites

-   Python 3.10+
-   Docker (for Batfish)

### Installation

1.  Create virtual environment and install dependencies:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install .
    ```

2.  Start Batfish service:
    ```bash
    docker-compose up -d
    ```

### Usage with MCP Inspector

```bash
npx @modelcontextprotocol/inspector ./.venv/bin/python src/server.py
```
