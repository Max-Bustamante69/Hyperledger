# Quick Start Guide

Get the University Room Reservation System running in 5 minutes!

## 🚀 Prerequisites

Make sure you have:

- **Docker Desktop** (running)
- **Python 3.8+**
- **Go 1.19+**
- **Git**

## 📥 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd university-room-reservation
```

### 2. Run Setup Script

```bash
python setup.py
```

This will automatically:

- Check all prerequisites
- Create Python virtual environment
- Install dependencies
- Download Hyperledger Fabric tools
- Set up directories and permissions

## 🏃‍♂️ Start the System

### 1. Start Blockchain Network

```bash
cd network
./scripts/start-network.sh
```

⏱️ _This takes 3-5 minutes on first run_

### 2. Start Web Application

```bash
# In a new terminal
cd client
python app.py
```

### 3. Open Browser

Navigate to: **http://localhost:5000**

## 🎯 Quick Demo

### Login as Student

1. Select "Student" role
2. Enter details:
   - User ID: `student1`
   - Name: `John Doe`
   - Email: `john@university.edu`
   - Block: `33`

### Make Your First Reservation

1. Choose Block 33, Room 100
2. Select today's date
3. Pick time: 10:00
4. Duration: 1 hour
5. Click "Make Reservation"

### Login as Professor (New Tab)

1. Open new tab: http://localhost:5000
2. Select "Professor" role
3. Enter details:
   - User ID: `prof1`
   - Name: `Dr. Smith`
   - Email: `smith@university.edu`
   - Block: `33`

### View All Reservations

- Go to "All Reservations" tab
- See the student's reservation
- Try canceling it (professor privilege)

## 🛑 Stop the System

### Stop Web App

Press `Ctrl+C` in the Flask terminal

### Stop Blockchain

```bash
cd network
./scripts/stop-network.sh
```

## 🔍 Verify Everything Works

### Check Network Status

```bash
docker ps
# Should show 7 running containers
```

### Check Web App

- Login page loads ✅
- Can create reservations ✅
- Calendar shows events ✅
- Real-time updates work ✅

## 🆘 Troubleshooting

### Common Issues

**"Docker not running"**

```bash
# Start Docker Desktop application
```

**"Port 5000 already in use"**

```bash
# Kill process using port
lsof -ti:5000 | xargs kill -9
```

**"Permission denied" (Linux/Mac)**

```bash
chmod +x network/scripts/*.sh
```

**Network won't start**

```bash
cd network
./scripts/stop-network.sh
docker system prune -f
./scripts/start-network.sh
```

### Get Help

- Check full **README.md** for detailed instructions
- Look at container logs: `docker-compose logs`
- Ensure all prerequisites are installed

## 📱 Features to Try

### Student Features

- ✅ Make reservations
- ✅ View personal reservations
- ✅ Check room availability
- ✅ Real-time calendar updates

### Professor Features

- ✅ All student features
- ✅ View all reservations
- ✅ Cancel any reservation
- ✅ Override existing bookings
- ✅ Advanced filtering

### Real-time Features

- ✅ Live calendar updates
- ✅ WebSocket notifications
- ✅ Network status monitoring
- ✅ Instant reservation alerts

---

🎉 **You're all set!** The system is now running with a complete blockchain network and web interface.

