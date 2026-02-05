# Network Topology Schema

This document defines the visual topology of the GNS3 network to help the AI understand the physical layout.

## Graph Diagram

```mermaid
graph TD
    %% Nodes
    R1[("Router (Cisco IOS)")]
    PC1("PC 1 (Linux)")
    PC2("PC 2 (Linux)")
    PC3("PC 3 (Linux)")
    
    %% Subnets / Clouds
    subgraph "Workstations Subnet (40.0.0.0/24)"
        PC1
        PC2
    end
    
    subgraph "Users Subnet (20.0.0.0/24)"
        PC3
    end

    %% Connections with Interface Names
    R1 -- "FastEthernet0/0" --> PC1
    R1 -- "FastEthernet0/0" --> PC2
    R1 -- "FastEthernet0/1" --> PC3

    %% Note on Connections
    note1[Ethernet Switch implied for shared 40.0.0.0/24 segment]
    PC1 -.- note1
    PC2 -.- note1
```

## Physical Wiring Table

| Device A | Interface A     | Device B | Interface B | Subnet       |
|----------|-----------------|----------|-------------|--------------|
| Router   | FastEthernet0/0 | PC 1     | eth0        | 40.0.0.0/24 |
| Router   | FastEthernet0/0 | PC 2     | eth0        | 40.0.0.0/24 |
| Router   | FastEthernet0/1 | PC 3     | eth0        | 20.0.0.0/24 |

> **Note**: The router uses **FastEthernet**, not standard Ethernet. ensure configuration commands use `interface FastEthernet0/0`.
