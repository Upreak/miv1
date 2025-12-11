@echo off
REM Start Cloudflare tunnel forwarding local FastAPI (port 8000) to a public URL
cloudflared tunnel --url http://localhost:8000
