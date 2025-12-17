# CTYun CLI Tool 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Count](https://img.shields.io/badge/APIs-175+-brightgreen.svg)](#api-statistics)
[![Commands](https://img.shields.io/badge/Commands-151+-orange.svg)](#feature-overview)
[![Modules](https://img.shields.io/badge/Modules-8+-blue.svg)](#feature-overview)

**CTYun CLI Tool** is a powerful enterprise-grade command-line tool for China Telecom Cloud (CTYun), enabling easy cloud resource management from your terminal. Supports ECS, monitoring & alerting, security protection, Redis distributed cache service, billing queries, and more.

**📊 Scale Statistics: 15,000+ lines of code, 175+ APIs, 151+ commands, 8+ service modules**

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

## 📊 Feature Overview

| Service Module | Commands | APIs | Description |
|----------------|----------|------|-------------|
| **ECS (Elastic Cloud Server)** | 50 | 42 | Instance management, snapshots, keypairs, cloud host groups, auto-renewal configuration |
| **Monitor (Monitoring Service)** | 54 | 54 | Monitoring metrics, alert management, Top-N statistics, events |
| **Redis (Distributed Cache)** | 13 | 16 | Instance management, performance monitoring, network config, complete creation functions |
| **Billing (Billing Query)** | 12 | 20 | Account balance, monthly bills, consumption analysis |
| **Security (Security Guard)** | 5 | 21 | Security scanning, vulnerability management, risk assessment |
| **IAM (Identity Access Management)** | 2 | 2 | Project management, permission control |
| **EBS (Elastic Block Storage)** | 1 | 1 | Block storage management |
| **CDA (Cloud Dedicated Access)** | 14 | 19 | Dedicated gateway, physical lines, VPC management, health checks, link probing |
| **Total** | **151** | **175** | **Covering CTYun Core Services** |

### 📈 Module Details

#### 🖥️ ECS Module - Cloud Server Management (50 Commands/42 APIs)
**Core Features:**
- Instance lifecycle management
- Snapshot and backup policies
- Keypairs and security groups
- Cloud host group management
- Auto-renewal configuration
- DNS record management

**Common Commands:**
```bash
ctyun-cli ecs list                              # List instances
ctyun-cli ecs get-instance-detail             # Get instance details
ctyun-cli ecs list-snapshots                   # List snapshots
ctyun-cli ecs list-keypairs                    # List keypairs
ctyun-cli ecs get-auto-renew-config           # Get auto-renewal configuration
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

#### 🗄️ Redis Module - Distributed Cache Service (13 Commands/16 APIs)
**Core Features:**
- 🔥 **Complete Instance Creation** - Full Redis instance creation with 25+ API parameters
- Redis instance management and queries
- Performance monitoring and diagnostic analysis
- Network configuration management
- Backup and recovery operations
- Resource specification checks

**New Feature Highlights (v1.3.11):**
- 📊 **Pagination Query Support** - Flexible pagination parameters for large task data display
- 🎯 **Smart Response Handling** - Compatible with both array and pagination object response formats
- ⚡ **Multiple Output Formats** - Support for table/json/yaml output formats for different scenarios

**Common Commands:**
```bash
# 🔥 New Feature: Complete Redis Instance Creation (25+ parameters)
ctyun-cli redis create-instance \
  --instance-name my-redis \
  --edition StandardSingle \
  --engine-version 6.0 \
  --shard-mem-size 8 \
  --zone-name cn-huabei2-tj-1a-public-ctcloud \
  --vpc-id <vpc_id> \
  --subnet-id <subnet_id> \
  --secgroups <security_group_id> \
  --password Test@123456 \
  --dry-run

# Basic Redis Instance Management
ctyun-cli redis list-instances                 # List Redis instances
ctyun-cli redis get-instance-metrics         # Get instance performance metrics
ctyun-cli redis create-backup                # Create instance backup
ctyun-cli redis list-network-configs         # List network configurations
ctyun-cli redis check-resources              # Check available specifications
ctyun-cli redis zones                        # Query availability zone information
```

#### 💰 Billing Module - Billing Management (12 Commands/20 APIs)
**Core Features:**
- Account balance queries
- Monthly bill statistics
- Consumption detail analysis
- Budget management

**Common Commands:**
```bash
ctyun-cli billing balance                      # Query account balance
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
ctyun-cli security scan-result                # Query scan results
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
ctyun-cli ebs list-disks                       # List cloud disk volumes
```

#### 🔌 CDA Module - Cloud Dedicated Access Management (14 Commands/19 APIs) ⭐ **NEW! (2025-12-02)**
**Core Features:**
- Dedicated gateway lifecycle management
- Physical line access and configuration
- VPC network management and routing configuration
- Health checks and link probing
- Cross-account authorization management
- Dedicated switch monitoring

**Today's New APIs (2025-12-02):**
- Cloud dedicated access health check status query
- Cloud dedicated access link probing query
- Cloud dedicated access VPC detail query
- Dedicated switch query (returns 358 devices)
- Dedicated gateway bound cloud express query

**Common Commands:**
```bash
# Dedicated Gateway Management
ctyun-cli cda gateway list                   # List dedicated gateways
ctyun-cli cda gateway count                  # Count dedicated gateways
ctyun-cli cda gateway physical-lines        # View bound physical lines
ctyun-cli cda gateway cloud-express          # Query bound cloud express ⭐ New

# VPC Management
ctyun-cli cda vpc list                       # List VPCs
ctyun-cli cda vpc count                      # Count VPCs
ctyun-cli cda vpc info                        # Query VPC details ⭐ New

# Physical Line Management
ctyun-cli cda physical-line list            # List physical lines
ctyun-cli cda physical-line access-points   # List access points
ctyun-cli cda physical-line count            # Count physical lines

# Health Checks and Link Probing
ctyun-cli cda health-check config           # Query health check configuration
ctyun-cli cda health-check status           # Query health check status ⭐ New
ctyun-cli cda health-check link-probe        # Query link probing history ⭐ New

# Route Management
ctyun-cli cda static-route list             # List static routes
ctyun-cli cda bgp-route list                 # List BGP routes

# Cross-account Authorization
ctyun-cli cda account-auth list             # List cross-account authorizations
ctyun-cli cda account-auth count             # Count cross-account authorizations

# Switch Management
ctyun-cli cda switches                       # Query dedicated switches ⭐ New
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
- **[Redis Instance Creation Guide](REDIS_CREATE_INSTANCE.md)** - Complete Redis instance creation with 25+ parameters
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

**Current Version:** 1.6.0 (Latest)

**Major Update v1.6.0 - VPC Module Comprehensive Upgrade (2025-12-03):**
- 🚀 **Complete VPC new-series API Implementation** - High-performance VPC queries with cursor-based pagination
- ✨ **4 New Core VPC Commands** - `vpc new-list`, `vpc subnet new-list`, `vpc security new-query`, `vpc show`
- ⚡ **Significant Performance Improvement** - nextToken-based cursor pagination supporting large data queries
- 🔍 **Enhanced Query Functions** - Fuzzy queries, multi-dimensional filtering, idempotency guarantee
- 📋 **API Statistics Update** - VPC module supports 11+ API interfaces, covering complete network management scenarios

**Historical Version v1.5.0 - Billing Module Comprehensive Upgrade (2025-12-02):**
- 🎉 **Complete Implementation of 10 Billing APIs** - Complete billing query system including annual/monthly, on-demand, and consumption type summaries
- 🆕 **New On-demand Bill Resource + Billing Cycle Command** - `ondemand-resource-cycle` supports resource-dimension and daily queries
- 🔧 **Optimized All Billing Command Output Formats** - Unified support for `--output json/yaml/table` parameters
- 💰 **Fixed Amount Display Issues** - Removed scientific notation, added thousand separators for better readability
- 📊 **Smart Data Return Strategy** - JSON/YAML returns complete original data, table returns user-friendly format
- 🗂️ **Complete Field Mapping System** - Chinese mapping for billing modes, bill types, payment methods
- 🔍 **Enhanced Filtering and Pagination** - Multi-dimensional filtering by product code, resource ID, contract ID

**Major Update v1.4.0 - Cloud Dedicated Access CDA Module Complete Launch (2025-12-02):**
- 🔥 **Brand New Cloud Dedicated Access CDA Service Module** - 14 new commands covering 19 API interfaces
- ✨ **Complete Dedicated Gateway Lifecycle Management** - Create, query, delete, bind physical lines
- ✨ **Physical Line Access Management** - Access point queries, line count statistics, detailed information
- ✨ **Intelligent VPC Network Management** - VPC lists, detail queries, count statistics, routing configuration
- ✨ **Health Check Monitoring System** - Configuration queries, status monitoring, link probing history analysis
- ✨ **Route Management Functions** - Static route and BGP route query configuration
- ✨ **Cross-account Authorization Management** - Authorization list queries and statistical analysis
- ✨ **Dedicated Switch Monitoring** - Real-time monitoring and detailed information for 358 devices
- 🔧 **Enterprise-grade EOP Signature Authentication** - Complete CTYun API signature mechanism
- 🔧 **Multi-endpoint Automatic Retry** - Improved API call success rate and stability
- 📊 **Complete CLI Output Formats** - Support for table, JSON, YAML display formats

**Major Update v1.3.11 - Feature Enhancement:**
- 📊 **Pagination Query Support** - Flexible pageNumber and pageSize parameters for large task data display
- 🎯 **Smart Response Handling** - Compatible with both array and pagination object response formats
- ⚡ **Multiple Output Formats** - Support for table/json/yaml output formats for different scenarios

**Major Update v1.3.10 - IAM Feature Enhancement:**
- 🔥 **New IAM Paginated Query Resource Information API** - Support for complete resource field display
- ✨ **Enhanced IAM Command Line Interface** - Including complete information like accountid, projectsetid
- 🔧 **Optimized Resource Data Display** - 10 columns of detailed information with intelligent truncation and formatting

**Major Update v1.3.9 - Redis Function Comprehensive Upgrade:**
- 🔥 **Re-developed Redis create-instance Command** - Support for complete 25+ API parameters
- ✨ **Enterprise-grade Redis Instance Management** - Support for BASIC/PLUS/Classic three version types
- ✨ **Intelligent Parameter Validation System** - Comprehensive parameter validation and error prompts
- ✨ **Preview and Resource Check Functions** - --dry-run and --check-resources options
- ✨ **Complete Billing Mode Support** - Annual/monthly, auto-renewal, on-demand billing
- ✨ **High Availability Deployment Solutions** - Multi-availability zone, dual replica, cluster deployment support

**Historical Updates:**
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