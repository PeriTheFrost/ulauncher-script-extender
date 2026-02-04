#!/usr/bin/env python3

import os
import subprocess
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

class ScriptRunner(Extension):
    def __init__(self):
        super(ScriptRunner, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        query = (event.get_argument() or "").lower()
        
        # Handle ~/ to /home/user and $HOME variable environtment
        raw_path = extension.preferences['scripts_dir']
        scripts_dir = os.path.expanduser(os.path.expandvars(raw_path))

        if not os.path.exists(scripts_dir):
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png', 
                    name="Directory Not Found", 
                    description=f"Tried to expand to: {scripts_dir}")
            ])

        # Scan all file .sh
        scripts = [f for f in os.listdir(scripts_dir) if f.endswith('.sh')]
        filtered = [s for s in scripts if query in s.lower()][:10]

        for script in filtered:
            full_path = os.path.join(scripts_dir, script)
            # Create name view (remove .sh and change dash/underscore with space)
            display_name = script.replace('.sh', '').replace('-', ' ').replace('_', ' ').title()
            
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=display_name,
                description=f"Run: {script}",
                on_enter=ExtensionCustomAction(full_path)
            ))

        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        script_path = event.get_data()
        terminal = extension.preferences['terminal_emulator']
        
        # Make sure terminal emulator support expansion path if any
        terminal_cmd = os.path.expanduser(os.path.expandvars(terminal))
        
        subprocess.Popen([
            terminal_cmd, 
            "--", "bash", "-c", 
            f"chmod +x '{script_path}'; '{script_path}'; echo -e '\n--- Script Finished ---'; read -p 'Press Enter to close...'"
        ])

        return HideWindowAction()

if __name__ == '__main__':
    ScriptRunner().run()
