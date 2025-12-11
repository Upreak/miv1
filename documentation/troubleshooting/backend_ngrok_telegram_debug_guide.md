# **BACKEND + NGROK + ROUTE DEBUG GUIDE**

**(FastAPI + Telegram Bot + Ngrok)**

This document explains:
- Why ngrok sometimes shows connection errors
- Why `/api/v1/telegram/configuration` returns `{"detail": "Not Found"}`
- How to correctly diagnose & fix backend routing issues
- How to ensure your backend exposes Telegram endpoints

---

## 🔍 1. Understanding the Full Problem

You experienced 3 separate issues:

### Issue 1 — Ngrok Error (ERR_NGROK_108)
**Your account is limited to 1 simultaneous ngrok agent session**

✔ **Cause**
Another ngrok instance was already running.

✔ **Fix**
Terminate old ngrok sessions:
```powershell
taskkill /IM ngrok.exe /F
```

Or terminate from ngrok dashboard: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/run-tunnel/

Then start the Cloudflare tunnel:
```bat
cloudflared tunnel --url http://localhost:8000
```

---

### Issue 2 — Backend was not running on port 8000

Testing:
```powershell
netstat -ano | findstr :8000
```

returned no listeners → no server running.

So the backend was not listening; start it before tunneling.

✔ **Fix**
Start backend from the correct folder:
```powershell
cd test2/Backend
uvicorn backend_app.main:app --reload --port 8000
```

Correct working directory was essential because of imports.

---

### Issue 3 — Wrong Python module path

You originally ran:
```bash
uvicorn backend_app.main:app
```

But the folder structure was:
```
Backend/backend_app/
```

So Python could not import:
```python
from backend_app.config_settings import settings
```

and crashed.

✔ **Fix**
Run Uvicorn from inside the `Backend/` directory:
```powershell
cd test2/Backend
uvicorn backend_app.main:app --reload --port 8000
```

---

### Issue 4 — Telegram route returned 404 ("Not Found")

Even after ngrok and backend were running, accessing:
```
/api/v1/telegram/configuration
```

returned:
```json
{"detail": "Not Found"}
```

✔ **Cause**
FastAPI only exposes routes that are properly included:
```python
app.include_router(telegram_router, prefix="/api/v1/telegram")
```

If:
- Router is not included
- Prefix is wrong
- Filename is different
- Path is misconfigured

…then the URL returns 404.

✔ **Fix Steps**

**STEP 1 — Open `backend_app/main.py`**

Check that this exists inside:
```
test2/Backend/backend_app/main.py
```

**STEP 2 — Verify router inclusion**

You must see something like:
```python
from backend_app.telegram.telegram_router import router as telegram_router
app.include_router(telegram_router, prefix="/api/v1/telegram")
```

If this line is missing → Telegram endpoints do not exist.

**STEP 3 — Check router file**

Open:
```
backend_app/telegram/
```

and confirm the function:
```python
@router.get("/configuration")
async def get_config():
    ...
```

If prefix or filename is different, final URL changes.

**STEP 4 — Build correct URL**

If:
- `prefix = /api/v1/telegram`
- and `endpoint = /configuration`

final path becomes:
```
/api/v1/telegram/configuration
```

If prefix differs:
- `/telegram/configuration`
- `/api/telegram/configuration`
- `/api/v1/configuration`

your URL must match.

---

## ✔ Summary of Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| ngrok ERR_NGROK_108 | Too many sessions | `taskkill /IM ngrok.exe /F` |
| ngrok 404 / connection refused | Backend not listening on 8000 | Start backend correctly |
| ModuleNotFoundError backend_app | Wrong working directory | Run from `/Backend` folder |
| FastAPI endpoint returns 404 | Router not included or wrong prefix | Fix `app.include_router()` |
| Telegram configuration not found | Wrong path | Verify prefix and endpoint |

---

## 🧪 Final Verification Steps

After applying fixes:

**1. Check backend is listening**
```powershell
netstat -ano | findstr :8000
```
Should show `LISTENING`.

**2. Test local config endpoint**
```
http://localhost:8000/api/v1/telegram/configuration
```
Should return JSON.

**3. Start ngrok**
```bash
ngrok http 8000
```

**4. Test ngrok endpoint**
```
https://xxxx.ngrok-free.app/api/v1/telegram/configuration
```
Should return the same JSON.

**5. Finally, set webhook**
```
https://xxxx.ngrok-free.app/api/v1/telegram/set-webhook
```

**6. Test Telegram Bot**
Send message to your bot.

---

## 🛠 Future Troubleshooting Checklist (Use This Always)

1️⃣ Is backend running?  
2️⃣ Is backend running from correct directory?  
3️⃣ Does import path match folder structure?  
4️⃣ Does router exist in `main.py`?  
5️⃣ Does router prefix match your URL?  
6️⃣ Is ngrok forwarding correctly?  
7️⃣ Is ngrok allowed only one session?  
8️⃣ Do Telegram tokens exist in `.env`?  
9️⃣ Did you restart backend after changing env?  

**If ANY of these fail → you get 404 or connection refused.**
