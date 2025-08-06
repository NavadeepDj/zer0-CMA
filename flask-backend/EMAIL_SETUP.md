# 📧 Email Setup Guide for Zer0 Customer Support

## 🎯 **What This Does:**

Your custom Flask system now:
1. **Collects support requests** via simple form or chatbot
2. **Sends email to admin/support team** with ticket details
3. **Sends confirmation email to customer** with ticket ID
4. **Stores tickets** for tracking and follow-up

## 🔧 **Email Configuration Setup:**

### **Step 1: Gmail App Password (Recommended)**

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password:**
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Copy the 16-character password

### **Step 2: Update Email Settings**

Edit `flask-backend/app.py` and replace these values:

```python
# Replace these with your actual email settings
sender_email = "your-email@gmail.com"        # Your Gmail address
sender_password = "your-app-password"        # Your 16-character app password
SUPPORT_EMAIL = "support@zer0company.com"    # Where tickets should be sent
```

### **Step 3: Alternative Email Providers**

#### **For Outlook/Hotmail:**
```python
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587
```

#### **For Yahoo:**
```python
smtp_server = "smtp.mail.yahoo.com"
smtp_port = 587
```

#### **For Custom Domain:**
```python
smtp_server = "mail.yourdomain.com"  # Check with your hosting provider
smtp_port = 587  # or 465 for SSL
```

## 🧪 **Testing the System:**

### **1. Start the Server:**
```bash
cd flask-backend
python app.py
```

### **2. Test Simple Form:**
```bash
# Open in browser:
http://172.28.0.217:5000/form

# Fill out the form and submit
# Check both admin and customer emails
```

### **3. Test Chatbot Integration:**
```bash
# Open in browser:
http://172.28.0.217:5000

# Go through complaint flow
# Check emails after ticket creation
```

## 📧 **Email Templates:**

### **Admin Notification Email:**
- **To:** support@zer0company.com
- **Subject:** 🎫 New Support Ticket - ZER0-2025-001
- **Content:** Customer details, issue description, SLA reminder

### **Customer Confirmation Email:**
- **To:** customer@email.com
- **Subject:** ✅ Your Support Request Received - Ticket ZER0-2025-001
- **Content:** Ticket details, next steps, contact information

## 🔒 **Security Best Practices:**

### **1. Environment Variables (Recommended):**

Create `.env` file:
```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SUPPORT_EMAIL=support@zer0company.com
```

Update `app.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')
```

### **2. Never Commit Passwords:**
Add to `.gitignore`:
```
.env
*.log
__pycache__/
```

## 🎨 **Customization Options:**

### **1. Email Templates:**
- Modify HTML in `send_admin_notification()` and `send_customer_confirmation()`
- Add your company logo and branding
- Customize colors and styling

### **2. Ticket ID Format:**
```python
# Current: ZER0-2025-001
# Custom options:
ticket_id = f"SUPPORT-{datetime.now().strftime('%Y%m%d')}-{len(tickets) + 1:03d}"
ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
```

### **3. Priority Assignment:**
```python
# Add priority logic based on keywords
priority = "high" if any(word in description.lower() for word in ['urgent', 'critical', 'down']) else "medium"
```

## 📊 **Features Included:**

### **✅ Current Features:**
- Simple form interface
- Chatbot integration
- Email notifications (admin + customer)
- Ticket ID generation
- Basic ticket storage
- Professional email templates

### **🔄 Future Enhancements:**
- Database storage (Firebase/PostgreSQL)
- Email templates customization
- Attachment support
- SMS notifications
- Admin dashboard
- Ticket status updates

## 🚀 **Deployment Options:**

### **1. Local Development:**
```bash
python app.py
# Access: http://172.28.0.217:5000
```

### **2. Production Deployment:**
- **Heroku:** Easy deployment with email support
- **DigitalOcean:** VPS with full control
- **AWS/GCP:** Scalable cloud deployment
- **Local Server:** Run on your own hardware

## 🆘 **Troubleshooting:**

### **Email Not Sending:**
1. Check Gmail app password is correct
2. Verify 2FA is enabled
3. Check firewall/antivirus blocking SMTP
4. Try different SMTP port (465 for SSL)

### **Form Not Submitting:**
1. Check browser console for errors
2. Verify Flask server is running
3. Check network connectivity
4. Test API endpoint directly

### **Emails Going to Spam:**
1. Add sender to contacts
2. Check SPF/DKIM records for custom domains
3. Use professional email address
4. Avoid spam trigger words

## 💡 **Pro Tips:**

1. **Test with Different Email Providers:** Gmail, Outlook, Yahoo
2. **Monitor Email Delivery:** Check spam folders initially
3. **Backup Email Settings:** Keep credentials secure
4. **Log Email Status:** Monitor success/failure rates
5. **Rate Limiting:** Prevent email spam/abuse

Your custom support system is now ready with full email integration! 🎉