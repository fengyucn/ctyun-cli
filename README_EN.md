# CTYun CLI Tool

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful command-line tool for China Telecom Cloud (CTYun), enabling easy cloud resource management from your terminal. Supports ECS, monitoring & alerting, security protection, billing queries, and more.

[简体中文](README.md) | English

## ✨ Why Choose CTYun CLI?

- 🚀 **Efficient & Convenient** - Manage cloud resources with a single command, say goodbye to tedious console operations
- 🔐 **Secure & Reliable** - Enterprise-grade EOP signature authentication with environment variable support for credential protection
- 📊 **Feature-Rich** - 70+ APIs covering ECS, monitoring, security, and billing management
- 🎯 **Easy to Use** - Clear command structure with rich examples, get started in 5 minutes
- 🔧 **Flexible Configuration** - Support for config files, environment variables, and multiple profiles

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

# Check current configuration
ctyun-cli show-config

# List ECS instances
ctyun-cli ecs list

# Query account balance
ctyun-cli billing balance
```

## 🎯 Core Features

### 🖥️ ECS Management

Manage your cloud server instances with complete functionality including queries, monitoring, snapshots, and backups.

```bash
# List all ECS instances
ctyun-cli ecs list

# Query region information
ctyun-cli ecs regions

# Query auto-renewal configuration
ctyun-cli ecs get-auto-renew-config --region-id cn-north-1 --instance-id i-xxxxx

# List snapshots
ctyun-cli ecs list-snapshots --region-id cn-north-1

# Query volume statistics
ctyun-cli ecs get-volume-statistics --region-id cn-north-1

# List keypairs
ctyun-cli ecs list-keypairs --region-id cn-north-1

# List backup policies
ctyun-cli ecs list-backup-policies --region-id cn-north-1

# List affinity groups
ctyun-cli ecs list-affinity-groups --region-id cn-north-1
```

**Supported Features:**
- ✅ Instance query & status management
- ✅ Region & availability zone queries
- ✅ Snapshot management (list, details)
- ✅ Volume management & statistics
- ✅ Keypair management
- ✅ Backup policy & status queries
- ✅ DNS record queries
- ✅ Affinity group management
- ✅ Async task queries
- ✅ Auto-renewal configuration

### 📊 Monitoring & Alerting

Real-time monitoring of cloud resource status, set alert rules, and detect issues promptly.

```bash
# Query monitoring data (CPU utilization)
ctyun-cli monitor query-data --region-id cn-north-1 --metric CPUUtilization

# Query alert history
ctyun-cli monitor query-alert-history --region-id cn-north-1

# Query alarm rules
ctyun-cli monitor query-alarm-rules --region-id cn-north-1 --service ctecs

# Query Top 10 CPU usage
ctyun-cli monitor query-cpu-top --region-id cn-north-1 --top-n 10

# Query Top 10 memory usage
ctyun-cli monitor query-mem-top --region-id cn-north-1 --top-n 10

# Query inspection task overview
ctyun-cli monitor query-inspection-task-overview --region-id cn-north-1
```

**Monitoring Modules:**
- 📈 **Metric Queries** (8 APIs) - Monitoring data, metric lists, alert history, event history
- 🔝 **Top-N Queries** (6 APIs) - Top rankings for CPU, memory, dimensions, resources, metrics, events
- 🚨 **Alert Management** (7 APIs) - Alarm rules, contacts, contact groups, blacklist
- 📋 **Notification Management** (4 APIs) - Notification templates, template variables, notification records
- 🔍 **Inspection** (5 APIs) - Inspection tasks, items, and history

For detailed usage → [Complete Monitoring Documentation](MONITOR_USAGE.md)

### 🛡️ Security Protection

View security protection status, manage vulnerability scanning and security policies.

```bash
# List security agents
ctyun-cli security agents

# Query scan results
ctyun-cli security scan-result

# Query vulnerability list for specific agent
ctyun-cli security vuln-list <agent_guid>
```

### 💰 Billing Management

Stay on top of cloud resource costs with billing and consumption details.

```bash
# Query account balance
ctyun-cli billing balance

# Query monthly bills
ctyun-cli billing bills --month 202411

# Query consumption details
ctyun-cli billing details --start-date 2024-11-01 --end-date 2024-11-30
```

## 🔧 Advanced Configuration

### Configuration File Location

The configuration file is stored at `~/.ctyun/config` in INI format:

```ini
[default]
access_key = YOUR_ACCESS_KEY
secret_key = YOUR_SECRET_KEY
region = cn-north-1
endpoint = https://api.ctyun.cn
output_format = table
```

### Multi-Environment Configuration

Support for multiple profiles to easily switch between different accounts:

```bash
# Configure production environment
ctyun-cli configure --profile production

# Configure testing environment
ctyun-cli configure --profile testing

# Use specific profile
ctyun-cli --profile production ecs list
```

### Output Formats

Three output formats to meet different scenarios:

```bash
# Table format (default, human-readable)
ctyun-cli ecs list --output table

# JSON format (suitable for programmatic processing)
ctyun-cli ecs list --output json

# YAML format (suitable for configuration management)
ctyun-cli ecs list --output yaml
```

### Debug Mode

Enable debug mode for detailed information when troubleshooting:

```bash
ctyun-cli --debug security scan-result
```

## 📚 Complete Documentation

- [Usage Guide](docs/usage.md) - Detailed instructions and best practices
- [Monitoring Service Documentation](MONITOR_USAGE.md) - Complete guide for 28 monitoring APIs
- [Project Overview](docs/overview.md) - Architecture design and technical details
- [Security Guide](docs/security-guide.md) - Security configuration and best practices

## 🤝 Technical Support

If you encounter issues or have suggestions:

- 📧 Contact our technical support team
- 💬 Submit an Issue for feedback
- 📖 Check the complete documentation for help

## 📋 System Requirements

- Python 3.8 or higher
- Stable network connection
- CTYun account with Access Key

## 🔐 Security Tips

- ⚠️ Never hardcode Access Key and Secret Key in your code
- ✅ Use environment variables for credential configuration (recommended)
- ✅ Rotate your access keys regularly
- ✅ Create different access keys for different purposes

## 📝 Version Information

**Current Version:** 1.1.0

**Updates:**
- ✨ Added 19 ECS query APIs
- ✨ Complete monitoring service support (28 APIs)
- 🔧 Optimized authentication mechanism with EOP signature support
- 🐛 Fixed several known issues

## 📜 License

This project is licensed under the MIT License. Contributions are welcome.

---

**Get started with CTYun CLI and make cloud resource management easier!** 🚀
