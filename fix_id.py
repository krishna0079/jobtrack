import os
import re

dir_path = r'c:\Users\kp\Desktop\job track\JobTrack'

# Update HTML files
for root, dirs, files in os.walk(os.path.join(dir_path, 'templates')):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = re.sub(r'\._id\b', '.id', content)
            if content != new_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated HTML: {filepath}')

# Update Python files
for root, dirs, files in os.walk(dir_path):
    if 'venv' in root or '.git' in root or '__pycache__' in root: continue
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_lines = []
            changed = False
            for line in content.split('\n'):
                new_lines.append(line)
                if '_id' in line and ' = str(' in line and line.strip().endswith(')'):
                    m = re.search(r'^(\s*)(\w+)\[\'_id\'\]\s*=\s*str\(', line)
                    if m:
                        indent = m.group(1)
                        var = m.group(2)
                        new_lines.append(f"{indent}{var}['id'] = {var}['_id']")
                        changed = True
            
            if changed:
                new_content = '\n'.join(new_lines)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated Python: {filepath}')
