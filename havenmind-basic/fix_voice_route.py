import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the voice journal route and fix the user.get() error there too
voice_route_pattern = r"(@app\.route\('/journal/voice'.*?return jsonify\(\{[^}]+\}\))"
match = re.search(voice_route_pattern, content, re.DOTALL)

if match:
    voice_route = match.group(1)
    # Fix user.get() calls in voice route
    fixed_voice_route = voice_route.replace("user.get('emergency_contact_phone')", "dict(user).get('emergency_contact_phone')")
    fixed_voice_route = fixed_voice_route.replace("user['username']", "dict(user)['username']")
    fixed_voice_route = fixed_voice_route.replace("user['id']", "dict(user)['id']")
    
    content = content.replace(voice_route, fixed_voice_route)

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed voice route user object errors")