import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the sqlite3.Row error
old_pattern = r"            # Send SMS to emergency contact if available\n            if user\.get\('emergency_contact_phone'\):"
new_pattern = "            # Send SMS to emergency contact if available\n            user_dict = dict(user) if user else {}\n            if user_dict.get('emergency_contact_phone'):"

content = re.sub(old_pattern, new_pattern, content)

# Also fix the username reference
content = content.replace("f\"HavenMind Alert: {user['username']}", "f\"HavenMind Alert: {user_dict['username']}")
content = content.replace("\"numbers\": user['emergency_contact_phone']", "\"numbers\": user_dict['emergency_contact_phone']")

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed sqlite3.Row error")