import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid
import hashlib
import time
import pickle
import os

# For this demo, we'll simulate the blockchain client with actual blockchain structure
# In a real implementation, you'd use the Hyperledger Fabric Python SDK

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Transaction:
    """Represents a blockchain transaction"""
    def __init__(self, tx_type: str, data: dict, user_id: str):
        self.tx_id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.tx_type = tx_type  # "REGISTER_USER", "MAKE_RESERVATION", "CANCEL_RESERVATION"
        self.data = data
        self.user_id = user_id
        self.signature = self._generate_signature()
    
    def _generate_signature(self) -> str:
        """Generate transaction signature (simplified)"""
        content = f"{self.tx_id}{self.timestamp}{self.tx_type}{json.dumps(self.data, sort_keys=True)}{self.user_id}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            'tx_id': self.tx_id,
            'timestamp': self.timestamp,
            'tx_type': self.tx_type,
            'data': self.data,
            'user_id': self.user_id,
            'signature': self.signature
        }

class Block:
    """Represents a blockchain block"""
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = self._calculate_merkle_root()
        self.nonce = 0
        self.hash = self._calculate_hash()
    
    def _calculate_merkle_root(self) -> str:
        """Calculate Merkle root of transactions"""
        if not self.transactions:
            return hashlib.sha256("".encode()).hexdigest()
        
        tx_hashes = [tx.signature for tx in self.transactions]
        while len(tx_hashes) > 1:
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                if i + 1 < len(tx_hashes):
                    combined = tx_hashes[i] + tx_hashes[i + 1]
                else:
                    combined = tx_hashes[i] + tx_hashes[i]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            tx_hashes = new_hashes
        
        return tx_hashes[0]
    
    def _calculate_hash(self) -> str:
        """Calculate block hash"""
        content = f"{self.index}{self.timestamp}{self.previous_hash}{self.merkle_root}{self.nonce}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2):
        """Simple proof-of-work mining"""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self._calculate_hash()
    
    def to_dict(self) -> dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'hash': self.hash,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'transaction_count': len(self.transactions)
        }

class Blockchain:
    """Represents the blockchain ledger"""
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.mining_difficulty = 2
        self.mining_reward = 10
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_tx = Transaction(
            "GENESIS", 
            {"message": "University Room Reservation Blockchain Genesis Block"}, 
            "system"
        )
        genesis_block = Block(0, [genesis_tx], "0")
        genesis_block.mine_block(self.mining_difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the last block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction):
        """Add transaction to pending pool"""
        self.pending_transactions.append(transaction)
    
    def mine_pending_transactions(self, mining_reward_address: str = "system"):
        """Mine pending transactions into a new block"""
        if not self.pending_transactions:
            return None
        
        # Add mining reward transaction
        reward_tx = Transaction(
            "MINING_REWARD",
            {"reward": self.mining_reward},
            mining_reward_address
        )
        self.pending_transactions.append(reward_tx)
        
        # Create new block
        new_block = Block(
            len(self.chain),
            self.pending_transactions[:],
            self.get_latest_block().hash
        )
        
        # Mine the block
        new_block.mine_block(self.mining_difficulty)
        
        # Add to chain
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return new_block
    
    def get_chain_data(self) -> List[dict]:
        """Get the complete blockchain data"""
        return [block.to_dict() for block in self.chain]
    
    def validate_chain(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block._calculate_hash():
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_blockchain_stats(self) -> dict:
        """Get blockchain statistics"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'latest_block_hash': self.get_latest_block().hash,
            'pending_transactions': len(self.pending_transactions),
            'is_valid': self.validate_chain(),
            'mining_difficulty': self.mining_difficulty
        }

class BlockchainClient:
    def __init__(self):
        self.blockchain = Blockchain()
        self.reservations = []  # Application state derived from blockchain
        self.users = {}
        self.rooms = self._generate_rooms()
        self.pending_tx_pool = []
        
        # Persistence file paths
        self.blockchain_file = 'blockchain_state.pkl'
        self.reservations_file = 'reservations_state.pkl'
        
        logger.info("Blockchain client initialized with actual blockchain structure")
        
        # Load persisted state
        self._load_persisted_state()
        
        # Initialize with default admin user for testing if no users exist
        if not self.users:
            self.users['admin'] = {
                'id': 'admin',
                'name': 'System Admin',
                'email': 'admin@university.edu',
                'userType': 'professor',
                'block': '33'
            }
    
    def _mine_block(self):
        """Mine pending transactions into a new block"""
        new_block = self.blockchain.mine_pending_transactions()
        if new_block:
            logger.info(f"New block mined: #{new_block.index} with {len(new_block.transactions)} transactions")
            
            # Commit pending reservations to active state
            self._commit_pending_reservations()
            
            # Save blockchain state after mining
            self._save_blockchain_state()
            
            return new_block
        return None
    
    def _save_blockchain_state(self):
        """Save the complete blockchain state to disk"""
        try:
            # Save blockchain data
            blockchain_data = {
                'chain': [block.to_dict() for block in self.blockchain.chain],
                'pending_transactions': [tx.to_dict() for tx in self.blockchain.pending_transactions],
                'mining_difficulty': self.blockchain.mining_difficulty,
                'mining_reward': self.blockchain.mining_reward
            }
            
            with open(self.blockchain_file, 'wb') as f:
                pickle.dump(blockchain_data, f)
            
            # Save reservations data
            reservations_data = {
                'reservations': self.reservations,
                'users': self.users
            }
            
            with open(self.reservations_file, 'wb') as f:
                pickle.dump(reservations_data, f)
            
            logger.info("Blockchain state saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving blockchain state: {str(e)}")
    
    def _load_persisted_state(self):
        """Load the blockchain state from disk"""
        try:
            # Load blockchain data
            if os.path.exists(self.blockchain_file):
                with open(self.blockchain_file, 'rb') as f:
                    blockchain_data = pickle.load(f)
                
                # Restore blockchain
                self.blockchain.chain = []
                self.blockchain.pending_transactions = []
                
                # Recreate blocks from saved data
                for block_data in blockchain_data['chain']:
                    # Recreate transactions
                    transactions = []
                    for tx_data in block_data['transactions']:
                        tx = Transaction(
                            tx_data['tx_type'],
                            tx_data['data'],
                            tx_data['user_id']
                        )
                        # Restore original values
                        tx.tx_id = tx_data['tx_id']
                        tx.timestamp = tx_data['timestamp']
                        tx.signature = tx_data['signature']
                        transactions.append(tx)
                    
                    # Recreate block
                    block = Block(
                        block_data['index'],
                        transactions,
                        block_data['previous_hash']
                    )
                    # Restore original values
                    block.timestamp = block_data['timestamp']
                    block.hash = block_data['hash']
                    block.merkle_root = block_data['merkle_root']
                    block.nonce = block_data['nonce']
                    
                    self.blockchain.chain.append(block)
                
                # Restore pending transactions
                for tx_data in blockchain_data['pending_transactions']:
                    tx = Transaction(
                        tx_data['tx_type'],
                        tx_data['data'],
                        tx_data['user_id']
                    )
                    tx.tx_id = tx_data['tx_id']
                    tx.timestamp = tx_data['timestamp']
                    tx.signature = tx_data['signature']
                    self.blockchain.pending_transactions.append(tx)
                
                # Restore blockchain settings
                self.blockchain.mining_difficulty = blockchain_data.get('mining_difficulty', 2)
                self.blockchain.mining_reward = blockchain_data.get('mining_reward', 10)
                
                logger.info(f"Loaded blockchain with {len(self.blockchain.chain)} blocks and {len(self.blockchain.pending_transactions)} pending transactions")
            
            # Load reservations and users data
            if os.path.exists(self.reservations_file):
                with open(self.reservations_file, 'rb') as f:
                    reservations_data = pickle.load(f)
                
                self.reservations = reservations_data.get('reservations', [])
                self.users = reservations_data.get('users', {})
                
                logger.info(f"Loaded {len(self.reservations)} reservations and {len(self.users)} users")
            
        except Exception as e:
            logger.error(f"Error loading persisted state: {str(e)}")
            # Continue with empty state if loading fails
    
    def download_blockchain_state(self) -> Dict:
        """Get complete blockchain state for download"""
        try:
            blockchain_data = {
                'blockchain': {
                    'chain': [block.to_dict() for block in self.blockchain.chain],
                    'pending_transactions': [tx.to_dict() for tx in self.blockchain.pending_transactions],
                    'stats': self.blockchain.get_blockchain_stats()
                },
                'application_state': {
                    'reservations': self.reservations,
                    'users': self.users,
                    'rooms': self.rooms
                },
                'export_timestamp': datetime.now().isoformat(),
                'export_version': '1.0'
            }
            
            return {
                'success': True,
                'data': blockchain_data
            }
        except Exception as e:
            logger.error(f"Error preparing blockchain state for download: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_committed_reservations(self):
        """Get only committed (active) reservations from blockchain state"""
        return [r for r in self.reservations if r['status'] == 'active']
    
    def _commit_pending_reservations(self):
        """Commit pending reservations to active state after block mining"""
        for reservation in self.reservations:
            if reservation['status'] == 'pending':
                reservation['status'] = 'active'
                logger.info(f"Reservation {reservation['id']} committed to blockchain")
    
    def get_blockchain_data(self) -> Dict:
        """Get complete blockchain data for visualization"""
        return {
            'success': True,
            'blockchain': self.blockchain.get_chain_data(),
            'stats': self.blockchain.get_blockchain_stats(),
            'pending_transactions': [tx.to_dict() for tx in self.blockchain.pending_transactions]
        }
        
    def _generate_rooms(self):
        """Generate all rooms for the system"""
        rooms = []
        blocks = ["33", "34", "35"]
        floors = ["1", "2", "3"]
        room_numbers = ["00", "01", "02", "03", "04"]
        
        for block in blocks:
            for floor in floors:
                for room_num in room_numbers:
                    rooms.append({
                        "block": block,
                        "floor": floor,
                        "number": floor + room_num,
                        "full_name": f"Block {block} - Room {floor}{room_num}"
                    })
        return rooms
    
    def get_user_info(self, user_id: str) -> Dict:
        """Get user information with debugging"""
        user = self.users.get(user_id)
        logger.info(f"Looking up user {user_id}: {user}")
        logger.info(f"All users in system: {list(self.users.keys())}")
        return user if user else {'userType': 'student'}  # Default fallback
    
    async def initialize(self, user_id: str, user_type: str = "student"):
        """Initialize the blockchain client with user credentials"""
        try:
            logger.info(f"Blockchain client initialized for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize blockchain client: {str(e)}")
            return False
    
    async def register_user(self, user_id: str, name: str, email: str, user_type: str, block: str) -> Dict:
        """Register a new user in the blockchain"""
        try:
            # Create blockchain transaction
            tx = Transaction(
                "REGISTER_USER",
                {
                    'user_id': user_id,
                    'name': name,
                    'email': email,
                    'user_type': user_type,
                    'block': block
                },
                user_id
            )
            
            # Add to blockchain
            self.blockchain.add_transaction(tx)
            
            # Update local state
            self.users[user_id] = {
                'id': user_id,
                'name': name,
                'email': email,
                'userType': user_type,
                'block': block
            }
            
            # Debug logging
            logger.info(f"User {user_id} registered as {user_type}")
            logger.info(f"User data stored: {self.users[user_id]}")
            logger.info(f"Total users in system: {len(self.users)}")
            
            # Save state after adding transaction
            self._save_blockchain_state()
            
            # Mine block if we have enough transactions (every 3 transactions)
            if len(self.blockchain.pending_transactions) >= 3:
                self._mine_block()
            
            return {
                'success': True,
                'message': f'User {user_id} registered successfully as {user_type}',
                'transaction_id': tx.tx_id,
                'user_type': user_type  # Return for verification
            }
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def make_reservation(self, room_number: str, block: str, user_id: str, 
                             start_time: str, duration: int) -> Dict:
        """Make a room reservation"""
        try:
            # Validate time
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=duration)
            
            # Validate business rules
            if start_dt.hour < 6 or start_dt.hour >= 23 or end_dt.hour > 23:
                return {
                    'success': False,
                    'error': 'Reservations are only allowed between 06:00 and 23:00'
                }
            
            if duration not in [60, 90, 120]:
                return {
                    'success': False,
                    'error': 'Duration must be 1, 1.5, or 2 hours'
                }
            
            # Check for conflicts in COMMITTED blockchain state only
            # (This simulates real blockchain behavior where pending transactions are not visible)
            committed_reservations = self._get_committed_reservations()
            
            for reservation in committed_reservations:
                if (reservation['roomNumber'] == room_number and 
                    reservation['block'] == block and 
                    reservation['status'] == 'active'):
                    
                    res_start = datetime.fromisoformat(reservation['startTime'])
                    res_end = datetime.fromisoformat(reservation['endTime'])
                    
                    if start_dt < res_end and end_dt > res_start:
                        return {
                            'success': False,
                            'error': f'Room {room_number} in block {block} is already reserved for the requested time'
                        }
            
            # Create blockchain transaction
            reservation_id = str(uuid.uuid4())
            user = self.get_user_info(user_id)
            
            tx = Transaction(
                "MAKE_RESERVATION",
                {
                    'reservation_id': reservation_id,
                    'room_number': room_number,
                    'block': block,
                    'floor': room_number[0],
                    'user_id': user_id,
                    'user_type': user.get('userType', 'student'),
                    'start_time': start_dt.isoformat(),
                    'end_time': end_dt.isoformat(),
                    'duration': duration,
                    'status': 'active'
                },
                user_id
            )
            
            # Add to blockchain
            self.blockchain.add_transaction(tx)
            
            # Update local state (PENDING until block is mined)
            reservation = {
                'id': reservation_id,
                'roomNumber': room_number,
                'block': block,
                'floor': room_number[0],
                'userID': user_id,
                'userType': user.get('userType', 'student'),
                'startTime': start_dt.isoformat(),
                'endTime': end_dt.isoformat(),
                'duration': duration,
                'status': 'pending',  # Pending until block is mined
                'createdAt': datetime.now().isoformat()
            }
            
            self.reservations.append(reservation)
            
            # Save state after adding transaction
            self._save_blockchain_state()
            
            # Mine block if we have enough transactions
            if len(self.blockchain.pending_transactions) >= 3:
                self._mine_block()
            
            return {
                'success': True,
                'reservation_id': reservation_id,
                'transaction_id': tx.tx_id,
                'message': f'Reservation created successfully for room {room_number} in block {block}'
            }
        except Exception as e:
            logger.error(f"Error making reservation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cancel_reservation(self, reservation_id: str, cancelled_by_user_id: str) -> Dict:
        """Cancel a room reservation"""
        try:
            for reservation in self.reservations:
                if reservation['id'] == reservation_id:
                    user = self.get_user_info(cancelled_by_user_id)
                    
                    # Check permissions
                    if (user.get('userType') == 'student' and 
                        reservation['userID'] != cancelled_by_user_id):
                        return {
                            'success': False,
                            'error': 'Students can only cancel their own reservations'
                        }
                    
                    # Create blockchain transaction for cancellation
                    tx = Transaction(
                        "CANCEL_RESERVATION",
                        {
                            'reservation_id': reservation_id,
                            'original_user_id': reservation['userID'],
                            'cancelled_by': cancelled_by_user_id,
                            'room_number': reservation['roomNumber'],
                            'block': reservation['block']
                        },
                        cancelled_by_user_id
                    )
                    
                    # Add to blockchain
                    self.blockchain.add_transaction(tx)
                    
                    # Update local state
                    reservation['status'] = 'cancelled'
                    reservation['cancelledBy'] = cancelled_by_user_id
                    
                    # Save state after adding transaction
                    self._save_blockchain_state()
                    
                    # Mine block if we have enough transactions
                    if len(self.blockchain.pending_transactions) >= 3:
                        self._mine_block()
                    
                    return {
                        'success': True,
                        'transaction_id': tx.tx_id,
                        'message': f'Reservation {reservation_id} cancelled successfully'
                    }
            
            return {
                'success': False,
                'error': f'Reservation {reservation_id} not found'
            }
        except Exception as e:
            logger.error(f"Error cancelling reservation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_all_reservations(self) -> Dict:
        """Get all reservations"""
        try:
            return {
                'success': True,
                'data': self.reservations
            }
        except Exception as e:
            logger.error(f"Error getting all reservations: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_reservations_by_user(self, user_id: str) -> Dict:
        """Get all reservations for a specific user"""
        try:
            user_reservations = [r for r in self.reservations if r['userID'] == user_id]
            return {
                'success': True,
                'data': user_reservations
            }
        except Exception as e:
            logger.error(f"Error getting user reservations: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_available_rooms(self, start_time: str, end_time: str) -> Dict:
        """Get available rooms for a specific time period"""
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
            
            available_rooms = []
            
            for room in self.rooms:
                is_available = True
                
                for reservation in self.reservations:
                    if (reservation['roomNumber'] == room['number'] and 
                        reservation['block'] == room['block'] and 
                        reservation['status'] == 'active'):
                        
                        res_start = datetime.fromisoformat(reservation['startTime'])
                        res_end = datetime.fromisoformat(reservation['endTime'])
                        
                        if start_dt < res_end and end_dt > res_start:
                            is_available = False
                            break
                
                if is_available:
                    available_rooms.append(room)
            
            return {
                'success': True,
                'data': available_rooms
            }
        except Exception as e:
            logger.error(f"Error getting available rooms: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_network_info(self) -> Dict:
        """Get information about connected peers"""
        try:
            import time
            current_time = time.time()
            
            peer_info = [
                {
                    "name": "peer0.block33.university.com", 
                    "block": "33", 
                    "status": "connected",
                    "rooms": 15,
                    "active_reservations": len([r for r in self.reservations if r['block'] == '33' and r['status'] == 'active']),
                    "last_seen": current_time
                },
                {
                    "name": "peer0.block34.university.com", 
                    "block": "34", 
                    "status": "connected",
                    "rooms": 15,
                    "active_reservations": len([r for r in self.reservations if r['block'] == '34' and r['status'] == 'active']),
                    "last_seen": current_time
                },
                {
                    "name": "peer0.block35.university.com", 
                    "block": "35", 
                    "status": "connected",
                    "rooms": 15,
                    "active_reservations": len([r for r in self.reservations if r['block'] == '35' and r['status'] == 'active']),
                    "last_seen": current_time
                }
            ]
            
            return {
                'success': True,
                'peers': peer_info,
                'channel': 'universitychannel',
                'chaincode': 'room-reservation',
                'total_peers': len(peer_info),
                'total_rooms': 45,
                'total_reservations': len([r for r in self.reservations if r['status'] == 'active']),
                'connected_users': len(self.users)
            }
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Utility functions for data formatting
class ReservationUtils:
    @staticmethod
    def format_time_for_blockchain(dt: datetime) -> str:
        """Format datetime for blockchain storage"""
        return dt.strftime("%Y-%m-%d %H:%M")
    
    @staticmethod
    def parse_time_from_blockchain(time_str: str) -> datetime:
        """Parse datetime from blockchain format"""
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    
    @staticmethod
    def get_duration_options() -> List[Dict]:
        """Get available duration options"""
        return [
            {"value": 60, "label": "1 hour"},
            {"value": 90, "label": "1.5 hours"},
            {"value": 120, "label": "2 hours"}
        ]
    
    @staticmethod
    def validate_reservation_time(start_time: datetime, duration: int) -> Dict:
        """Validate reservation time constraints"""
        end_time = start_time + timedelta(minutes=duration)
        
        # Check if within allowed hours (06:00 to 23:00)
        if start_time.hour < 6 or start_time.hour >= 23 or end_time.hour > 23:
            return {
                'valid': False,
                'error': 'Reservations are only allowed between 06:00 and 23:00'
            }
        
        # Check if duration is valid
        if duration not in [60, 90, 120]:
            return {
                'valid': False,
                'error': 'Duration must be 1, 1.5, or 2 hours'
            }
        
        return {'valid': True}
    
    @staticmethod
    def generate_room_list() -> List[Dict]:
        """Generate list of all available rooms"""
        rooms = []
        blocks = ["33", "34", "35"]
        floors = ["1", "2", "3"]
        room_numbers = ["00", "01", "02", "03", "04"]
        
        for block in blocks:
            for floor in floors:
                for room_num in room_numbers:
                    rooms.append({
                        "block": block,
                        "floor": floor,
                        "number": floor + room_num,
                        "full_name": f"Block {block} - Room {floor}{room_num}"
                    })
        
        return rooms
