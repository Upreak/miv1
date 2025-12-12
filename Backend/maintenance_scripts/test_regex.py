
import re

token = "7980838931:AAGBEjbuajf8Nvy3ZSYTJ_Q9B4dXhLGJ9F8"
pattern = r'^\d+:[A-Za-z0-9_-]{35,}$'

match = re.match(pattern, token)
print(f"Token: {token}")
print(f"Pattern: {pattern}")
print(f"Match: {bool(match)}")

if not match:
    # Debug why
    parts = token.split(':')
    if len(parts) != 2:
        print("Split failed")
    else:
        print(f"Part 1 (digits): {parts[0].isdigit()}")
        print(f"Part 2 length: {len(parts[1])}")
        print(f"Part 2 chars: {set(parts[1])}")
