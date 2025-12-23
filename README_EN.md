# CTyun CLI

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Count](https://img.shields.io/badge/APIs-283+-brightgreen.svg)](#api-coverage)
[![Commands](https://img.shields.io/badge/Commands-217+-orange.svg)](#cli-commands)

A unified command-line interface for China Telecom Cloud (CTyun), designed for developers and DevOps engineers who manage cloud infrastructure at scale.

[简体中文](README_CN.md) | **English**

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Service Modules](#service-modules)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [API Coverage](#api-coverage)
- [Contributing](#contributing)
- [License](#license)

---

## Features

**Why choose CTyun CLI?**

- **Infrastructure as Code Ready** - JSON/YAML output for automation pipelines
- **Extensive API Coverage** - 283+ cloud APIs, 217+ CLI commands across 11 services
- **Secure by Default** - EOP signature authentication, environment-based credential management
- **Multi-Cloud Patterns** - Familiar command structure similar to AWS CLI and kubectl
- **Production Ready** - Built for enterprise workloads with comprehensive error handling

---

## Installation

### Using pip (Recommended)

```bash
pip install ctyun-cli
```

### From Source

```bash
git clone https://github.com/fengyucn/ctyun-cli.git
cd ctyun-cli
pip install -e .
```

### Verify Installation

```bash
ctyun-cli --version
ctyun-cli --help
```

---

## Getting Started

### Authentication Setup

CTyun CLI uses Access Key authentication. Set your credentials using environment variables:

```bash
export CTYUN_ACCESS_KEY="your_access_key"
export CTYUN_SECRET_KEY="your_secret_key"
```

Alternatively, use the interactive configuration:

```bash
ctyun-cli configure
```

This creates a configuration file at `~/.ctyun/config`.

### First Commands

```bash
# Verify configuration
ctyun-cli show-config

# List compute instances
ctyun-cli ecs list

# Check account balance
ctyun-cli billing balance

# Query monitoring metrics
ctyun-cli monitor query-metric-data --region-id <region>
```

---

## Service Modules

CTyun CLI organizes commands into logical service modules:

### Compute & Storage

#### ECS (Elastic Compute Service)
Manage virtual machines, snapshots, and compute resources.

```bash
ctyun-cli ecs list                    # List instances
ctyun-cli ecs get-instance-detail     # Instance details
ctyun-cli ecs list-snapshots          # Snapshot management
ctyun-cli ecs list-keypairs           # SSH key management
```

**41 commands | 38 APIs**

#### EBS (Elastic Block Storage)
Persistent block storage volumes for ECS instances.

```bash
ctyun-cli ebs list-disks              # List block volumes
```

**1 command | 1 API**

### Containers & Orchestration

#### CCE (Cloud Container Engine)
Managed Kubernetes service for containerized applications.

```bash
# Cluster operations
ctyun-cli cce list-clusters
ctyun-cli cce create-cluster
ctyun-cli cce get-kubeconfig

# ConfigMap management
ctyun-cli cce configmap list
ctyun-cli cce configmap show

# Logs and diagnostics
ctyun-cli cce logs query
```

**36 commands | 37 APIs**

### Networking

#### VPC (Virtual Private Cloud)
Software-defined networking with subnets, routing, and security groups.

```bash
# VPC management
ctyun-cli vpc list-vpcs
ctyun-cli vpc new-list                # Cursor-based pagination
ctyun-cli vpc show

# Subnet operations
ctyun-cli vpc create-subnet
ctyun-cli vpc subnet new-list

# Security groups
ctyun-cli vpc create-security-group
ctyun-cli vpc security new-query
```

**15 commands | 15 APIs**

#### ELB (Elastic Load Balancing)
Distribute traffic across multiple compute instances.

```bash
# Load balancers
ctyun-cli elb loadbalancer list
ctyun-cli elb loadbalancer get

# Target groups
ctyun-cli elb targetgroup list
ctyun-cli elb targetgroup targets list

# Health monitoring
ctyun-cli elb health-check show
ctyun-cli elb monitor realtime
ctyun-cli elb monitor history
```

**7 commands | 5 APIs**

#### CDA (Cloud Dedicated Access)
Enterprise dedicated network connections and hybrid cloud networking.

```bash
# Gateway management
ctyun-cli cda gateway list
ctyun-cli cda gateway physical-lines

# Health checks
ctyun-cli cda health-check status
ctyun-cli cda health-check link-probe

# VPC integration
ctyun-cli cda vpc list
ctyun-cli cda vpc info
```

**19 commands | 19 APIs**

### Data Services

#### Redis
Managed in-memory data store for caching and real-time applications.

```bash
# Instance management
ctyun-cli redis list-instances
ctyun-cli redis create-instance

# Performance monitoring
ctyun-cli redis get-instance-metrics

# Backup operations
ctyun-cli redis create-backup
ctyun-cli redis list-network-configs
```

**14 commands | 19 APIs**

### Observability

#### Monitor
Metrics, alarms, and observability for all CTyun resources.

```bash
# Metrics queries
ctyun-cli monitor query-metric-data
ctyun-cli monitor query-cpu-top
ctyun-cli monitor query-mem-top

# Alarm management
ctyun-cli monitor query-alarm-rules
ctyun-cli monitor query-alert-history

# Inspection tasks
ctyun-cli monitor query-inspection-tasks
```

**53 commands | 54 APIs**

### Security & Compliance

#### Security
Host security scanning, vulnerability detection, and threat intelligence.

```bash
ctyun-cli security agents           # Security agents
ctyun-cli security scan-result      # Scan results
ctyun-cli security vuln-list        # Vulnerabilities
ctyun-cli security security-risks   # Risk assessment
```

**5 commands | 11 APIs**

### Management & Billing

#### IAM (Identity and Access Management)
Project and user access control.

```bash
ctyun-cli iam list-projects
ctyun-cli iam get-project-detail
```

**3 commands | 3 APIs**

#### Billing
Cost tracking, billing reports, and budget management.

```bash
ctyun-cli billing balance                  # Account balance
ctyun-cli billing bills                    # Monthly bills
ctyun-cli billing details                  # Consumption details
ctyun-cli billing consumption-statistics   # Cost analysis
```

**15 commands | 14 APIs**

---

## Usage Examples

### Infrastructure Automation

**Provision a Redis instance:**

```bash
ctyun-cli redis create-instance \
  --instance-name prod-cache \
  --edition StandardSingle \
  --engine-version 6.0 \
  --shard-mem-size 8 \
  --zone-name cn-huabei2-tj-1a-public-ctcloud \
  --vpc-id vpc-xxxxx \
  --subnet-id subnet-xxxxx \
  --secgroups sg-xxxxx \
  --password "YourSecureP@ssw0rd" \
  --dry-run
```

### Cost Optimization

**Analyze monthly spending:**

```bash
# Get account balance
ctyun-cli billing balance --output json

# Review billing details
ctyun-cli billing bills --month 202412 --output yaml

# Export consumption data
ctyun-cli billing consumption-statistics --output json > costs.json
```

### Kubernetes Management

**Manage CCE clusters:**

```bash
# List all clusters
ctyun-cli cce list-clusters --output table

# Get kubeconfig
ctyun-cli cce get-kubeconfig \
  --region-id <region> \
  --cluster-id <cluster-id> > ~/.kube/config

# View ConfigMaps
ctyun-cli cce configmap list \
  --region-id <region> \
  --cluster-id <cluster-id> \
  --namespace default
```

### Monitoring & Alerting

**Query performance metrics:**

```bash
# CPU utilization Top-N
ctyun-cli monitor query-cpu-top \
  --region-id <region> \
  --number 10

# Check alarm rules
ctyun-cli monitor query-alarm-rules \
  --region-id <region> \
  --output json

# Query inspection tasks
ctyun-cli monitor query-inspection-tasks \
  --region-id <region>
```

### Network Operations

**VPC and subnet management:**

```bash
# Create VPC
ctyun-cli vpc create-vpc \
  --name prod-vpc \
  --cidr 10.0.0.0/16

# Create subnet
ctyun-cli vpc create-subnet \
  --vpc-id vpc-xxxxx \
  --cidr 10.0.1.0/24 \
  --name prod-subnet-a

# Configure security group
ctyun-cli vpc create-security-group \
  --name prod-sg \
  --description "Production security group"
```

---

## Configuration

### Output Formats

CTyun CLI supports multiple output formats for different use cases:

```bash
# Human-readable table (default)
ctyun-cli ecs list --output table

# Machine-parseable JSON
ctyun-cli ecs list --output json | jq '.[] | {id, name, status}'

# Configuration-friendly YAML
ctyun-cli ecs list --output yaml
```

### Multi-Environment Profiles

Manage multiple accounts or regions with profiles:

```bash
# Configure production profile
ctyun-cli configure --profile production

# Configure staging profile
ctyun-cli configure --profile staging

# Use specific profile
ctyun-cli --profile production ecs list
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
ctyun-cli --debug ecs list
```

### Shell Integration

**Bash/Zsh completion:**

```bash
# Add to ~/.bashrc or ~/.zshrc
eval "$(_CTYUN_CLI_COMPLETE=bash_source ctyun-cli)"
```

**Scripting example:**

```bash
#!/bin/bash

# Get all running instances
INSTANCES=$(ctyun-cli ecs list --output json | jq -r '.[] | select(.status=="running") | .instanceId')

# Process each instance
for INSTANCE in $INSTANCES; do
  echo "Processing instance: $INSTANCE"
  ctyun-cli ecs get-instance-detail --instance-id "$INSTANCE"
done
```

---

## API Coverage

### Statistics

| Category | Modules | Commands | APIs | Coverage |
|----------|---------|----------|------|----------|
| **Compute** | 2 | 42 | 39 | 100% |
| **Networking** | 3 | 41 | 39 | 95%+ |
| **Containers** | 1 | 36 | 37 | 100% |
| **Data Services** | 1 | 14 | 19 | 100% |
| **Observability** | 2 | 58 | 65 | 90%+ |
| **Management** | 2 | 18 | 17 | 100% |
| **Total** | **11** | **217** | **283** | **95%+** |

### Version Compatibility

- **API Version**: Supports CTyun API v1/v2
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Authentication**: EOP signature + legacy AK/SK

---

## Documentation

### User Guides
- [Installation & Setup](docs/usage.md)
- [Authentication Guide](docs/security-guide.md)
- [Command Reference](docs/COMMAND_MANUAL.md)

### Service Guides
- [Monitoring Service](MONITOR_USAGE.md) - 54 monitoring APIs
- [Redis Service](REDIS_CLI_USAGE.md) - Distributed cache management
- [IAM Service](IAM_USAGE.md) - Identity and access control

### Developer Resources
- [Architecture Overview](docs/overview.md)
- [API Documentation](https://github.com/fengyucn/ctyun-cli/wiki)
- [Changelog](CHANGELOG.md)

---

## Contributing

We welcome contributions! Please see our [contribution guidelines](CONTRIBUTING.md).

### Development Setup

```bash
git clone https://github.com/fengyucn/ctyun-cli.git
cd ctyun-cli
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

---

## Support

- **Issues**: [GitHub Issues](https://github.com/fengyucn/ctyun-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fengyucn/ctyun-cli/discussions)
- **Email**: popfrog@gmail.com

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Credits

**Author**: Y.FENG (popfrog@gmail.com)  
**Repository**: [github.com/fengyucn/ctyun-cli](https://github.com/fengyucn/ctyun-cli)  
**PyPI**: [pypi.org/project/ctyun-cli](https://pypi.org/project/ctyun-cli/)

---

**Made with ❤️ for the CTyun community**
