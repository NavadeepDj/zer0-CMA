#!/usr/bin/env python3
"""
Check email configuration before running the server
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_email_config():
    """Check if email configuration is working"""
    print("🔍 Checking Email Configuration...")
    print("=" * 40)
    
    # Email settings (same as in app.py)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "99220040115@klu.ac.in"
    sender_password = "yogs yflr nddc fibj"  # You need to update this!
    test_recipient = "navadeepmarella@gmail.com"
    
    print(f"📧 Sender: {sender_email}")
    print(f"📧 Recipient: {test_recipient}")
    print(f"🌐 SMTP Server: {smtp_server}:{smtp_port}")
    
    # Check if password is still placeholder
    if sender_password == "your-app-password-here":
        print("\n❌ ERROR: Email password not configured!")
        print("💡 You need to:")
        print("   1. Generate app password for dohaloj488@foboxs.com")
        print("   2. Update the password in app.py")
        print("   3. See EMAIL_CONFIG_GUIDE.md for details")
        return False
    
    # Test SMTP connection
    try:
        print("\n🔌 Testing SMTP connection...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("✅ TLS connection established")
            
            server.login(sender_email, sender_password)
            print("✅ Login successful")
            
            # Send test email
            print("📤 Sending test email...")
            
            msg = MIMEMultipart()
            msg['Subject'] = "🧪 Zer0 Support System - Email Test"
            msg['From'] = sender_email
            msg['To'] = test_recipient
            
            body = """
            <h2>✅ Email Configuration Test Successful!</h2>
            <p>This is a test email from your Zer0 Customer Support system.</p>
            <p><strong>Configuration Details:</strong></p>
            <ul>
                <li>Sender: dohaloj488@foboxs.com</li>
                <li>SMTP Server: smtp.gmail.com:587</li>
                <li>Status: Working correctly!</li>
            </ul>
            <p>Your email system is ready to send support notifications! 🎉</p>
            """
            
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            server.send_message(msg)
            print("✅ Test email sent successfully!")
            
        print("\n🎉 Email configuration is working correctly!")
        print(f"📬 Check {test_recipient} for the test email")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ SMTP Authentication Failed!")
        print("💡 Possible issues:")
        print("   1. Wrong app password")
        print("   2. 2FA not enabled on dohaloj488@foboxs.com")
        print("   3. App password not generated")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP Error: {e}")
        print("💡 Check your internet connection and SMTP settings")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Zer0 Customer Support - Email Configuration Checker")
    print("=" * 60)
    
    if check_email_config():
        print("\n✅ All good! Your email system is ready.")
        print("🚀 You can now run: python app.py")
    else:
        print("\n❌ Email configuration needs fixing.")
        print("📖 Check EMAIL_CONFIG_GUIDE.md for help")

if __name__ == "__main__":
    main()