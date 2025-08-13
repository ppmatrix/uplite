# 📡 UpLite Monitoring Guide

This guide shows you how to add addresses/services to monitor in your UpLite dashboard.

## 🚀 Quick Start

You now have **5 sample connections** already configured:
- **Google** - Website monitoring
- **GitHub API** - API endpoint monitoring  
- **Cloudflare DNS** - Ping connectivity test
- **Local SSH** - TCP port monitoring
- **UpLite App** - Self-monitoring

## 🔧 Methods to Add Connections

### 1. 🌐 Web Interface (Recommended)

1. **Start UpLite**: `uv run uplite`
2. **Login** at `http://localhost:5001` with:
   - Username: `admin`
   - Password: `admin123`
3. **Navigate** to "Connections" in the menu
4. **Click** "Add Connection" button
5. **Fill in** the connection details:
   - **Name**: Friendly name for your service
   - **Type**: Choose from HTTP, Ping, TCP, Database
   - **Target**: URL, IP address, or hostname
   - **Port**: Optional port number
   - **Timeout**: How long to wait for response
   - **Check Interval**: How often to check (seconds)

### 2. 📟 Command Line Interface

Use the `add_connection.py` script:

```bash
# Basic syntax
uv run python add_connection.py "Name" type "target" [options]

# Examples
uv run python add_connection.py "My Website" http "https://mysite.com"
uv run python add_connection.py "Router" ping "192.168.1.1"  
uv run python add_connection.py "Database" tcp "localhost" -p 5432
```

## 📋 Connection Types & Examples

### 🌐 HTTP/HTTPS Monitoring
Monitor websites, APIs, and web services:

```bash
# Website monitoring
uv run python add_connection.py "My Website" http "https://example.com"

# API endpoint
uv run python add_connection.py "API Health" http "http://api.example.com/health"

# Local service
uv run python add_connection.py "Local App" http "http://localhost:8080"
```

**Use cases:**
- Website uptime monitoring
- API endpoint health checks
- Web service availability
- Load balancer status

### 📡 Ping Monitoring  
Test network connectivity:

```bash
# Router connectivity
uv run python add_connection.py "Router" ping "192.168.1.1"

# Internet connectivity  
uv run python add_connection.py "Google DNS" ping "8.8.8.8"

# Remote server
uv run python add_connection.py "Remote Server" ping "server.example.com"
```

**Use cases:**
- Network connectivity tests
- Router/gateway monitoring
- Internet access verification
- Remote server reachability

### 🔌 TCP Port Monitoring
Check if specific services are running:

```bash
# SSH service
uv run python add_connection.py "SSH" tcp "192.168.1.100" -p 22

# Web server
uv run python add_connection.py "Web Server" tcp "localhost" -p 80

# Custom application
uv run python add_connection.py "My App" tcp "server.local" -p 3000
```

**Use cases:**
- Service port availability
- Application server monitoring
- Network service checks
- Firewall testing

### 🗄️ Database Monitoring
Monitor database connectivity:

```bash
# PostgreSQL
uv run python add_connection.py "PostgreSQL" database "db.example.com" -p 5432

# MySQL  
uv run python add_connection.py "MySQL" database "localhost" -p 3306

# Redis
uv run python add_connection.py "Redis" database "cache.local" -p 6379
```

**Use cases:**
- Database server monitoring
- Connection pool health
- Database cluster status
- Cache service availability

## ⚙️ Advanced Options

### Custom Timeout & Intervals

```bash
# Quick checks (5s timeout, check every 30s)
uv run python add_connection.py "Critical API" http "https://api.critical.com" -t 5 -i 30

# Slow services (30s timeout, check every 5 minutes)  
uv run python add_connection.py "Slow Service" http "https://slow.service.com" -t 30 -i 300
```

### With Descriptions

```bash
uv run python add_connection.py "Production DB" database "prod-db.company.com" \
  -p 5432 -d "Main production PostgreSQL database" -t 10 -i 60
```

## 📊 Monitoring Dashboard

Once connections are added:

1. **Dashboard View**: See all connections status at a glance
2. **Real-time Updates**: Status updates automatically every 30 seconds  
3. **Manual Checks**: Click "Check Now" for immediate status updates
4. **Response Times**: See how fast your services respond
5. **Error Details**: View specific error messages when connections fail

## 🔍 Connection Status Colors

- 🟢 **Green (Up)**: Service is responding normally
- 🔴 **Red (Down)**: Service is not responding or failed
- 🟡 **Yellow (Unknown)**: Service hasn't been checked yet

## 📈 Best Practices

### 🎯 What to Monitor

**Essential Services:**
- Your main website/application
- Database servers
- API endpoints
- Email servers
- DNS servers
- Load balancers

**Infrastructure:**
- Network gateways/routers
- Firewalls
- VPN servers
- Backup systems
- Monitoring systems

### ⏱️ Recommended Settings

**Critical Services:**
- Timeout: 5-10 seconds
- Check Interval: 30-60 seconds

**Normal Services:**  
- Timeout: 10-15 seconds
- Check Interval: 60-300 seconds

**Slow/Batch Services:**
- Timeout: 30-60 seconds  
- Check Interval: 300-600 seconds

### 🚨 Naming Conventions

Use clear, descriptive names:
- ✅ "Production API"
- ✅ "Main Database" 
- ✅ "Customer Website"
- ❌ "Server1"
- ❌ "DB"
- ❌ "Test"

## 🔧 Managing Connections

### Via Web Interface:
- **Edit**: Modify connection settings
- **Delete**: Remove connections you no longer need
- **Check Now**: Manual status check
- **Enable/Disable**: Turn monitoring on/off

### Via Command Line:
```bash
# List all connections
uv run python -c "
from src.uplite.app import create_app, db
from src.uplite.models.connection import Connection
app = create_app()
with app.app_context():
    connections = Connection.query.all()
    for c in connections:
        print(f'{c.name}: {c.connection_type} -> {c.target}')
"
```

## 🏃‍♂️ Getting Started Now

1. **Start UpLite**: `uv run uplite`
2. **Login** at `http://localhost:5001` (admin/admin123)
3. **Go to Connections** to see the sample connections
4. **Click "Check Now"** on any connection to test it
5. **Add your own** services using the web interface or CLI

Your monitoring dashboard is ready to use! 🎉
