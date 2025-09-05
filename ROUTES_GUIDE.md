# 🗺️ **Complete Routes Guide - University Room Reservation System**

## 📍 **All Available Routes**

### **🏠 Main Application Routes**

| Route         | Access Level        | Description               | Features                                                              |
| ------------- | ------------------- | ------------------------- | --------------------------------------------------------------------- |
| `/`           | **Public**          | Login & Registration Page | Role selection, user registration                                     |
| `/student`    | **Students Only**   | Student Dashboard         | Make reservations, view calendar, check availability                  |
| `/professor`  | **Professors Only** | Professor Dashboard       | All student features + cancel any reservation + view all reservations |
| `/navigation` | **Public**          | Navigation Hub            | Quick access to all routes with role-based links                      |

### **📊 Monitoring & Analytics Routes**

| Route            | Access Level | Description              | Features                                             |
| ---------------- | ------------ | ------------------------ | ---------------------------------------------------- |
| `/monitor`       | **Public**   | System Monitor Dashboard | Live network status, connected users, real-time logs |
| `/blockchain`    | **Public**   | Blockchain Explorer      | View actual blockchain blocks, transactions, mining  |
| `/access-denied` | **System**   | Access Denied Page       | Shows when unauthorized role access attempted        |

### **🔌 API Endpoints**

#### **Authentication & User Management**

| Endpoint                   | Method | Description               | Response                                       |
| -------------------------- | ------ | ------------------------- | ---------------------------------------------- |
| `/api/login`               | POST   | User login & registration | Session creation, blockchain user registration |
| `/api/logout`              | GET    | User logout               | Session cleanup, redirect to home              |
| `/api/user-info/<user_id>` | GET    | Get user information      | User details, session info, debugging data     |

#### **Room & Reservation Management**

| Endpoint                 | Method | Description                    | Response                         |
| ------------------------ | ------ | ------------------------------ | -------------------------------- |
| `/api/rooms`             | GET    | Get all available rooms        | List of 45 rooms across 3 blocks |
| `/api/reservations`      | GET    | Get reservations (all/by user) | Reservation list with filters    |
| `/api/reservations`      | POST   | Make new reservation           | Creates blockchain transaction   |
| `/api/reservations/<id>` | DELETE | Cancel reservation             | Role-based cancellation          |
| `/api/available-rooms`   | GET    | Check room availability        | Available rooms for time period  |

#### **System & Blockchain**

| Endpoint                | Method | Description                     | Response                            |
| ----------------------- | ------ | ------------------------------- | ----------------------------------- |
| `/api/network-info`     | GET    | Get network status              | Peer information, connection status |
| `/api/system-status`    | GET    | Get comprehensive system status | Network, users, activity, uptime    |
| `/api/blockchain-data`  | GET    | Get complete blockchain data    | Blocks, transactions, mining stats  |
| `/api/mine-block`       | POST   | Manually trigger block mining   | Mine pending transactions           |
| `/api/duration-options` | GET    | Get valid duration options      | 1h, 1.5h, 2h options                |

---

## 🔐 **Role-Based Access Control**

### **Student Access:**

✅ **Allowed:**

- `/` - Login page
- `/student` - Student dashboard
- `/monitor` - System monitoring
- `/blockchain` - Blockchain explorer
- `/navigation` - Navigation hub
- All API endpoints (with student permissions)

❌ **Restricted:**

- `/professor` - Redirected to access denied page

### **Professor Access:**

✅ **Allowed:**

- All student routes PLUS:
- `/professor` - Professor dashboard with admin features
- Enhanced API permissions (cancel any reservation)

### **Public Access:**

✅ **Available to Everyone:**

- `/` - Login/registration
- `/monitor` - System monitoring
- `/blockchain` - Blockchain explorer
- `/navigation` - Navigation hub
- `/access-denied` - Error page

---

## 🧭 **Navigation Features**

### **Smart Navigation Bars:**

- **Student Navbar:** Shows student-appropriate links only
- **Professor Navbar:** Shows all available links with professor badge
- **Monitor/Blockchain:** Shows general navigation with role detection

### **Role-Based Link Display:**

- **Students:** See warning that professor dashboard is restricted
- **Professors:** Can access both student and professor dashboards
- **Not Logged In:** Prompted to login first

### **Quick Access Features:**

- **Navigation Page** (`/navigation`): Central hub with all routes
- **Role Detection:** JavaScript checks session and shows appropriate links
- **Access Control:** Server-side validation prevents unauthorized access
- **Error Handling:** Graceful redirection to access denied page

---

## 🎯 **Professional Demo Navigation**

### **For Classroom Demonstration:**

1. **Start with Navigation Hub:**

   ```
   http://localhost:5000/navigation
   ```

2. **Show Role-Based Access:**

   - Login as student → Try to access `/professor` → Access denied
   - Login as professor → Can access both dashboards

3. **Demonstrate All Routes:**

   - **Main App:** Reservation functionality
   - **Monitor:** Live system status
   - **Blockchain:** Actual blockchain visualization
   - **API:** Direct data access

4. **Highlight Security:**
   - Role-based restrictions work properly
   - Unauthorized access is prevented
   - Professional error handling

---

## 🔗 **Quick Links for Testing**

### **For YOU (Host):**

```
Main App: http://localhost:5000
Navigation: http://localhost:5000/navigation
Monitor: http://localhost:5000/monitor
Blockchain: http://localhost:5000/blockchain
```

### **For Classmates:**

```
Main App: http://[YOUR_IP]:5000
Navigation: http://[YOUR_IP]:5000/navigation
Monitor: http://[YOUR_IP]:5000/monitor
Blockchain: http://[YOUR_IP]:5000/blockchain
```

### **Test Credentials:**

```
Professor: prof-test | Professor Test | prof@uni.edu | Block 33
Student: student-test | Student Test | student@uni.edu | Block 33
```

---

## ✅ **Security Features Implemented**

1. **✅ Role-Based Route Protection:** Students cannot access professor dashboard
2. **✅ Session Validation:** Must be logged in to access dashboards
3. **✅ Graceful Access Denial:** Professional error page for unauthorized access
4. **✅ Smart Navigation:** Links shown based on user role
5. **✅ Server-Side Validation:** Backend enforces access control
6. **✅ Professional Error Handling:** Clear messaging for access issues

**Your system now has enterprise-grade role-based access control!** 🔐
