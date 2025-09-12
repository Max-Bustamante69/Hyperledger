# 🚀 **How to Run the Blockchain Room Reservation System**

## 📋 **Quick Start Guide (5 Minutes)**

### **For You (Project Owner):**

```bash
# 1. Navigate to project directory
cd "C:\Users\Usuario\Desktop\P\Github\Eafit\Blockchain\Hyperledger"

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start the blockchain system
cd client
python app.py

# 4. Open your browser
# Go to: http://localhost:5000
```

### **For Other People (Students/Colleagues):**

```bash
# 1. Clone or download the project
# 2. Navigate to project directory
cd path/to/Hyperledger

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start the system
cd client
python app.py

# 5. Open browser
# Go to: http://localhost:5000
```

---

## 🎯 **Step-by-Step Instructions**

### **Step 1: Prerequisites**

- **Python 3.8+** installed
- **pip** package manager
- **Web browser** (Chrome, Firefox, Edge)

### **Step 2: Install Dependencies**

```bash
# Install all required Python packages
pip install -r requirements.txt
```

**Required packages:**

- Flask (web framework)
- Flask-SocketIO (real-time communication)
- python-socketio (WebSocket support)
- requests (HTTP client)
- python-dateutil (date handling)

### **Step 3: Start the System**

```bash
# Navigate to client directory
cd client

# Start the Flask application
python app.py
```

**Expected output:**

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
```

### **Step 4: Access the System**

1. **Open your web browser**
2. **Go to:** `http://localhost:5000`
3. **You should see:** Login/Registration page

---

## 👥 **For Multiple Users (Network Testing)**

### **Scenario: Testing with Friends/Colleagues**

#### **Option 1: Same Computer (Different Browser Tabs)**

```bash
# Start the system once
cd client
python app.py

# Open multiple browser tabs:
# Tab 1: http://localhost:5000 (User A)
# Tab 2: http://localhost:5000 (User B)
# Tab 3: http://localhost:5000 (User C)
```

#### **Option 2: Different Computers (Network)**

```bash
# On your computer (Server):
cd client
python app.py
# Note your IP address (e.g., 192.168.1.100)

# On other computers:
# Go to: http://192.168.1.100:5000
# (Replace with your actual IP address)
```

**To find your IP address:**

```bash
# Windows:
ipconfig

# Look for: IPv4 Address (e.g., 192.168.1.100)
```

---

## 🧪 **Testing the Blockchain Behavior**

### **Test 1: Basic Registration & Login**

```bash
# 1. Go to http://localhost:5000
# 2. Register a new user:
#    - User ID: student-001
#    - Name: John Student
#    - Password: password123
#    - Role: Student
# 3. Click "Login/Register"
# 4. Should see: Student Dashboard
```

### **Test 2: Make a Reservation**

```bash
# 1. On Student Dashboard
# 2. Select:
#    - Room: 101
#    - Block: 33
#    - Date: Today
#    - Time: 10:00 AM
#    - Duration: 1 hour
# 3. Click "Make Reservation"
# 4. Should see: "PENDING" status (yellow/cyan color)
```

### **Test 3: Realistic Blockchain Behavior**

```bash
# 1. Make first reservation → Shows as "PENDING"
# 2. Make second reservation for SAME time → Should be ALLOWED!
# 3. Both show as "PENDING" on calendar
# 4. Make third reservation → Triggers mining (every 3 transactions)
# 5. All reservations become "ACTIVE" (green/blue)
# 6. Try fourth reservation → Should be BLOCKED (realistic conflict)
```

### **Test 4: Professor Override**

```bash
# 1. Register as professor:
#    - User ID: prof-001
#    - Name: Dr. Smith
#    - Role: Professor
# 2. Make reservation for occupied room
# 3. Should succeed (professor override capability)
```

---

## 🔗 **Blockchain Explorer**

### **View the Blockchain:**

```bash
# 1. Go to: http://localhost:5000/blockchain
# 2. See:
#    - All blocks with hash chains
#    - Transaction details
#    - Mining process
#    - Pending transactions
```

### **Mine Blocks Manually:**

```bash
# 1. Go to: http://localhost:5000/blockchain
# 2. Click "Mine Block" button
# 3. Watch proof-of-work mining
# 4. See new block added to chain
```

---

## 📊 **System Monitoring**

### **Network Status:**

```bash
# Go to: http://localhost:5000/monitor
# See:
# - Connected users
# - Active reservations
# - Blockchain statistics
# - System performance
```

---

## 🎓 **For University Presentation**

### **Demo Script:**

```
1. "Let me show you our blockchain room reservation system..."

2. Open: http://localhost:5000
   "This is the login system with secure password authentication"

3. Register as student:
   "Students can make reservations with time and duration limits"

4. Make reservation:
   "Notice it shows as PENDING - this is realistic blockchain behavior"

5. Make another reservation for same time:
   "This is allowed because the first isn't committed yet"

6. Show blockchain explorer: http://localhost:5000/blockchain
   "Here you can see the actual blockchain with proof-of-work mining"

7. Mine a block:
   "Now both reservations become ACTIVE and committed to blockchain"

8. Try to make conflicting reservation:
   "Now it's blocked - this is how real blockchains work!"
```

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **"Module not found" Error:**

```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

#### **"Port 5000 already in use":**

```bash
# Solution: Kill existing process
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or change port in app.py:
app.run(host='0.0.0.0', port=5001, debug=True)
```

#### **"Cannot access from other computers":**

```bash
# Solution: Check firewall settings
# Windows: Allow Python through Windows Firewall
# Or run with specific host:
python app.py --host=0.0.0.0
```

#### **"Docker errors":**

```bash
# Solution: Use simulation mode (already implemented)
# The system works without Docker for testing
# Docker is only needed for full Hyperledger Fabric network
```

---

## 📱 **Mobile Testing**

### **Test on Phone/Tablet:**

```bash
# 1. Find your computer's IP address
# 2. Connect phone to same WiFi network
# 3. Go to: http://YOUR_IP:5000
# 4. Test the responsive interface
```

---

## 🎯 **Key Features to Demonstrate**

### **1. Realistic Blockchain Behavior:**

- Pending vs Active reservations
- Proof-of-work mining
- Transaction conflict resolution

### **2. Role-Based Access:**

- Students: Limited to 2-hour reservations
- Professors: Can override any reservation

### **3. Real-Time Updates:**

- Live calendar updates
- WebSocket communication
- Network status monitoring

### **4. Security Features:**

- Password hashing with salt
- Session management
- Role-based access control

---

## 🏆 **Success Indicators**

### **System Working Correctly:**

✅ **Login page loads** at http://localhost:5000
✅ **Registration works** with password validation
✅ **Reservations show as PENDING** initially
✅ **Multiple pending reservations allowed** for same time
✅ **Mining triggers** every 3 transactions
✅ **Reservations become ACTIVE** after mining
✅ **Conflicts detected** after commitment
✅ **Blockchain explorer** shows blocks and transactions
✅ **Real-time updates** work across multiple users

---

## 📞 **Getting Help**

### **If Something Doesn't Work:**

1. **Check terminal output** for error messages
2. **Verify all dependencies** are installed
3. **Try restarting** the Flask application
4. **Check browser console** for JavaScript errors
5. **Ensure port 5000** is not blocked by firewall

### **For Technical Issues:**

- Check the `README.md` for detailed setup
- Review `BLOCKCHAIN_IMPLEMENTATION_ANALYSIS.md` for technical details
- Look at `BLOCKCHAIN_BEHAVIOR_ANALYSIS.md` for behavior explanations

---

## 🎉 **Ready to Demo!**

**Your blockchain room reservation system is now ready for:**

- ✅ **University presentations**
- ✅ **Multi-user testing**
- ✅ **Blockchain behavior demonstration**
- ✅ **Real-time collaboration**
- ✅ **Professional evaluation**

**Good luck with your presentation!** 🎓⛓️

