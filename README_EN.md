# CTYun CLI Tool 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Count](https://img.shields.io/badge/APIs-156+-brightgreen.svg)](#api-statistics)
[![Commands](https://img.shields.io/badge/Commands-136+-orange.svg)](#feature-overview)

**CTYun CLI Tool** is a powerful enterprise-grade command-line tool for China Telecom Cloud (CTYun), enabling easy cloud resource management from your terminal. Supports ECS, monitoring & alerting, security protection, Redis distributed cache service, billing queries, and more.

**📊 Scale Statistics: 15,000+ lines of code, 156+ APIs, 136+ commands**

[简体中文](README.md) | English

## ✨ Why Choose CTYun CLI?

- 🚀 **Efficient & Convenient** - Manage cloud resources with a single command, say goodbye to tedious console operations
- 🔐 **Secure & Reliable** - Enterprise-grade EOP signature authentication with environment variable support for credential protection
- 📊 **Feature-Rich** - Covering 156+ APIs across 7 core service modules
- 🎯 **Easy to Use** - Clear command structure with rich examples, get started in 5 minutes
- 🔧 **Flexible Configuration** - Support for config files, environment variables, and multiple profiles
- 📈 **Real-time Monitoring** - Complete monitoring service support including metrics queries, alert management, and Top-N statistics

## 📦 Quick Installation

Install with a single command:

```bash
pip install ctyun-cli
```

Verify installation:

```bash
ctyun-cli --version
```

## ⚡ 5-Minute Quick Start

### Step 1: Configure Credentials

Using environment variables (recommended for security):

```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
```

Or use interactive configuration:

```bash
ctyun-cli configure
```

### Step 2: Start Using

```bash
# View all available commands
ctyun-cli --help

# Show current configuration
ctyun-cli show-config

# List cloud server instances
ctyun-cli ecs list

# Check account balance
ctyun-cli billing balance
```

## 📊 API Statistics

### 🎯 Feature Overview

| Service Module | Commands | APIs | Description |
|----------------|----------|------|-------------|
| **ECS (Elastic Cloud Server)** | 50 | 42 | Instance management, snapshots, keypairs, affinity groups |
| **Monitor (Monitoring Service)** | 54 | 54 | Monitoring metrics, alert management, Top-N statistics, events |
| **Redis (Distributed Cache)** | 12 | 16 | Instance management, performance monitoring, network config |
| **Billing (Billing Query)** | 12 | 20 | Account balance, monthly bills, consumption analysis |
| **Security (Security Guard)** | 5 | 21 | Security scanning, vulnerability management, risk assessment |
| **IAM (Identity Access Management)** | 2 | 2 | Project management, permission control |
| **EBS (Elastic Block Storage)** | 1 | 1 | Block storage management |
| **Total** | **136** | **156** | **Covering CTYun Core Services** |

### 📈 Module Details

#### 🖥️ ECS Module - Cloud Server Management (50 Commands/42 APIs)
**Core Features:**
- Instance lifecycle management
- Snapshot and backup policies
- Keypairs and security groups
- Affinity group management
- Auto-renewal configuration
- DNS record management

**Common Commands:**
```bash
ctyun-cli ecs list                              # List instances
ctyun-cli ecs get-instance-detail             # Get instance details
ctyun-cli ecs list-snapshots                   # List snapshots
ctyun-cli ecs list-keypairs                    # List keypairs
ctyun-cli ecs get-auto-renew-config           # Get auto-renewal config
```

#### 📊 Monitor Module - Monitoring & Alerting Service (54 Commands/54 APIs)
**Core Features:**
- Monitoring metrics queries (8 APIs)
- Top-N statistics ranking (6 APIs)
- Alert rule management (7 APIs)
- Notification management (4 APIs)
- Inspection features (5 APIs)
- Event history queries (24 APIs)

**Common Commands:**
```bash
ctyun-cli monitor query-metric-data            # Query monitoring data
ctyun-cli monitor query-cpu-top               # CPU usage Top-N
ctyun-cli monitor query-mem-top               # Memory usage Top-N
ctyun-cli monitor query-alarm-rules           # Query alert rules
ctyun-cli monitor query-inspection-tasks      # Query inspection tasks
```

#### 🗄️ Redis Module - Distributed Cache Service (12 Commands/16 APIs)
**Core Features:**
- Redis instance management
- Performance monitoring and diagnostics
- Network configuration management
- Backup and recovery

**Common Commands:**
```bash
ctyun-cli redis list-instances                 # List Redis instances
ctyun-cli redis get-instance-metrics         # Get instance metrics
ctyun-cli redis create-backup                # Create backup
ctyun-cli redis list-network-configs         # List network configurations
```

#### 💰 Billing Module - Billing Management (12 Commands/20 APIs)
**Core Features:**
- Account balance queries
- Monthly bill statistics
- Consumption detail analysis
- Budget management

**Common Commands:**
```bash
ctyun-cli billing balance                      # Check account balance
ctyun-cli billing bills                        # View monthly bills
ctyun-cli billing details                      # View consumption details
ctyun-cli billing consumption-statistics     # Consumption statistics analysis
```

#### 🛡️ Security Module - Security Guard (5 Commands/21 APIs)
**Core Features:**
- Security client management
- Vulnerability scanning and assessment
- Security policy configuration
- Risk analysis reports

**Common Commands:**
```bash
ctyun-cli security agents                      # List security clients
ctyun-cli security scan-result                # View scan results
ctyun-cli security vuln-list                  # List vulnerabilities
ctyun-cli security security-risks             # View security risks
```

#### 👤 IAM Module - Identity Access Management (2 Commands/2 APIs)
**Core Features:**
- Project management
- User permission control

**Common Commands:**
```bash
ctyun-cli iam list-projects                    # List projects
ctyun-cli iam get-project-detail             # Get project details
```

#### 💾 EBS Module - Elastic Block Storage (1 Command/1 API)
**Core Features:**
- Block storage management

**Common Commands:**
```bash
ctyun-cli ebs list-disks                       # List block storage volumes
```

## 🔧 Advanced Features

### Multiple Output Formats

Support for three output formats for different scenarios:

```bash
# Table format (default, human-readable)
ctyun-cli ecs list --output table

# JSON format (program-friendly)
ctyun-cli ecs list --output json

# YAML format (configuration management)
ctyun-cli ecs list --output yaml
```

### Multi-Environment Configuration

Support for multiple profiles for easy switching between different accounts:

```bash
# Configure production environment
ctyun-cli configure --profile production

# Configure testing environment
ctyun-cli configure --profile testing

# Use specific profile
ctyun-cli --profile production ecs list
```

### Debug Mode

Enable debug mode for detailed troubleshooting information:

```bash
ctyun-cli --debug security scan-result
```

### Pipeline Operations

Support for combining with other commands:

```bash
# Save results to file
ctyun-cli ecs list --output json > instances.json

# Count instances
ctyun-cli ecs list --output json | jq '. | length'

# Filter specific status instances
ctyun-cli ecs list --output json | jq '.[] | select(.status == "running")'
```

## 📚 Documentation

- **[Usage Guide](docs/usage.md)** - Detailed usage instructions and best practices
- **[Monitoring Service Documentation](MONITOR_USAGE.md)** - Complete guide for 54 monitoring APIs
- **[Redis Service Documentation](REDIS_CLI_USAGE.md)** - Redis distributed cache service usage guide
- **[IAM Service Documentation](IAM_USAGE.md)** - Identity access management service guide
- **[Project Overview](docs/overview.md)** - Architecture design and technical specifications
- **[Security Guide](docs/security-guide.md)** - Security configuration and best practices

## 🤝 Support

If you encounter issues or have suggestions:

- 📧 Email the technical support team
- 💬 Submit an Issue: https://github.com/fengyucn/ctyun-cli/issues
- 📖 Check the complete documentation for help

## 📋 System Requirements

- Python 3.8 or higher
- Stable internet connection
- CTYun account and valid Access Key

## 🔐 Security Tips

- ⚠️ Avoid hardcoding Access Keys and Secret Keys in your code
- ✅ Use environment variables for credential configuration
- ✅ Rotate your access keys regularly
- ✅ Create different access keys for different purposes

## 📝 Version Information

**Current Version:** 1.3.3

**Update History:**
- ✨ Added Redis distributed cache service support (12 commands/16 APIs)
- ✨ Complete monitoring service support (54 APIs)
- ✨ Added IAM and EBS service modules
- ✨ Optimized authentication mechanism with EOP signature support
- 🔧 Improved project documentation and usage guides
- 🐛 Fixed known issues and performance optimizations

## 📜 Open Source License

This project is licensed under the MIT License and welcomes usage and contributions.

**Author: Y.FENG | Email: popfrog@gmail.com**

---

**🚀 Making CTYun resource management simpler! Install and try it now!**

**Installation Command:** `pip install ctyun-cli`