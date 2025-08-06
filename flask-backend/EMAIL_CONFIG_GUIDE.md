# 📧 Email Configuration Guide for Zer0 Support System

## 🎯 **Current Setup:**

- **Sender Email**: `dohaloj488@foboxs.com` (sends emails)
- **Support Email**: `navadeepmarella@gmail.com` (receives tickets)
- **Email Flow**: User submits → Admin gets ticket → User gets confirmation

## 🔧 **What You Need to Do:**

### **Step 1: Get App Password for dohaloj488@foboxs.com**

Since `dohaloj488@foboxs.com` appears to be a Gmail account, you need to:

1. **Log into dohaloj488@foboxs.com**
2. **Enable 2-Factor Authentication** (if not already enabled)
3. **Generate App Password:**
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### **Step 2: Update the Password in Code**

Edit `flask-backend/app.py` line 25:

```python
# Change this line:
app.config['MAIL_PASSWORD'] = 'your-app-password-here'

# To your actual app password:
app.config['MAIL_PASSWORD'] = 'abcd efgh ijkl mnop'  # Your 16-char app password
```

### **Step 3: Test the Email System**

```bash
cd flask-backend
python test_email.py
```

## 🧪 **Quick Test:**

### **1. Start Server:**
```bash
python app.py
```

### **2. Submit Test Ticket:**
```bash
# Go to: http://172.28.0.217:5000/form
# Fill out form with your email
# Submit and check both emails
```

### **3. Expected Results:**

#### **Admin Email (navadeepmarella@gmail.com):**
```
Subject: 🎫 New Support Ticket - ZER0-2025-001
From: dohaloj488@foboxs.com

[Professional ticket details with customer info]
```

#### **Customer Confirmation Email:**
```
Subject: ✅ Your Support Request Received - Ticket ZER0-2025-001
From: dohaloj488@foboxs.com
To: [customer email]

[Branded confirmation with ticket details]
```

## 🔒 **Security Best Practices:**

### **Option 1: Environment Variables (Recommended)**

Create `.env` file:
```bash
MAIL_USERNAME=dohaloj488@foboxs.com
MAIL_PASSWORD=your-16-char-app-password
SUPPORT_EMAIL=navadeepmarella@gmail.com
```

Update `app.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')
```

### **Option 2: Direct Configuration (Quick Setup)**

Just update the password in `app.py`:
```python
app.config['MAIL_PASSWORD'] = 'your-actual-app-password'
```

## 🚨 **Troubleshooting:**

### **Email Not Sending:**

1. **Check App Password:**
   - Make sure it's the 16-character app password, not your regular password
   - No spaces in the password

2. **Check Gmail Settings:**
   - 2FA must be enabled
   - App password must be generated for "Mail"

3. **Check Network:**
   - Firewall might block SMTP port 587
   - Try port 465 with SSL if needed

4. **Check Email Address:**
   - Verify `dohaloj488@foboxs.com` is correct
   - Make sure it's a Gmail account

### **Emails Going to Spam:**

1. **Add to Contacts:**
   - Add `dohaloj488@foboxs.com` to contacts
   - Check spam folder initially

2. **Email Content:**
   - Professional subject lines
   - Proper HTML formatting
   - No spam trigger words

## 🎨 **Customization:**

### **Change Sender Name:**
```python
msg['From'] = f"Zer0 Support <{sender_email}>"
```

### **Add Reply-To:**
```python
msg['Reply-To'] = SUPPORT_EMAIL
```

### **Custom Email Templates:**
Edit the HTML in `send_admin_notification()` and `send_customer_confirmation()` functions.

## 📊 **Email Flow:**

```
1. User submits support request
   ↓
2. System creates ticket (ZER0-2025-001)
   ↓
3. Admin email sent to: navadeepmarella@gmail.com
   ↓
4. Customer confirmation sent to: [user's email]
   ↓
5. Both emails sent from: dohaloj488@foboxs.com
```

## ✅ **Final Checklist:**

- [ ] App password generated for dohaloj488@foboxs.com
- [ ] Password updated in app.py
- [ ] Test email sent successfully
- [ ] Admin receives ticket notifications
- [ ] Customers receive confirmations
- [ ] Emails not going to spam

**Once you update the app password, your email system will be fully functional! 🚀**