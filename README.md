# University Room Reservation System

A blockchain-powered room reservation system built with Hyperledger Fabric and Python. This system allows students and professors to make reservations for study rooms in university blocks 33, 34, and 35.

## 🏗️ Architecture

The system consists of:

- **Hyperledger Fabric Network**: 3 peer organizations (one per block) with an orderer
- **Smart Contract (Chaincode)**: Written in Go, handles reservation logic and validation
- **Python Web Application**: Flask-based web interface with real-time updates
- **WebSocket Support**: Real-time notifications and calendar updates

## 🏢 System Overview

### Blocks and Rooms

- **3 Blocks**: 33, 34, and 35
- **3 Floors per block**: 1, 2, and 3
- **5 Rooms per floor**: {floor}00, {floor}01, {floor}02, {floor}03, {floor}04
- **Total**: 45 study rooms

### User Roles

- **Students**: Can make reservations for their own use (max 2 hours)
- **Professors**: Can make reservations and cancel any existing reservation

### Business Rules

- **Operating Hours**: 06:00 - 23:00
- **Reservation Durations**: 1 hour, 1.5 hours, or 2 hours
- **Maximum Duration**: 2 hours per reservation
- **Conflict Prevention**: No overlapping reservations allowed
- **Professor Override**: Professors can cancel student reservations

## 📋 Prerequisites

### Software Requirements

- **Docker & Docker Compose**: For running Hyperledger Fabric network
- **Python 3.8+**: For the web application
- **Node.js 14+**: For Hyperledger Fabric tools
- **Go 1.19+**: For chaincode compilation

### Hyperledger Fabric Tools

Install the following Hyperledger Fabric binaries:

- `peer`
- `orderer`
- `configtxgen`
- `cryptogen`

## 🚀 Installation & Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd university-room-reservation
```

### 2. Install Hyperledger Fabric Binaries

```bash
# Download and install Hyperledger Fabric binaries
curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.4.7 1.5.2
export PATH=$PWD/fabric-samples/bin:$PATH
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Make Scripts Executable (macOS/Linux)

```bash
chmod +x network/scripts/start-network.sh
chmod +x network/scripts/stop-network.sh
```

## 🏃‍♂️ Running the System

### 1. Start the Blockchain Network

```bash
# Navigate to network directory
cd network

# Start the network (this will take a few minutes on first run)
./scripts/start-network.sh
```

This script will:

- Generate cryptographic material for all organizations
- Start Docker containers for peers, orderer, and CouchDB
- Create and configure the channel
- Deploy and initialize the smart contract
- Set up the complete blockchain network

### 2. Start the Web Application

```bash
# In a new terminal, navigate to client directory
cd client

# Start the Flask application
python app.py
```

### 3. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

## 🖥️ Using the System

### Login Process

1. Select your role (Student or Professor)
2. Enter your details:
   - User ID
   - Full Name
   - Email
   - Primary Block (33, 34, or 35)

### Student Dashboard Features

- **Calendar View**: Visual calendar showing all reservations
- **Make Reservation**: Book rooms with date, time, and duration selection
- **My Reservations**: View and manage your own reservations
- **Room Availability**: Check which rooms are available for specific times
- **Real-time Updates**: Live notifications when reservations are made or cancelled

### Professor Dashboard Features

- **All Student Features**: Plus additional administrative capabilities
- **All Reservations View**: See reservations from all users
- **Cancel Any Reservation**: Override student reservations
- **Priority Booking**: Make reservations even when rooms are occupied
- **Advanced Filtering**: Filter reservations by block, date, or user type

### Making a Reservation

1. Select the block (33, 34, or 35)
2. Choose a room from the dropdown
3. Pick a date (today or future)
4. Select start time (06:00-23:00)
5. Choose duration (1, 1.5, or 2 hours)
6. Click "Make Reservation"

### Real-time Features

- **Live Calendar**: Updates automatically when new reservations are made
- **Network Status**: Shows connected blockchain peers
- **Instant Notifications**: Real-time alerts for reservation changes
- **WebSocket Connection**: Maintains live connection for updates

## 🔧 Configuration

### Environment Variables

Edit `config.env` to customize:

```env
# Flask Configuration
FLASK_APP=client/app.py
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Blockchain Configuration
CHANNEL_NAME=universitychannel
CHAINCODE_NAME=room-reservation

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### Network Configuration

The blockchain network configuration is in:

- `network/docker-compose.yaml`: Container definitions
- `network/configtx.yaml`: Channel and organization configuration
- `network/crypto-config.yaml`: Cryptographic material setup

## 🛠️ Development

### Project Structure

```
university-room-reservation/
├── network/                      # Hyperledger Fabric network
│   ├── docker-compose.yaml      # Docker containers
│   ├── configtx.yaml           # Channel configuration
│   ├── crypto-config.yaml      # Crypto material config
│   ├── connection-profile.json  # Network connection profile
│   └── scripts/                 # Network management scripts
├── chaincode/                   # Smart contract (Go)
│   └── room-reservation/
│       ├── main.go             # Main chaincode file
│       └── go.mod              # Go dependencies
├── client/                     # Python web application
│   ├── app.py                  # Flask web server
│   ├── blockchain_client.py    # Blockchain interaction layer
│   ├── static/                 # CSS, JS, images
│   └── templates/              # HTML templates
├── requirements.txt            # Python dependencies
├── config.env                  # Environment configuration
└── README.md                   # This file
```

### Smart Contract Functions

The chaincode provides these functions:

- `InitLedger()`: Initialize the system with rooms
- `RegisterUser()`: Register a new user
- `MakeReservation()`: Create a room reservation
- `CancelReservation()`: Cancel an existing reservation
- `GetReservation()`: Get reservation details
- `GetAllReservations()`: Get all reservations
- `GetReservationsByUser()`: Get user's reservations
- `GetReservationsByRoom()`: Get room's reservations
- `GetAvailableRooms()`: Get available rooms for a time period

### API Endpoints

The Flask application provides these REST endpoints:

- `POST /api/login`: User authentication
- `GET /api/rooms`: Get all rooms
- `GET /api/reservations`: Get reservations (with filters)
- `POST /api/reservations`: Make a new reservation
- `DELETE /api/reservations/<id>`: Cancel a reservation
- `GET /api/available-rooms`: Check room availability
- `GET /api/network-info`: Get blockchain network status

## 🔍 Monitoring & Debugging

### View Blockchain Logs

```bash
# View all container logs
docker-compose logs

# View specific peer logs
docker logs peer0.block33.university.com

# View orderer logs
docker logs orderer.university.com
```

### Access CouchDB

CouchDB web interfaces are available at:

- Block 33: http://localhost:5984/\_utils
- Block 34: http://localhost:6984/\_utils
- Block 35: http://localhost:7984/\_utils

Login with: `admin` / `adminpw`

### Check Network Status

```bash
# List running containers
docker ps

# Check peer channel list
docker exec cli peer channel list

# Query chaincode
docker exec cli peer chaincode query -C universitychannel -n room-reservation -c '{"function":"GetAllReservations","Args":[]}'
```

## 🛑 Stopping the System

### Stop Web Application

Press `Ctrl+C` in the terminal running the Flask app.

### Stop Blockchain Network

```bash
cd network
./scripts/stop-network.sh
```

This will:

- Stop all Docker containers
- Remove containers and volumes
- Clean up generated certificates and artifacts

## 🐛 Troubleshooting

### Common Issues

**1. Docker Permission Errors**

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and log back in
```

**2. Port Already in Use**

```bash
# Check what's using the port
netstat -tulpn | grep :5000
# Kill the process or change the port in config
```

**3. Chaincode Installation Fails**

```bash
# Check Go version and GOPATH
go version
echo $GOPATH

# Rebuild chaincode
cd chaincode/room-reservation
go mod tidy
```

**4. Network Start Fails**

```bash
# Clean everything and restart
./scripts/stop-network.sh
docker system prune -f
./scripts/start-network.sh
```

**5. Python Dependencies Issues**

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies one by one
pip install Flask==2.3.3
pip install hfc==0.10.0
# ... etc
```

### Debug Mode

Enable debug mode by setting in `config.env`:

```env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

## 📚 Additional Resources

- [Hyperledger Fabric Documentation](https://hyperledger-fabric.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Go Programming Language](https://golang.org/doc/)



