#!/usr/bin/env python3
"""
System Reset Script
Cleans up users without passwords and resets the blockchain
"""

import os
import pickle
import requests
import sys

def manual_reset():
    """Manually reset system files"""
    files_to_remove = [
        'user_sessions.pkl',
        'registered_users.pkl'
    ]
    
    removed_files = []
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            removed_files.append(file_path)
            print(f"✅ Removed: {file_path}")
        else:
            print(f"ℹ️  File not found: {file_path}")
    
    print(f"\n🎉 Manual reset complete! Removed {len(removed_files)} files.")
    print("📝 All users and sessions have been cleared.")
    print("🔄 Restart your Flask app to start fresh.")

def api_reset():
    """Reset system via API (if app is running)"""
    try:
        response = requests.post('http://localhost:5000/api/reset-system')
        data = response.json()
        
        if data['success']:
            print("✅ API Reset Successful!")
            print(f"📊 Removed {len(data['removed_users'])} users without passwords")
            print(f"👥 {data['remaining_users']} valid users remain")
            print(f"🔗 Blockchain reset: {data['reset_blockchain']}")
            
            if data['removed_users']:
                print("\n🗑️  Removed users:")
                for user in data['removed_users']:
                    print(f"   • {user}")
        else:
            print(f"❌ API Reset failed: {data['error']}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ API Reset error: {e}")
        return False
    
    return True

def main():
    print("🔧 University Room Reservation System - Reset Tool")
    print("=" * 50)
    
    # Check if Flask app is running
    try:
        response = requests.get('http://localhost:5000/api/admin-panel', timeout=2)
        app_running = response.status_code == 200
    except:
        app_running = False
    
    if app_running:
        print("🟢 Flask app is running - using API reset")
        
        # Get current stats
        try:
            response = requests.get('http://localhost:5000/api/admin-panel')
            data = response.json()
            
            if data['success']:
                stats = data['stats']
                print(f"\n📊 Current System Status:")
                print(f"   • Total users: {stats['total_registered_users']}")
                print(f"   • Users without passwords: {stats['users_without_passwords']}")
                print(f"   • Valid users: {stats['valid_users']}")
                print(f"   • Blockchain blocks: {stats['blockchain_blocks']}")
                
                if stats['users_without_passwords'] > 0:
                    print(f"\n⚠️  Found {stats['users_without_passwords']} users without passwords")
                    confirm = input("🤔 Do you want to clean them up? (y/N): ")
                    
                    if confirm.lower() == 'y':
                        success = api_reset()
                        if success:
                            print("\n✅ System cleaned successfully!")
                        else:
                            print("\n❌ API reset failed, trying manual reset...")
                            manual_reset()
                    else:
                        print("ℹ️  Reset cancelled.")
                else:
                    print("\n✅ No cleanup needed - all users have passwords!")
            
        except Exception as e:
            print(f"Error getting admin panel data: {e}")
            manual_reset()
    
    else:
        print("🔴 Flask app not running - using manual reset")
        print("📁 This will delete all user data files")
        
        confirm = input("🤔 Continue with manual reset? (y/N): ")
        if confirm.lower() == 'y':
            manual_reset()
        else:
            print("ℹ️  Reset cancelled.")
    
    print("\n🎯 Next Steps:")
    print("1. Restart your Flask app: cd client && python app.py")
    print("2. Go to: http://localhost:5000")
    print("3. Register with new secure credentials (User ID + Password)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Reset interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        sys.exit(1)
