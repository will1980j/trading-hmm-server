# 📤 INDICATOR EXPORT - QUICK REFERENCE CARD

**Print this and keep it handy during export!**

---

## 🎯 THE GOAL
Import 2,124 signals from indicator → database (30 minutes)

---

## 📋 THE 5 STEPS

### 1. DEPLOY BACKEND (5 min)
```
GitHub Desktop → Commit → Push → Wait
```

### 2. ENABLE EXPORT (2 min)
```
TradingView → Indicator Settings → Export
✅ Enable Bulk Export
Delay = 0
```

### 3. CREATE ALERT (2 min)
```
Right-click chart → Add Alert
Webhook: https://web-production-f8c3.up.railway.app/api/indicator-inspector/receive
Message: {{strategy.order.alert_message}}
Frequency: Once Per Bar Close
```

### 4. WAIT FOR EXPORT (3 min)
```
Watch: 📤 EXPORT: Batch X/107
Done: 📤 EXPORT: ✅ COMPLETE
```

### 5. IMPORT (5 min)
```bash
python analyze_indicator_export.py
python import_indicator_data.py
```

---

## ✅ SUCCESS LOOKS LIKE

```
Dashboard:
  Active: 510
  Completed: 1,614
  Total: 2,124 ✅
```

---

## 🚨 TROUBLESHOOTING

**Export not starting?**
- Check ✅ Enable Bulk Export
- Verify alert exists
- Check webhook URL

**Export stuck?**
- Disable/re-enable export
- Check indicator panel
- Verify Railway deployed

**Import fails?**
```bash
python verify_export_system.py
```

---

## 📞 QUICK COMMANDS

```bash
# Verify system
python verify_export_system.py

# Analyze data
python analyze_indicator_export.py

# Import to database
python import_indicator_data.py
```

---

## 🔗 WEBHOOK URL
```
https://web-production-f8c3.up.railway.app/api/indicator-inspector/receive
```

---

## 📚 FULL GUIDES

- `READY_TO_EXPORT.md` - Quick start
- `EXPORT_VISUAL_GUIDE.md` - Visual guide
- `INDICATOR_EXPORT_SETUP_GUIDE.md` - Detailed steps

---

**Good luck! 🚀**
