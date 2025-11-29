import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the broken emergency contact code
pattern = r'            # Send to emergency contact if available\n            if user\.get\(\'emergency_contact_phone\'\):\n                emergency_msg = f"HavenMind Alert: \{user\[\'username\'\]\} may need support\. They\'ve expressed concerning emotions in their journal\. Please check on them\. If urgent, call crisis helpline: 91-9820466726"\n                notification_system\.send_telegram_to_number\(user\[\'emergency_contact_phone\'\], emergency_msg\)'

replacement = '            # Emergency contact notification disabled - requires proper setup'

# Replace all occurrences
new_content = re.sub(pattern, replacement, content)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed emergency contact notifications")