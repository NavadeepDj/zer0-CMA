# 🚀 Quick Setup Instructions for Zer0 Support System

## 📧 **Your Email Configuration:**

- **Sender Email**: `dohaloj488@foboxs.com` (sends all emails)
- **Support Email**: `navadeepmarella@gmail.com` (receives tickets)
- **Current Status**: ⚠️ **Needs app password setup**

## 🔧 **What You Need to Do (5 minutes):**

### **Step 1: Get App Password**

1. **Log into dohaloj488@foboxs.com**
2. **Go to Google Account Settings** → Security
3. **Enable 2-Factor Authentication** (if not already enabled)
4. **Generate App Password:**
   - Click "App passwords"
   - Select "Mail" 
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### **Step 2: Update the Code**

Edit `flask-backend/app.py` line 25:

```python
# Change this:
app.config['MAIL_PASSWORD'] = 'your-app-password-here'

# To your actual app password:
app.config['MAIL_PASSWORD'] = 'abcd efgh ijkl mnop'  # Your real password
```

### **Step 3: Test It**

```bash
# Test email configuration
python check_email_config.py

# If successful, start the server
python app.py

# Test the complete system
python test_your_email.py
```

## 🎯 **Expected Results:**

### **When someone submits a support request:**

1. **Admin Email** → `navadeepmarella@gmail.com`
   ```
   Subject: 🎫 New Support Ticket - ZER0-2025-001
   From: dohaloj488@foboxs.com
   
   [Professional ticket details with customer info]
   ```

2. **Customer Confirmation** → `[customer's email]`
   ```
   Subject: ✅ Your Support Request Received - Ticket ZER0-2025-001
   From: dohaloj488@foboxs.com
   
   [Branded confirmation with ticket details and next steps]
   ```

## 🧪 **Test Interfaces:**

### **1. Simple Form:**
```
http://172.28.0.217:5000/form
```
- Clean, professional form
- Instant email notifications
- Perfect for embedding in websites

### **2. Prashna Chatbot:**
```
http://172.28.0.217:5000
```
- Intelligent conversation
- Guided ticket creation
- Full Zer0 knowledge base

## 🔍 **Troubleshooting:**

### **If emails don't work:**

1. **Check the password:**
   ```bash
   python check_email_config.py
   ```

2. **Check server logs:**
   - Look for error messages in the console
   - Check for authentication failures

3. **Check spam folders:**
   - Both admin and customer emails might go to spam initially

4. **Verify email addresses:**
   - Make sure `dohaloj488@foboxs.com` is correct
   - Confirm `navadeepmarella@gmail.com` is right

## 📊 **System Flow:**

```
User submits request
        ↓
Prashna creates ticket (ZER0-2025-001)
        ↓
Email 1: Admin notification → navadeepmarella@gmail.com
        ↓
Email 2: Customer confirmation → user's email
        ↓
Both emails sent from: dohaloj488@foboxs.com
```

## ✅ **Quick Checklist:**

- [ ] App password generated for `dohaloj488@foboxs.com`
- [ ] Password updated in `app.py` line 25
- [ ] Email test passes: `python check_email_config.py`
- [ ] Server starts: `python app.py`
- [ ] System test passes: `python test_your_email.py`
- [ ] Both interfaces work: `/form` and `/` (chatbot)

## 🎉 **Once Working:**

Your system will:
- ✅ **Collect support requests** via form or chatbot
- ✅ **Send professional emails** to admin team
- ✅ **Confirm with customers** automatically
- ✅ **Track tickets** with unique IDs
- ✅ **Provide excellent UX** with Prashna's personality

**Total setup time: ~5 minutes after getting the app password! 🚀**