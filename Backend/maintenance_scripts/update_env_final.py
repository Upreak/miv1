
import os

updates = {
    'TELEGRAM_WEBHOOK_URL': 'https://arel-humans-cookies.trycloudflare.com',
    'TELEGRAM_BOT_TOKEN': '7980838931:AAFGLKKsdt_E3YjXA11Ula7r3YUFPxY22YD0',
    'TELEGRAM_WEBHOOK_SECRET': 'tk0v7615n0lizdvtybdo1fr0223907wm'
}

env_path = '.env'
new_lines = []
keys_updated = set()

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line_clean = line.strip()
            if not line_clean or line_clean.startswith('#'):
                new_lines.append(line)
                continue
                
            key = line_clean.split('=')[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}\n")
                keys_updated.add(key)
            else:
                new_lines.append(line)

# Add missing
for key, val in updates.items():
    if key not in keys_updated:
        new_lines.append(f"{key}={val}\n")

with open(env_path, 'w') as f:
    f.writelines(new_lines)

print("Updated .env")
