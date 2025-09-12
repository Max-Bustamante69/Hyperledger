from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import asyncio
import json
from datetime import datetime, timedelta
import threading
import time
import uuid
import os
import pickle
from pathlib import Path
import hashlib
import secrets

from blockchain_client import BlockchainClient, ReservationUtils

app = Flask(__name__)
app.config['SECRET_KEY'] = 'university-room-reservation-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Sessions last 24 hours
socketio = SocketIO(app, cors_allowed_origins="*")

# Global blockchain client instance
blockchain_client = None

# Store connected users and their rooms
connected_users = {}

# Session persistence file
SESSION_FILE = 'user_sessions.pkl'
USERS_FILE = 'registered_users.pkl'

def load_persistent_data():
    """Load persistent session and user data"""
    users_data = {}
    sessions_data = {}
    
    # Load registered users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'rb') as f:
                users_data = pickle.load(f)
        except Exception as e:
            print(f"Error loading users data: {e}")
    
    # Load sessions
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'rb') as f:
                sessions_data = pickle.load(f)
        except Exception as e:
            print(f"Error loading sessions data: {e}")
    
    return users_data, sessions_data

def save_user_data(users_data):
    """Save user data to persistent storage"""
    try:
        with open(USERS_FILE, 'wb') as f:
            pickle.dump(users_data, f)
    except Exception as e:
        print(f"Error saving users data: {e}")

def save_session_data(sessions_data):
    """Save session data to persistent storage"""
    try:
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(sessions_data, f)
    except Exception as e:
        print(f"Error saving sessions data: {e}")

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify password against stored hash"""
    if len(stored_password) < 64:  # Invalid hash length
        return False
    
    salt = stored_password[:64]
    stored_hash = stored_password[64:]
    
    pwd_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwd_hash.hex() == stored_hash

def get_user_by_id(user_id):
    """Check if user exists by ID only"""
    users_data, _ = load_persistent_data()
    return users_data.get(user_id, None)

def get_user_by_name(name):
    """Check if user exists by name only"""
    users_data, _ = load_persistent_data()
    
    # Check by name (case insensitive)
    for uid, user_info in users_data.items():
        if user_info.get('name', '').lower() == name.lower():
            return user_info
    
    return None

def check_for_duplicates(user_id, name):
    """Check for duplicate ID or name, return specific error"""
    users_data, _ = load_persistent_data()
    
    # Check for duplicate ID
    if user_id in users_data:
        return {'duplicate': True, 'type': 'id', 'existing_user': users_data[user_id]}
    
    # Check for duplicate name
    for uid, user_info in users_data.items():
        if user_info.get('name', '').lower() == name.lower():
            return {'duplicate': True, 'type': 'name', 'existing_user': user_info}
    
    return {'duplicate': False}

def init_blockchain():
    """Initialize blockchain client"""
    global blockchain_client
    blockchain_client = BlockchainClient()
    
    # Load persistent user data
    users_data, _ = load_persistent_data()
    if users_data:
        blockchain_client.users.update(users_data)
        print(f"Loaded {len(users_data)} persistent users")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Initialize with a default admin user
    loop.run_until_complete(blockchain_client.initialize("admin", "professor"))

# Initialize blockchain client in a separate thread
threading.Thread(target=init_blockchain, daemon=True).start()

@app.route('/')
def index():
    """Main page - user selection with session checking"""
    # Check if user is already logged in
    if 'user_id' in session and 'user_type' in session:
        user_type = session['user_type']
        return redirect(url_for(f'{user_type}_dashboard'))
    
    return render_template('index.html')

@app.route('/api/session-status')
def session_status():
    """Get current session status"""
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'logged_in': True,
            'user_id': session['user_id'],
            'user_type': session['user_type'],
            'name': session['name'],
            'block': session['block'],
            'last_login': session.get('last_login'),
            'session_age': time.time() - session.get('last_login', time.time())
        })
    else:
        return jsonify({
            'success': True,
            'logged_in': False
        })

@app.route('/student')
def student_dashboard():
    """Student dashboard - restricted to students only"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    # Check if user is actually a student
    if session.get('user_type') != 'student':
        return redirect(url_for('access_denied', required_role='student'))
    
    return render_template('student.html', user_id=session['user_id'])

@app.route('/professor')
def professor_dashboard():
    """Professor dashboard - restricted to professors only"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    # Check if user is actually a professor
    if session.get('user_type') != 'professor':
        return redirect(url_for('access_denied', required_role='professor'))
    
    return render_template('professor.html', user_id=session['user_id'])

@app.route('/monitor')
def system_monitor():
    """System monitoring dashboard"""
    return render_template('monitor.html')

@app.route('/blockchain')
def blockchain_explorer():
    """Blockchain explorer and visualization"""
    return render_template('blockchain.html')

@app.route('/navigation')
def navigation_page():
    """Navigation page with all routes"""
    return render_template('navigation.html')

@app.route('/access-denied')
def access_denied():
    """Access denied page for unauthorized role access"""
    required_role = request.args.get('required_role', 'unknown')
    current_role = session.get('user_type', 'unknown')
    return render_template('access_denied.html', required_role=required_role, current_role=current_role)

@app.route('/api/blockchain-data')
def get_blockchain_data():
    """Get complete blockchain data for visualization"""
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    try:
        blockchain_data = blockchain_client.get_blockchain_data()
        return jsonify(blockchain_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/blockchain-download')
def download_blockchain_state():
    """Download complete blockchain state as JSON"""
    try:
        if not blockchain_client:
            return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
        
        data = blockchain_client.download_blockchain_state()
        if data['success']:
            # Return the data as a downloadable JSON file
            from flask import Response
            import json
            
            json_data = json.dumps(data['data'], indent=2, default=str)
            filename = f"blockchain_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            return Response(
                json_data,
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-Type': 'application/json'
                }
            )
        else:
            return jsonify(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mine-block', methods=['POST'])
def mine_block():
    """Manually trigger block mining"""
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    try:
        new_block = blockchain_client._mine_block()
        if new_block:
            # Emit real-time update
            socketio.emit('blockchain_update', {
                'type': 'new_block_mined',
                'block': new_block.to_dict()
            })
            
            return jsonify({
                'success': True,
                'message': f'Block #{new_block.index} mined successfully',
                'block': new_block.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No pending transactions to mine'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login with robust session management and password authentication"""
    data = request.get_json()
    user_id = data.get('user_id', '').strip()
    user_type = data.get('user_type')
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    block = data.get('block', '33')
    
    if not user_id or not user_type or not name or not password:
        return jsonify({'success': False, 'error': 'User ID, name, password, and type are required'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters long'})
    
    # Step 1: Check if this is an existing user login attempt (by User ID)
    existing_user_by_id = get_user_by_id(user_id)
    
    if existing_user_by_id:
        # EXISTING USER LOGIN FLOW
        user_info = existing_user_by_id
        
        # Verify password
        stored_password = user_info.get('password_hash', '')
        if not stored_password:
            return jsonify({
                'success': False,
                'error': f'User {user_id} exists but has no password. Please contact system administrator for reset.'
            })
        
        if not verify_password(stored_password, password):
            return jsonify({
                'success': False,
                'error': 'Invalid password. Please check your password and try again.'
            })
        
        # Verify user type matches
        if user_info['userType'] != user_type:
            return jsonify({
                'success': False, 
                'error': f'User {user_id} is registered as {user_info["userType"]}, not {user_type}. Please select the correct role.'
            })
        
        # Successful login - update session
        session.permanent = True
        session['user_id'] = user_info['id']
        session['user_type'] = user_info['userType']
        session['name'] = user_info['name']
        session['email'] = user_info.get('email', email)
        session['block'] = user_info['block']
        session['last_login'] = time.time()
        
        # Update login count
        users_data, sessions_data = load_persistent_data()
        if user_id in sessions_data:
            sessions_data[user_id]['login_count'] = sessions_data[user_id].get('login_count', 0) + 1
            sessions_data[user_id]['last_login'] = time.time()
        else:
            sessions_data[user_id] = {'login_count': 1, 'last_login': time.time()}
        save_session_data(sessions_data)
        
        return jsonify({
            'success': True, 
            'redirect': f'/{user_info["userType"]}',
            'user_type': user_info['userType'],
            'message': f'Welcome back, {user_info["name"]}! Logged in as {user_info["userType"]}',
            'returning_user': True
        })
    
    else:
        # NEW USER REGISTRATION FLOW
        # Note: Names CAN be duplicated, only User IDs must be unique
        
        # Step 2: Create new user (names are allowed to be duplicated)
        # Hash password for secure storage
        password_hash = hash_password(password)
        
        # Store user info in session
        session.permanent = True
        session['user_id'] = user_id
        session['user_type'] = user_type
        session['name'] = name
        session['email'] = email
        session['block'] = block
        session['first_login'] = time.time()
        session['last_login'] = time.time()
        
        # Register user in blockchain
        if blockchain_client:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                blockchain_client.register_user(user_id, name, email, user_type, block)
            )
            
            if not result['success']:
                return jsonify({
                    'success': False,
                    'error': f'Blockchain registration failed: {result["error"]}'
                })
        
        # Save to persistent storage with password hash
        users_data, sessions_data = load_persistent_data()
        users_data[user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'userType': user_type,
            'block': block,
            'password_hash': password_hash,
            'registered_at': time.time()
        }
        
        sessions_data[user_id] = {
            'last_login': time.time(),
            'login_count': 1
        }
        
        save_user_data(users_data)
        save_session_data(sessions_data)
        
        return jsonify({
            'success': True, 
            'redirect': f'/{user_type}',
            'user_type': user_type,
            'message': f'Welcome to the system, {name}! Successfully registered as {user_type}',
            'new_user': True
        })

@app.route('/api/logout')
def logout():
    """Handle user logout"""
    user_id = session.get('user_id')
    if user_id:
        # Update session data
        users_data, sessions_data = load_persistent_data()
        if user_id in sessions_data:
            sessions_data[user_id]['last_logout'] = time.time()
            save_session_data(sessions_data)
    
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/check-user/<user_id>')
def check_user_exists(user_id):
    """Check if user exists and return info"""
    try:
        existing_user = get_user_by_id(user_id)
        
        if existing_user:
            return jsonify({
                'success': True,
                'user_exists': True,
                'user_info': {
                    'id': existing_user['id'],
                    'name': existing_user['name'],
                    'userType': existing_user['userType'],
                    'block': existing_user['block'],
                    'registered_at': existing_user.get('registered_at'),
                    'has_password': 'password_hash' in existing_user
                },
                'message': f'User {user_id} found in system'
            })
        else:
            return jsonify({
                'success': True,
                'user_exists': False,
                'message': f'User {user_id} not found - will create new registration'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-name/<name>')
def check_name_exists(name):
    """Check if name exists and return suggestions"""
    try:
        users_data, _ = load_persistent_data()
        
        # Find users with similar names
        similar_users = []
        name_lower = name.lower()
        
        for uid, user_info in users_data.items():
            user_name = user_info.get('name', '').lower()
            if name_lower in user_name or user_name in name_lower:
                similar_users.append({
                    'id': user_info['id'],
                    'name': user_info['name'],
                    'userType': user_info['userType'],
                    'block': user_info['block']
                })
        
        return jsonify({
            'success': True,
            'similar_users': similar_users,
            'suggestions_count': len(similar_users)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rooms')
def get_rooms():
    """Get all available rooms"""
    rooms = ReservationUtils.generate_room_list()
    return jsonify({'success': True, 'data': rooms})

@app.route('/api/reservations')
def get_reservations():
    """Get reservations (all or by user)"""
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        if user_id:
            result = loop.run_until_complete(
                blockchain_client.get_reservations_by_user(user_id)
            )
        else:
            result = loop.run_until_complete(
                blockchain_client.get_all_reservations()
            )
        
        # Add blockchain status information to reservations
        if result.get('success') and 'data' in result:
            for reservation in result['data']:
                if reservation.get('status') == 'pending':
                    reservation['blockchain_status'] = 'Pending (not yet mined)'
                elif reservation.get('status') == 'active':
                    reservation['blockchain_status'] = 'Committed to blockchain'
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reservations', methods=['POST'])
def make_reservation():
    """Make a new reservation"""
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    data = request.get_json()
    room_number = data.get('room_number')
    block = data.get('block')
    user_id = data.get('user_id')
    start_time_str = data.get('start_time')
    duration = int(data.get('duration', 60))
    
    # Validate input
    if not all([room_number, block, user_id, start_time_str]):
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    try:
        # Make reservation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            blockchain_client.make_reservation(room_number, block, user_id, start_time_str, duration)
        )
        
        # If conflict, provide better error message with suggestions
        if not result['success'] and 'already reserved' in result['error']:
            # Get available rooms for the same time
            from datetime import datetime, timedelta
            start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=duration)
            
            available_result = loop.run_until_complete(
                blockchain_client.get_available_rooms(
                    start_dt.strftime("%Y-%m-%d %H:%M"),
                    end_dt.strftime("%Y-%m-%d %H:%M")
                )
            )
            
            available_rooms = []
            if available_result['success']:
                # Filter rooms in the same block
                available_rooms = [r for r in available_result['data'] if r['block'] == block]
            
            result['suggested_rooms'] = available_rooms[:5]  # Top 5 suggestions
            result['error'] = f"Room {room_number} in Block {block} is already reserved. {len(available_rooms)} alternative rooms available in the same block."
        
        # Emit real-time update if successful
        if result['success']:
            socketio.emit('reservation_update', {
                'type': 'new_reservation',
                'data': {
                    'room_number': room_number,
                    'block': block,
                    'user_id': user_id,
                    'start_time': start_time_str,
                    'duration': duration,
                    'reservation_id': result.get('reservation_id')
                }
            })
            
            # Update network statistics
            network_update = blockchain_client.get_network_info()
            socketio.emit('network_update', network_update)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reservations/<reservation_id>', methods=['DELETE'])
def cancel_reservation(reservation_id):
    """Cancel a reservation"""
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    data = request.get_json()
    cancelled_by_user_id = data.get('cancelled_by_user_id')
    
    if not cancelled_by_user_id:
        return jsonify({'success': False, 'error': 'cancelled_by_user_id is required'})
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            blockchain_client.cancel_reservation(reservation_id, cancelled_by_user_id)
        )
        
        # Emit real-time update if successful
        if result['success']:
            socketio.emit('reservation_update', {
                'type': 'cancelled_reservation',
                'data': {
                    'reservation_id': reservation_id,
                    'cancelled_by': cancelled_by_user_id
                }
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/available-rooms')
def get_available_rooms():
    """Get available rooms for a specific time period"""
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not start_time or not end_time:
        return jsonify({'success': False, 'error': 'start_time and end_time are required'})
    
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            blockchain_client.get_available_rooms(start_time, end_time)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/network-info')
def get_network_info():
    """Get blockchain network information"""
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    try:
        result = blockchain_client.get_network_info()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/duration-options')
def get_duration_options():
    """Get available duration options"""
    options = ReservationUtils.get_duration_options()
    return jsonify({'success': True, 'data': options})

@app.route('/api/user-info/<user_id>')
def get_user_info(user_id):
    """Get user information for debugging"""
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    try:
        # Handle special case for current user
        if user_id == 'current':
            return jsonify({
                'success': True,
                'session_user_id': session.get('user_id'),
                'session_user_type': session.get('user_type'),
                'session_name': session.get('name'),
                'session_block': session.get('block')
            })
        
        user_info = blockchain_client.get_user_info(user_id)
        all_users = list(blockchain_client.users.keys())
        
        return jsonify({
            'success': True,
            'user_info': user_info,
            'all_users': all_users,
            'session_user_id': session.get('user_id'),
            'session_user_type': session.get('user_type')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system-status')
def get_system_status():
    """Get comprehensive system status"""
    if not blockchain_client:
        return jsonify({'success': False, 'error': 'Blockchain client not initialized'})
    
    try:
        # Get network info
        network_info = blockchain_client.get_network_info()
        
        # Get connected users info
        connected_users_info = []
        for sid, user_info in connected_users.items():
            user_details = blockchain_client.users.get(user_info.get('user_id', ''), {})
            connected_users_info.append({
                'session_id': sid[:8] + '...',  # Abbreviated for privacy
                'user_id': user_info.get('user_id', 'Unknown'),
                'user_type': user_details.get('userType', 'Unknown'),
                'block': user_details.get('block', 'Unknown'),
                'room': user_info.get('room', 'general')
            })
        
        # Get recent activity
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        recent_reservations = loop.run_until_complete(
            blockchain_client.get_all_reservations()
        )
        
        # Sort by creation time and get last 5
        if recent_reservations['success']:
            sorted_reservations = sorted(
                recent_reservations['data'], 
                key=lambda x: x.get('createdAt', ''), 
                reverse=True
            )[:5]
        else:
            sorted_reservations = []
        
        return jsonify({
            'success': True,
            'network': network_info,
            'connected_users': connected_users_info,
            'recent_activity': sorted_reservations,
            'system_uptime': time.time(),
            'active_sessions': len(connected_users)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'data': 'Connected to room reservation system'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')
    if request.sid in connected_users:
        del connected_users[request.sid]

@socketio.on('join_room')
def handle_join_room(data):
    """Handle user joining a room for updates"""
    room = data.get('room', 'general')
    user_id = data.get('user_id')
    
    join_room(room)
    connected_users[request.sid] = {
        'user_id': user_id,
        'room': room
    }
    
    emit('joined_room', {'room': room}, room=request.sid)
    
    # Send network info to the user
    if blockchain_client:
        try:
            network_info = blockchain_client.get_network_info()
            emit('network_info', network_info, room=request.sid)
        except Exception as e:
            emit('error', {'message': str(e)}, room=request.sid)

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle user leaving a room"""
    room = data.get('room', 'general')
    leave_room(room)
    
    if request.sid in connected_users:
        connected_users[request.sid]['room'] = None

@socketio.on('request_reservations')
def handle_request_reservations(data):
    """Handle real-time reservation data request"""
    if not blockchain_client:
        emit('error', {'message': 'Blockchain client not initialized'}, room=request.sid)
        return
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            blockchain_client.get_all_reservations()
        )
        
        emit('reservations_data', result, room=request.sid)
        
    except Exception as e:
        emit('error', {'message': str(e)}, room=request.sid)

# Background task to periodically update clients
def background_task():
    """Background task to send periodic updates"""
    while True:
        time.sleep(30)  # Update every 30 seconds
        if blockchain_client:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get current reservations
                result = loop.run_until_complete(
                    blockchain_client.get_all_reservations()
                )
                
                if result['success']:
                    socketio.emit('periodic_update', {
                        'type': 'reservations',
                        'data': result['data'],
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"Background task error: {e}")

@app.route('/api/reset-system', methods=['POST'])
def reset_system():
    """Reset system data - removes users without passwords and cleans up"""
    try:
        # Load current data
        users_data, sessions_data = load_persistent_data()
        
        # Count users without passwords
        users_without_passwords = []
        valid_users = {}
        
        for user_id, user_info in users_data.items():
            if 'password_hash' not in user_info or not user_info['password_hash']:
                users_without_passwords.append(user_id)
            else:
                valid_users[user_id] = user_info
        
        # Reset blockchain client data
        if blockchain_client:
            blockchain_client.users.clear()
            blockchain_client.reservations.clear()
            # Reset blockchain by creating new instance
            from blockchain_client import Blockchain
            blockchain_client.blockchain = Blockchain()
            
            # Re-add valid users to blockchain
            for user_id, user_info in valid_users.items():
                blockchain_client.users[user_id] = user_info
        
        # Save cleaned data
        save_user_data(valid_users)
        
        # Clean sessions for removed users
        cleaned_sessions = {uid: data for uid, data in sessions_data.items() if uid in valid_users}
        save_session_data(cleaned_sessions)
        
        return jsonify({
            'success': True,
            'message': f'System reset complete. Removed {len(users_without_passwords)} users without passwords.',
            'removed_users': users_without_passwords,
            'remaining_users': len(valid_users),
            'reset_blockchain': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Start background task
threading.Thread(target=background_task, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
