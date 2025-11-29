import re

# Read the file
with open('templates/journal.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the async AI loading with original sync version
old_ai_section = r'<div class="ai-response".*?</div>'
new_ai_section = '''<p class="text-sm text-blue-700">
                                {{ generate_ai_response(entry.content, entry.emotion_tags, entry.sentiment_score) }}
                            </p>'''

content = re.sub(old_ai_section, new_ai_section, content, flags=re.DOTALL)

# Remove the async loading JavaScript
js_pattern = r'// Load AI responses asynchronously.*?}\);'
content = re.sub(js_pattern, '', content, flags=re.DOTALL)

# Write back to file
with open('templates/journal.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Reverted to original AI responses")