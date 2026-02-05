# MCP Servers Guide

---

## 🇬🇧 English

### Overview
7 **MCP servers** act as a network engineering team for the AI agent.

### Servers

#### **librarian** - Knowledge Base
- **Purpose**: Source of truth and documentation
- **Data**: `inventory.yaml` (devices), `topology_physical.yaml` (cabling)
- **Tools**: `get_source_of_truth`, `update_source_of_truth`, `search_docs`

#### **ipam** - IP Management
- **Purpose**: Manage IP addresses and subnets
- **Data**: Internal IP registry (JSON)
- **Tools**: `allocate_ip`, `get_subnet_usage`, `list_subnets`

#### **verifier** - Pre-Deployment Validation
- **Purpose**: Validate configs before deployment
- **Engine**: Batfish for network analysis
- **Tools**: `verify_device_config`, `verify_host_config`

#### **deployer** - Configuration Deployment
- **Purpose**: Apply configurations to devices
- **Method**: Telnet to GNS3 console ports
- **Tools**: `deploy_config`, `get_config_diff`, `rollback`

#### **observer** - Network Monitoring
- **Purpose**: Monitor live network state
- **Method**: Connect via Telnet, run commands (`ping`, `show ip interface`)
- **Tools**: `check_reachability`, `get_interface_health`, `detect_link_failures`

#### **auditor** - Security & Compliance
- **Purpose**: Security checks and vulnerability scanning
- **Method**: Check against security rules, CVE lookup
- **Tools**: `check_compliance`, `scan_vulnerabilities`

#### **traffic_gen** - Traffic Testing
- **Purpose**: Simulate and measure network traffic
- **Method**: Simulates iperf3 tests
- **Tools**: `start_traffic_server`, `run_traffic_test`

### Shared Folder

- **`gns3_utils.py`**: Telnet connection library for GNS3
- **`inventory.yaml`**: Device inventory (IPs, ports, groups)
- **`topology_physical.yaml`**: Physical cabling map

---

## 🇫🇷 Français

### Vue d'ensemble
7 **serveurs MCP** agissent comme une équipe réseau pour l'agent IA.

### Serveurs

#### **librarian** - Base de Connaissances
- **Rôle**: Source de vérité et documentation
- **Données**: `inventory.yaml` (équipements), `topology_physical.yaml` (câblage)
- **Outils**: `get_source_of_truth`, `update_source_of_truth`, `search_docs`

#### **ipam** - Gestion IP
- **Rôle**: Gérer adresses IP et sous-réseaux
- **Données**: Registre IP interne (JSON)
- **Outils**: `allocate_ip`, `get_subnet_usage`, `list_subnets`

#### **verifier** - Validation Pré-Déploiement
- **Rôle**: Valider configs avant déploiement
- **Moteur**: Batfish pour analyse réseau
- **Outils**: `verify_device_config`, `verify_host_config`

#### **deployer** - Déploiement Configuration
- **Rôle**: Appliquer configurations aux équipements
- **Méthode**: Telnet vers ports console GNS3
- **Outils**: `deploy_config`, `get_config_diff`, `rollback`

#### **observer** - Surveillance Réseau
- **Rôle**: Surveiller l'état réseau en temps réel
- **Méthode**: Connexion Telnet, commandes (`ping`, `show ip interface`)
- **Outils**: `check_reachability`, `get_interface_health`, `detect_link_failures`

#### **auditor** - Sécurité & Conformité
- **Rôle**: Vérifications sécurité et scan vulnérabilités
- **Méthode**: Vérifier règles sécurité, recherche CVE
- **Outils**: `check_compliance`, `scan_vulnerabilities`

#### **traffic_gen** - Tests de Trafic
- **Rôle**: Simuler et mesurer trafic réseau
- **Méthode**: Simulation tests iperf3
- **Outils**: `start_traffic_server`, `run_traffic_test`

### Dossier Partagé

- **`gns3_utils.py`**: Bibliothèque connexion Telnet pour GNS3
- **`inventory.yaml`**: Inventaire équipements (IPs, ports, groupes)
- **`topology_physical.yaml`**: Plan câblage physique
