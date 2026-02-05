import sys
import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

async def run_tests():
    # Define server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["src/server.py"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"Tools found: {[t.name for t in tools.tools]}")
            
            # Test verify_host_config (valid)
            print("\nTesting verify_host_config (Valid)...")
            with open("tests/netplan_valid.yaml", "r") as f:
                content = f.read()
            result = await session.call_tool("verify_host_config", arguments={"config_content": content, "config_type": "netplan"})
            print(f"Result: {result.content[0].text}")

            # Test verify_host_config (invalid)
            print("\nTesting verify_host_config (Invalid)...")
            with open("tests/netplan_invalid.yaml", "r") as f:
                content = f.read()
            result = await session.call_tool("verify_host_config", arguments={"config_content": content, "config_type": "netplan"})
            print(f"Result: {result.content[0].text}")

            # Test verify_device_config
            print("\nTesting verify_device_config...")
            try:
                with open("tests/cisco_valid.cfg", "r") as f:
                     content = f.read()
                result = await session.call_tool("verify_device_config", arguments={"config_content": content, "hostname": "test-router", "platform": "cisco"})
                print(f"Result: {result.content[0].text}")
            except Exception as e:
                print(f"Batfish test failed (expected if docker not running): {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
