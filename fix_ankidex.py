import re

def insert_anki_bridge_injection(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    if 'profile.scripts().insert(_bridge_script)' in content:
        return

    injection = """
        try:
            from aqt.webview import _bridge_script
            if not self.profile.scripts().contains(_bridge_script):
                self.profile.scripts().insert(_bridge_script)
        except ImportError:
            pass
"""
    new_content = content.replace("        self.profile = QWebEngineProfile()\n", "        self.profile = QWebEngineProfile()\n" + injection)

    with open(filepath, 'w') as f:
        f.write(new_content)

insert_anki_bridge_injection('src/Ankimon/ankidex/ankidex_obj.py')
