#!/usr/bin/env python3
"""
Hook runner for Claude system integration.
This script is called after file modifications to run configured hooks.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class HookRunner:
    """Manages and executes hooks based on configuration."""
    
    def __init__(self, hooks_dir: Optional[Path] = None):
        self.hooks_dir = hooks_dir or Path(__file__).parent
        self.config_file = self.hooks_dir / 'hooks.json'
        self.config = self.load_config()
        self.log_file = self.hooks_dir / self.config['settings'].get('log_file', 'hooks.log')
        
    def load_config(self) -> Dict:
        """Load hook configuration from JSON file."""
        if not self.config_file.exists():
            return {
                'hooks': {'post-execution': []},
                'settings': {'hooks_enabled': True, 'verbose': True}
            }
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages to file and optionally to console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
        
        # Print to console if verbose
        if self.config['settings'].get('verbose', False):
            print(log_entry)
    
    def run_hook(self, hook_config: Dict) -> bool:
        """Run a single hook based on its configuration."""
        if not hook_config.get('enabled', True):
            self.log(f"Hook '{hook_config['name']}' is disabled, skipping.")
            return True
        
        script_path = self.hooks_dir / hook_config['script']
        
        if not script_path.exists():
            self.log(f"Hook script not found: {script_path}", "ERROR")
            return False
        
        self.log(f"Running hook: {hook_config['name']}")
        
        try:
            # Set environment variables for the hook
            env = os.environ.copy()
            env['HOOK_CONFIG'] = json.dumps(hook_config.get('config', {}))
            env['PROJECT_ROOT'] = str(Path.cwd())
            
            # Run the hook
            result = subprocess.run(
                [sys.executable, str(script_path)],
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                self.log(f"Hook output:\n{result.stdout}")
            
            if result.returncode != 0:
                self.log(f"Hook failed with code {result.returncode}", "ERROR")
                if result.stderr:
                    self.log(f"Error output:\n{result.stderr}", "ERROR")
                return False
            
            self.log(f"Hook '{hook_config['name']}' completed successfully")
            return True
            
        except Exception as e:
            self.log(f"Exception running hook: {e}", "ERROR")
            return False
    
    def run_hooks(self, hook_type: str = "post-execution") -> bool:
        """Run all hooks of the specified type."""
        if not self.config['settings'].get('hooks_enabled', True):
            self.log("Hooks are disabled globally")
            return True
        
        hooks = self.config['hooks'].get(hook_type, [])
        
        if not hooks:
            self.log(f"No {hook_type} hooks configured")
            return True
        
        self.log(f"Running {len(hooks)} {hook_type} hook(s)")
        
        all_success = True
        for hook in hooks:
            success = self.run_hook(hook)
            if not success:
                all_success = False
                # Continue running other hooks even if one fails
        
        return all_success
    
    def run_specific_hook(self, hook_name: str) -> bool:
        """Run a specific hook by name."""
        for hook_type, hooks in self.config['hooks'].items():
            for hook in hooks:
                if hook['name'] == hook_name:
                    return self.run_hook(hook)
        
        self.log(f"Hook '{hook_name}' not found", "ERROR")
        return False


def main():
    """Main entry point for hook runner."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run Claude hooks")
    parser.add_argument('--type', default='post-execution', 
                       help='Type of hooks to run (default: post-execution)')
    parser.add_argument('--hook', help='Run a specific hook by name')
    parser.add_argument('--list', action='store_true', help='List all configured hooks')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = HookRunner()
    
    # List hooks if requested
    if args.list:
        print("Configured hooks:")
        for hook_type, hooks in runner.config['hooks'].items():
            print(f"\n{hook_type}:")
            for hook in hooks:
                status = "enabled" if hook.get('enabled', True) else "disabled"
                print(f"  - {hook['name']} ({status}): {hook.get('description', 'No description')}")
        return
    
    # Run specific hook if requested
    if args.hook:
        success = runner.run_specific_hook(args.hook)
    else:
        # Run all hooks of the specified type
        success = runner.run_hooks(args.type)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()