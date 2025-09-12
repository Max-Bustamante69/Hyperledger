#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting University Room Reservation Network${NC}"

# Set the working directory
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Clean up any existing containers
echo -e "${YELLOW}Cleaning up existing containers...${NC}"
docker-compose down --volumes --remove-orphans

# Remove existing crypto material
echo -e "${YELLOW}Cleaning up existing crypto material...${NC}"
rm -rf crypto-config
rm -rf channel-artifacts

# Generate crypto material
echo -e "${YELLOW}Generating crypto material...${NC}"
cryptogen generate --config=./crypto-config.yaml

# Create channel artifacts directory
mkdir -p channel-artifacts

# Generate genesis block
echo -e "${YELLOW}Generating genesis block...${NC}"
configtxgen -profile UniversityOrdererGenesis -channelID system-channel -outputBlock ./channel-artifacts/genesis.block

# Generate channel configuration transaction
echo -e "${YELLOW}Generating channel configuration transaction...${NC}"
configtxgen -profile UniversityChannel -outputCreateChannelTx ./channel-artifacts/universitychannel.tx -channelID universitychannel

# Generate anchor peer transactions
echo -e "${YELLOW}Generating anchor peer transactions...${NC}"
configtxgen -profile UniversityChannel -outputAnchorPeersUpdate ./channel-artifacts/Block33MSPanchors.tx -channelID universitychannel -asOrg Block33MSP
configtxgen -profile UniversityChannel -outputAnchorPeersUpdate ./channel-artifacts/Block34MSPanchors.tx -channelID universitychannel -asOrg Block34MSP
configtxgen -profile UniversityChannel -outputAnchorPeersUpdate ./channel-artifacts/Block35MSPanchors.tx -channelID universitychannel -asOrg Block35MSP

# Start the network
echo -e "${YELLOW}Starting the blockchain network...${NC}"
docker-compose up -d

# Wait for containers to start
echo -e "${YELLOW}Waiting for containers to start...${NC}"
sleep 10

# Create the channel
echo -e "${YELLOW}Creating channel...${NC}"
docker exec cli peer channel create -o orderer.university.com:7050 -c universitychannel -f ./channel-artifacts/universitychannel.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem

# Join peers to the channel
echo -e "${YELLOW}Joining peers to channel...${NC}"

# Block 33
docker exec -e CORE_PEER_LOCALMSPID=Block33MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/peers/peer0.block33.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/users/Admin@block33.university.com/msp -e CORE_PEER_ADDRESS=peer0.block33.university.com:7051 cli peer channel join -b universitychannel.block

# Block 34
docker exec -e CORE_PEER_LOCALMSPID=Block34MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/peers/peer0.block34.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/users/Admin@block34.university.com/msp -e CORE_PEER_ADDRESS=peer0.block34.university.com:8051 cli peer channel join -b universitychannel.block

# Block 35
docker exec -e CORE_PEER_LOCALMSPID=Block35MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/peers/peer0.block35.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/users/Admin@block35.university.com/msp -e CORE_PEER_ADDRESS=peer0.block35.university.com:9051 cli peer channel join -b universitychannel.block

# Update anchor peers
echo -e "${YELLOW}Updating anchor peers...${NC}"

# Block 33 anchor peer
docker exec -e CORE_PEER_LOCALMSPID=Block33MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/peers/peer0.block33.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/users/Admin@block33.university.com/msp -e CORE_PEER_ADDRESS=peer0.block33.university.com:7051 cli peer channel update -o orderer.university.com:7050 -c universitychannel -f ./channel-artifacts/Block33MSPanchors.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem

# Block 34 anchor peer
docker exec -e CORE_PEER_LOCALMSPID=Block34MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/peers/peer0.block34.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/users/Admin@block34.university.com/msp -e CORE_PEER_ADDRESS=peer0.block34.university.com:8051 cli peer channel update -o orderer.university.com:7050 -c universitychannel -f ./channel-artifacts/Block34MSPanchors.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem

# Block 35 anchor peer
docker exec -e CORE_PEER_LOCALMSPID=Block35MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/peers/peer0.block35.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/users/Admin@block35.university.com/msp -e CORE_PEER_ADDRESS=peer0.block35.university.com:9051 cli peer channel update -o orderer.university.com:7050 -c universitychannel -f ./channel-artifacts/Block35MSPanchors.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem

# Package the chaincode
echo -e "${YELLOW}Packaging chaincode...${NC}"
docker exec cli peer lifecycle chaincode package room-reservation.tar.gz --path /opt/gopath/src/github.com/chaincode/room-reservation --lang golang --label room-reservation_1.0

# Install chaincode on all peers
echo -e "${YELLOW}Installing chaincode on peers...${NC}"

# Install on Block 33
docker exec -e CORE_PEER_LOCALMSPID=Block33MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/peers/peer0.block33.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/users/Admin@block33.university.com/msp -e CORE_PEER_ADDRESS=peer0.block33.university.com:7051 cli peer lifecycle chaincode install room-reservation.tar.gz

# Install on Block 34
docker exec -e CORE_PEER_LOCALMSPID=Block34MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/peers/peer0.block34.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/users/Admin@block34.university.com/msp -e CORE_PEER_ADDRESS=peer0.block34.university.com:8051 cli peer lifecycle chaincode install room-reservation.tar.gz

# Install on Block 35
docker exec -e CORE_PEER_LOCALMSPID=Block35MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/peers/peer0.block35.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/users/Admin@block35.university.com/msp -e CORE_PEER_ADDRESS=peer0.block35.university.com:9051 cli peer lifecycle chaincode install room-reservation.tar.gz

# Get package ID
echo -e "${YELLOW}Getting chaincode package ID...${NC}"
PACKAGE_ID=$(docker exec cli peer lifecycle chaincode queryinstalled --output json | jq -r '.installed_chaincodes[0].package_id')
echo "Package ID: $PACKAGE_ID"

# Approve chaincode for each organization
echo -e "${YELLOW}Approving chaincode for organizations...${NC}"

# Approve for Block 33
docker exec -e CORE_PEER_LOCALMSPID=Block33MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/peers/peer0.block33.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/users/Admin@block33.university.com/msp -e CORE_PEER_ADDRESS=peer0.block33.university.com:7051 cli peer lifecycle chaincode approveformyorg -o orderer.university.com:7050 --channelID universitychannel --name room-reservation --version 1.0 --package-id $PACKAGE_ID --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem

# Approve for Block 34
docker exec -e CORE_PEER_LOCALMSPID=Block34MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/peers/peer0.block34.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/users/Admin@block34.university.com/msp -e CORE_PEER_ADDRESS=peer0.block34.university.com:8051 cli peer lifecycle chaincode approveformyorg -o orderer.university.com:7050 --channelID universitychannel --name room-reservation --version 1.0 --package-id $PACKAGE_ID --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem

# Approve for Block 35
docker exec -e CORE_PEER_LOCALMSPID=Block35MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/peers/peer0.block35.university.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/users/Admin@block35.university.com/msp -e CORE_PEER_ADDRESS=peer0.block35.university.com:9051 cli peer lifecycle chaincode approveformyorg -o orderer.university.com:7050 --channelID universitychannel --name room-reservation --version 1.0 --package-id $PACKAGE_ID --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem

# Check commit readiness
echo -e "${YELLOW}Checking commit readiness...${NC}"
docker exec cli peer lifecycle chaincode checkcommitreadiness --channelID universitychannel --name room-reservation --version 1.0 --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem --output json

# Commit the chaincode
echo -e "${YELLOW}Committing chaincode...${NC}"
docker exec cli peer lifecycle chaincode commit -o orderer.university.com:7050 --channelID universitychannel --name room-reservation --version 1.0 --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem --peerAddresses peer0.block33.university.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/peers/peer0.block33.university.com/tls/ca.crt --peerAddresses peer0.block34.university.com:8051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/peers/peer0.block34.university.com/tls/ca.crt --peerAddresses peer0.block35.university.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/peers/peer0.block35.university.com/tls/ca.crt

# Initialize the ledger
echo -e "${YELLOW}Initializing ledger...${NC}"
docker exec cli peer chaincode invoke -o orderer.university.com:7050 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/university.com/orderers/orderer.university.com/msp/tlscacerts/tlsca.university.com-cert.pem -C universitychannel -n room-reservation --peerAddresses peer0.block33.university.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block33.university.com/peers/peer0.block33.university.com/tls/ca.crt --peerAddresses peer0.block34.university.com:8051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block34.university.com/peers/peer0.block34.university.com/tls/ca.crt --peerAddresses peer0.block35.university.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/block35.university.com/peers/peer0.block35.university.com/tls/ca.crt -c '{"function":"InitLedger","Args":[]}'

echo -e "${GREEN}Network started successfully!${NC}"
echo -e "${GREEN}Chaincode deployed and initialized!${NC}"
echo ""
echo -e "${YELLOW}Network components:${NC}"
echo -e "  • Orderer: orderer.university.com:7050"
echo -e "  • Peer Block 33: peer0.block33.university.com:7051"
echo -e "  • Peer Block 34: peer0.block34.university.com:8051"
echo -e "  • Peer Block 35: peer0.block35.university.com:9051"
echo -e "  • CouchDB instances on ports: 5984, 6984, 7984"
echo ""
echo -e "${YELLOW}You can now start the Python client application:${NC}"
echo -e "  cd ../client && python app.py"
