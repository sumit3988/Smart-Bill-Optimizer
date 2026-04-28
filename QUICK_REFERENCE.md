# ⚡ QUICK REFERENCE CARD

## 🚀 START THE APP (Copy & Paste)

### Windows PowerShell
```powershell
# Navigate to project
cd e:\Projects\SmartElectricityOptimizer

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Flask app
python app.py

# Then open browser:
# http://localhost:5000
```

### Windows Command Prompt
```batch
cd e:\Projects\SmartElectricityOptimizer
venv\Scripts\activate.bat
python app.py
REM Then open http://localhost:5000
```

### Linux/Mac
```bash
cd ~/Projects/SmartElectricityOptimizer
source venv/bin/activate
python app.py
# Then open http://localhost:5000
```

---

## 📁 KEY FILES

| File | Purpose | Must-Know |
|------|---------|-----------|
| `app.py` | Main app (350 lines) | Routes, calculations, insights |
| `chatbot.py` | AI assistant (380 lines) | **Most important** - answers questions |
| `database.py` | Data storage (220 lines) | Stores user data, history |
| `model.py` | Bill predictor (11 lines) | ML-based bill estimation |
| `templates/dashboard.html` | Main UI (900 lines) | Professional interface |
| `test_app.py` | Test suite (80 lines) | Verify everything works |

---

## 🎯 DASHBOARD SECTIONS

### 1. **Input Form** (Left)
- Enter appliance counts
- OR enter meter reading
- Click "Calculate"

### 2. **Results** (Right)
- Current bill
- Eco score
- Insights
- Tips

### 3. **Tracking** (Middle)
- Today's usage
- Weekly chart
- Monthly comparison

### 4. **Chatbot** (Bottom Right)
- 💬 Click blue button
- Ask any energy question
- Gets AI response instantly

### 5. **Profile** (Bottom)
- Enter family size
- Enter property type
- Set savings goal

### 6. **Knowledge** (Accordion)
- How bills work
- Peak/off-peak hours
- AC tips
- EV charging guide

---

## 💬 CHATBOT CHEAT SHEET

### Try These Questions
```
"How to reduce my bill?"
"Why is my usage high?"
"Best AC temperature?"
"EV charging tips?"
"AC optimization?"
"What can you do?"
"How bills calculated?"
"Peak hours explained?"
"Appliance power consumption?"
"Save ₹500/month how?"
```

### What Chatbot Knows
- ✅ All appliances & power
- ✅ Billing slab system
- ✅ Peak/off-peak rates
- ✅ AC efficiency
- ✅ EV charging strategy
- ✅ Savings calculations
- ✅ Usage patterns
- ✅ Personalized advice

---

## 📊 EXAMPLE WORKFLOW

### Step 1: Enter Data
```
AC: 2
Fridge: 1
Fan: 2
TV: 1
Others: 0
```

### Step 2: See Results
```
Bills: ₹2,500
Eco Score: 40 (Red - Needs Improvement)
```

### Step 3: View Insights
```
🔌 AC IS YOUR TOP CONSUMER (270 units/month)
💰 Potential savings: 25%
❄️ Reduce AC temp by 1°C → Save ₹50/month
📈 Your bill increased 15% from last month
```

### Step 4: Read Tips
```
❄️ AC Temperature Optimization → Save ₹150/month
💡 LED Bulb Upgrade → Save ₹50/month
⭐ 5-Star Appliances → Save ₹150/month
```

### Step 5: Chat with Bot
```
You: "How to reduce AC bill?"

Bot: "❄️ AC Optimization Guide:
     • Set to 24°C (saves ₹50/month)
     • Use sleep mode (saves ₹30/month)
     • Close AC in unused rooms (₹20/month)
     → Total potential: ₹100/month"
```

---

## 🎨 COLOR MEANINGS

| Color | Meaning | Action |
|-------|---------|--------|
| 🟢 Green | Efficient | Keep it up! |
| 🟡 Yellow | Moderate | Can improve |
| 🔴 Red | High/Alert | Optimize now |
| 🔵 Blue | Information | Additional details |

---

## 📈 ECO SCORE RANGES

| Score | Label | Assessment |
|-------|-------|------------|
| 90-100 | Excellent 🟢 | ≤100 units/month |
| 75-89 | Good 🟡 | 150-200 units/month |
| 60-74 | Moderate 🟡 | 250-300 units/month |
| 40-59 | Poor 🔴 | 350-400 units/month |
| <40 | Critical 🔴 | >400 units/month |

---

## 💰 TYPICAL SAVINGS

| Action | Monthly Saving | Effort |
|--------|-----------------|--------|
| AC at 24°C | ₹50-100 | Easy |
| AC sleep mode | ₹30-50 | Very easy |
| EV off-peak charging | ₹300-400 | Medium |
| LED bulbs | ₹50-80 | Medium |
| Close AC in unused rooms | ₹20-30 | Easy |
| 5-star appliances | ₹100-200 | Hard |
| Skip peak hours usage | ₹50-100 | Medium |

---

## 🔧 MAINTENANCE

### Reset Database
```bash
# Delete database file
rm energy_tracker.db
# OR on Windows
del energy_tracker.db

# App will auto-create new database on next run
python app.py
```

### Check Last error
```bash
# View Flask console output
# (Flask runs in debug mode - shows errors)
python app.py
```

### View Data
```bash
# List database tables
python
>>> import sqlite3
>>> conn = sqlite3.connect('energy_tracker.db')
>>> c = conn.cursor()
>>> c.execute("SELECT name FROM sqlite_master WHERE type='table'")
>>> print([row[0] for row in c.fetchall()])
```

---

## 🌐 BROWSER COMPATIBILITY

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Excellent | Full support |
| Firefox | ✅ Excellent | Full support |
| Safari | ✅ Good | iOS supported |
| Edge | ✅ Excellent | Full support |
| IE 11 | ❌ Not supported | Use modern browser |

---

## 📱 MOBILE ACCESS

### From Another Device
```
1. Find your computer's IP
   Windows: ipconfig (look for IPv4)
   Mac: ifconfig (look for inet)
   
2. On mobile, go to:
   http://YOUR_IP:5000
   
   Example: http://192.168.1.10:5000
```

---

## 🆘 TROUBLESHOOTING

### "Address already in use"
```bash
# Change port in app.py last line:
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed to 5001

# Then visit: http://localhost:5001
```

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Make sure venv is activated
# Windows:
.\venv\Scripts\Activate.ps1

# Then reinstall:
pip install flask numpy
```

### "Template not found"
```bash
# Ensure files are in templates/ folder:
templates/
├── dashboard.html
└── knowledge.html

# If missing, copy them back
```

### Chatbot not responding
```
- Refresh the page (Ctrl+F5)
- Type clearly in input field
- Check browser console for errors (F12)
```

---

## 🎓 LEARNING RESOURCES

### Understanding the Code
- **Bill Calculation**: `app.py` lines 18-27
- **Appliance Estimation**: `app.py` lines 31-40
- **Chatbot Logic**: `chatbot.py` entire file
- **Database Setup**: `database.py` lines 1-50
- **UI Components**: `templates/dashboard.html`

### Key Concepts
- **Slab System**: Progressive pricing per unit (₹3, ₹5, ₹7, ₹10)
- **Eco Score**: Efficiency rating based on consumption
- **Off-Peak**: 10 PM - 6 AM (40% cheaper electricity)
- **Peak Hours**: 6 PM - 9 PM (expensive)
- **Eco Rating**: AC + EV = biggest consumption

---

## 📞 FAQ QUICK ANSWERS

**Q: Why does chatbot say "partially initialized module pandas"?**
A: Bug fixed in latest version. Delete `energy_tracker.db` and restart.

**Q: Can app access real meter data?**
A: No, it's manual entry. Can be integrated with IoT devices.

**Q: Is data secure?**
A: Good for personal use. Production needs authentication.

**Q: Can I share with family?**
A: Yes! On LAN, use your computer's IP + port 5000.

**Q: How to export data?**
A: Database is SQLite. Can be exported with SQL tools.

---

## ⚡ YOU'RE ALL SET!

```
Status: ✅ READY TO USE
        ✅ ALL TESTS PASSED
        ✅ FEATURES COMPLETE
        ✅ UI PROFESSIONAL
        ✅ CHATBOT ACTIVE
```

### Run Now:
```bash
python app.py
```

### Open Browser:
```
http://localhost:5000
```

### Enjoy Saving! 🎉
