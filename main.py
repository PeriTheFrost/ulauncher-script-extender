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

    def expand_path(self, path):
        """Helper to handle ~ and $VARs"""
        if not path:
            return ""
        return os.path.expanduser(os.path.expandvars(path))

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        query = (event.get_argument() or "").lower()
        
        raw_paths = extension.preferences['scripts_dir'].split(',')
        
        all_scripts = []
        for p in raw_paths:
            p = p.strip()
            if not p or p.startswith('!'):
                continue
            
            scripts_dir = extension.expand_path(p)
            
            if os.path.exists(scripts_dir):
                try:
                    for f in os.listdir(scripts_dir):
                        if f.endswith('.sh'):
                            all_scripts.append({
                                "filename": f,
                                "full_path": os.path.join(scripts_dir, f)
                            })
                except Exception:
                    continue

        filtered = [s for s in all_scripts if query in s['filename'].lower()][:10]

        if not filtered and not query:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png', name="No scripts found", description="Add some .sh files to your configured directories.")
            ])

        for script in filtered:
            display_name = script['filename'].replace('.sh', '').replace('-', ' ').replace('_', ' ').title()
            
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=display_name,
                description=f"Path: {script['full_path']}",
                on_enter=ExtensionCustomAction(script['full_path'])
            ))

        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):
    def run_terminal_command(self, terminal, working_dir, command=None):
        """Helper terminal emulator"""
        # 1. Konsole (KDE)
        if "konsole" in terminal:
            args = [terminal, "--workdir", working_dir]
            if command:
                args += ["-e", "bash", "-ic", command]
            else:
                args += ["-e", "bash"]
            subprocess.Popen(args)

        # 2. XFCE4 Terminal
        elif "xfce4-terminal" in terminal:
            full_command = f"bash -ic \"{command}\""
            args = [terminal, "--working-directory", working_dir, "-e", full_command]
            subprocess.Popen(args)

        # 3. Terminator
        elif "terminator" in terminal:
            args = [terminal, "--working-directory", working_dir]
            if command:
                args += ["-x", "bash", "-ic", command]
            else:
                args += ["-x", "bash"]
            subprocess.Popen(args)

        # 4. GNOME Terminal / Default
        else:
            args = [terminal, "--working-directory", working_dir, "--"]
            if command:
                args += ["bash", "-ic", command]
            else:
                args += ["bash"]
            subprocess.Popen(args)

    def on_event(self, event, extension):
        script_path = event.get_data()
        working_dir = os.path.dirname(script_path) 
        
        terminal = extension.expand_path(extension.preferences['terminal_emulator'])
        
        cmd = (
            f"chmod +x '{script_path}'; '{script_path}'; "
            f"echo -e '\\n--- Script Finished ---'; "
            f"read -p 'Press Enter to close...'"
        )

        self.run_terminal_command(terminal, working_dir, command=cmd)

        return HideWindowAction()

if __name__ == '__main__':
    ScriptRunner().run()