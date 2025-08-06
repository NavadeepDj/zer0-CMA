# JotForm + Prashna Integration Guide

## 🎯 **Hybrid Architecture**

### **Level 1: JotForm AI (Basic Support)**
- Simple FAQ responses
- Basic information queries
- Quick answers for common questions
- Lightweight, fast responses

### **Level 2: Prashna AI (Advanced Support)**
- Complex complaint handling
- Multi-step ticket creation
- AI-powered categorization
- Intelligent agent assignment
- ETA predictions

## 🔗 **Integration Setup**

### **1. JotForm Configuration**

Add this button/link in your JotForm for escalation:

```html
<!-- Add this to JotForm for advanced support -->
<div class="advanced-support-button">
    <p>Need more help? Our advanced AI assistant can help with:</p>
    <ul>
        <li>Complex technical issues</li>
        <li>Detailed complaint submission</li>
        <li>Real-time ticket tracking</li>
        <li>Priority support requests</li>
    </ul>
    <a href="http://172.28.0.217:5000" target="_blank" class="btn btn-primary">
        🤖 Chat with Prashna - Advanced AI Support
    </a>
</div>
```

### **2. JotForm Escalation Triggers**

Configure JotForm to show the Prashna link when:
- User selects "Complex Issue"
- Multiple FAQ attempts without resolution
- User types "I need more help"
- Specific keywords detected: "urgent", "escalate", "not working"

### **3. Prashna Welcome for JotForm Users**

Update Prashna to detect JotForm referrals:

```javascript
// Add to JotForm link
http://172.28.0.217:5000?source=jotform&issue=complex
```

## 🎨 **JotForm Integration Code**

### **JotForm Escalation Button**
```html
<style>
.escalation-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
}

.escalation-btn {
    background: white;
    color: #667eea;
    padding: 12px 24px;
    border: none;
    border-radius: 25px;
    font-weight: bold;
    text-decoration: none;
    display: inline-block;
    margin-top: 15px;
    transition: transform 0.2s;
}

.escalation-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
</style>

<div class="escalation-card">
    <h3>🚀 Need Advanced Support?</h3>
    <p>For complex issues, our AI assistant Prashna can provide:</p>
    <ul style="text-align: left; display: inline-block;">
        <li>Detailed ticket creation with priority assignment</li>
        <li>Real-time agent matching and ETA predictions</li>
        <li>Multi-step troubleshooting workflows</li>
        <li>Direct escalation to live agents</li>
    </ul>
    <a href="http://172.28.0.217:5000?ref=jotform" class="escalation-btn" target="_blank">
        💬 Chat with Prashna AI
    </a>
</div>
```

### **JotForm Conditional Logic**
```javascript
// Add this to JotForm's custom JavaScript
JotForm.init(function(){
    // Show escalation after 3 FAQ attempts
    let faqAttempts = 0;
    
    $('.faq-option').on('click', function(){
        faqAttempts++;
        if(faqAttempts >= 3) {
            $('.escalation-card').slideDown();
        }
    });
    
    // Show escalation for specific keywords
    $('#text_input').on('input', function(){
        const text = $(this).val().toLowerCase();
        const escalationKeywords = ['urgent', 'escalate', 'complex', 'not working', 'broken'];
        
        if(escalationKeywords.some(keyword => text.includes(keyword))) {
            $('.escalation-card').slideDown();
        }
    });
});
```

## 🤖 **Prashna Enhancements for JotForm Integration**

### **Detect JotForm Referrals**
```python
# Add to app.py
@app.route('/')
def index():
    """Serve the chatbot interface"""
    referral_source = request.args.get('ref', '')
    issue_type = request.args.get('issue', '')
    
    return render_template('chatbot.html', 
                         referral_source=referral_source,
                         issue_type=issue_type)
```

### **Enhanced Welcome for JotForm Users**
```python
def handle_jotform_referral(self):
    return {
        "message": "Hi! I see you came from our basic support. I'm Prashna, your advanced AI assistant! 🚀\n\nI can help with complex issues that need detailed attention:\n\n• Create priority support tickets\n• Match you with the right specialist\n• Provide accurate resolution times\n• Handle urgent escalations\n\nHow can I assist you today?",
        "type": "jotform_welcome",
        "buttons": [
            {"text": "Create Priority Ticket", "action": "priority_complaint"},
            {"text": "Urgent Issue", "action": "urgent_complaint"},
            {"text": "Technical Problem", "action": "technical_complaint"},
            {"text": "Check Existing Status", "action": "status_check"}
        ]
    }
```

## 📊 **User Journey Flow**

### **Typical User Path:**
```
1. User visits JotForm
2. Tries basic FAQ (1-2 questions)
3. Issue is complex/unresolved
4. JotForm shows "Advanced Support" option
5. User clicks → Redirected to Prashna (172.28.0.217:5000)
6. Prashna detects JotForm referral
7. Enhanced welcome + priority handling
8. Complete ticket creation with AI intelligence
```

### **Benefits:**
- ✅ **Fast Basic Support**: JotForm handles simple queries
- ✅ **Advanced Intelligence**: Prashna handles complex issues
- ✅ **Seamless Transition**: Users don't feel lost
- ✅ **Resource Optimization**: Right tool for right job
- ✅ **Better User Experience**: Progressive support levels

## 🚀 **Next Steps**

1. **Update JotForm**: Add escalation buttons and conditional logic
2. **Enhance Prashna**: Add JotForm referral detection
3. **Test Integration**: Verify smooth user transition
4. **Add Analytics**: Track escalation rates and success

## 🔧 **Configuration**

### **Prashna Server**
- **URL**: `http://172.28.0.217:5000`
- **Status**: Ready for integration
- **Features**: Complete AI ticketing system

### **JotForm Setup**
- **Basic Support**: FAQ, simple queries
- **Escalation Trigger**: Complex issues, multiple attempts
- **Redirect**: Seamless transition to Prashna

This hybrid approach gives you the best of both worlds! 🎯