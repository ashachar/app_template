#!/usr/bin/env python3
"""
Parallel Monitor - Real-time monitoring dashboard for parallel debug execution.
Provides a terminal-based UI to track worker progress and status.
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
from queue import Queue, Empty
import shutil

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    
    # Cursor control
    CLEAR_LINE = '\033[2K'
    MOVE_UP = '\033[1A'
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'


class WorkerStatus:
    """Track status of a single worker."""
    
    def __init__(self, worker_id: str, scenario_name: str):
        self.worker_id = worker_id
        self.scenario_name = scenario_name
        self.status = "pending"
        self.message = "Waiting to start"
        self.start_time = None
        self.last_update = datetime.now()
        self.progress_steps = []
        self.error = None
    
    def update(self, status: str, message: str):
        """Update worker status."""
        self.status = status
        self.message = message
        self.last_update = datetime.now()
        
        if status == "starting" and not self.start_time:
            self.start_time = datetime.now()
        elif status == "failed":
            self.error = message
    
    def get_elapsed_time(self) -> str:
        """Get elapsed time since start."""
        if not self.start_time:
            return "0:00"
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes}:{seconds:02d}"
    
    def get_status_icon(self) -> str:
        """Get icon representing current status."""
        icons = {
            "pending": "⏳",
            "starting": "",
            "running": "",
            "executing": "",
            "completed": "",
            "failed": "",
            "cleanup": ""
        }
        return icons.get(self.status, "")
    
    def get_status_color(self) -> str:
        """Get color for current status."""
        colors = {
            "pending": Colors.DIM,
            "starting": Colors.CYAN,
            "running": Colors.BLUE,
            "executing": Colors.YELLOW,
            "completed": Colors.GREEN,
            "failed": Colors.RED,
            "cleanup": Colors.DIM
        }
        return colors.get(self.status, Colors.WHITE)


class ParallelMonitor:
    """Terminal-based monitoring dashboard for parallel execution."""
    
    def __init__(self, status_queue: Queue, scenarios: Dict[str, Any]):
        self.status_queue = status_queue
        self.scenarios = scenarios
        self.workers: Dict[str, WorkerStatus] = {}
        self.running = False
        self.lock = threading.Lock()
        
        # Terminal settings
        self.term_width = shutil.get_terminal_size().columns
        self.term_height = shutil.get_terminal_size().lines
        
        # Statistics
        self.stats = {
            'total': len(scenarios),
            'completed': 0,
            'failed': 0,
            'running': 0,
            'elapsed_time': 0
        }
        
        self.start_time = datetime.now()
        
    def run(self):
        """Run the monitoring dashboard."""
        self.running = True
        
        # Hide cursor
        print(Colors.HIDE_CURSOR, end='')
        
        # Clear screen
        os.system('clear' if os.name != 'cls' else 'cls')
        
        try:
            # Start update threads
            status_thread = threading.Thread(target=self._process_status_updates, daemon=True)
            status_thread.start()
            
            # Main display loop
            while self.running:
                self._update_display()
                time.sleep(0.5)  # Update every 500ms
                
        except KeyboardInterrupt:
            pass
        finally:
            # Show cursor
            print(Colors.SHOW_CURSOR, end='')
            # Clear screen one last time
            os.system('clear' if os.name != 'cls' else 'cls')
    
    def stop(self):
        """Stop the monitor."""
        self.running = False
    
    def _process_status_updates(self):
        """Process status updates from workers."""
        while self.running:
            try:
                update = self.status_queue.get(timeout=0.1)
                self._handle_status_update(update)
            except Empty:
                continue
            except Exception as e:
                print(f"Error processing status: {e}")
    
    def _handle_status_update(self, update: Dict[str, Any]):
        """Handle a status update from a worker."""
        with self.lock:
            worker_id = update.get('worker_id')
            scenario = update.get('scenario')
            status = update.get('status')
            message = update.get('message', '')
            
            # Create or update worker status
            if worker_id not in self.workers:
                self.workers[worker_id] = WorkerStatus(worker_id, scenario)
            
            worker = self.workers[worker_id]
            worker.update(status, message)
            
            # Update statistics
            self._update_stats()
    
    def _update_stats(self):
        """Update execution statistics."""
        self.stats['completed'] = sum(1 for w in self.workers.values() 
                                     if w.status == 'completed')
        self.stats['failed'] = sum(1 for w in self.workers.values() 
                                  if w.status == 'failed')
        self.stats['running'] = sum(1 for w in self.workers.values() 
                                   if w.status in ['starting', 'running', 'executing'])
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.stats['elapsed_time'] = elapsed
    
    def _update_display(self):
        """Update the terminal display."""
        # Move cursor to top
        print('\033[H', end='')
        
        # Clear and redraw
        self._draw_header()
        self._draw_progress_bar()
        self._draw_workers()
        self._draw_footer()
        
        # Flush output
        sys.stdout.flush()
    
    def _draw_header(self):
        """Draw the header section."""
        # Title
        title = " PARALLEL DEBUG MONITOR "
        padding = (self.term_width - len(title)) // 2
        print(f"{Colors.BOLD}{Colors.CYAN}{' ' * padding}{title}{' ' * padding}{Colors.RESET}")
        print("=" * self.term_width)
        
        # Statistics
        elapsed = int(self.stats['elapsed_time'])
        elapsed_str = f"{elapsed // 60}:{elapsed % 60:02d}"
        
        stats_line = (
            f"Total: {self.stats['total']} | "
            f"{Colors.GREEN}Completed: {self.stats['completed']}{Colors.RESET} | "
            f"{Colors.RED}Failed: {self.stats['failed']}{Colors.RESET} | "
            f"{Colors.YELLOW}Running: {self.stats['running']}{Colors.RESET} | "
            f"Time: {elapsed_str}"
        )
        
        # Center the stats line
        # Account for ANSI codes when calculating padding
        visible_length = (
            len(f"Total: {self.stats['total']} | Completed: {self.stats['completed']} | "
                f"Failed: {self.stats['failed']} | Running: {self.stats['running']} | "
                f"Time: {elapsed_str}")
        )
        padding = (self.term_width - visible_length) // 2
        print(f"{' ' * padding}{stats_line}")
        print("=" * self.term_width)
        print()
    
    def _draw_progress_bar(self):
        """Draw overall progress bar."""
        completed = self.stats['completed'] + self.stats['failed']
        total = self.stats['total']
        
        if total == 0:
            progress = 0
        else:
            progress = completed / total
        
        # Calculate bar width (leave room for percentage)
        bar_width = self.term_width - 20
        filled = int(bar_width * progress)
        empty = bar_width - filled
        
        # Create progress bar
        bar = f"[{'' * filled}{'' * empty}] {progress*100:.1f}%"
        
        # Color based on status
        if self.stats['failed'] > 0:
            color = Colors.YELLOW
        elif progress == 1.0:
            color = Colors.GREEN
        else:
            color = Colors.BLUE
        
        print(f"{color}{bar}{Colors.RESET}")
        print()
    
    def _draw_workers(self):
        """Draw worker status list."""
        print(f"{Colors.BOLD}WORKER STATUS:{Colors.RESET}")
        print("-" * self.term_width)
        
        # Sort workers by status (running first, then completed, then failed)
        sorted_workers = sorted(
            self.workers.values(),
            key=lambda w: (
                w.status == 'completed',
                w.status == 'failed',
                w.worker_id
            )
        )
        
        # Display each worker
        for worker in sorted_workers:
            self._draw_worker_line(worker)
        
        # Fill remaining space
        displayed = len(sorted_workers)
        remaining_lines = max(0, self.term_height - 15 - displayed)
        for _ in range(remaining_lines):
            print(Colors.CLEAR_LINE)
    
    def _draw_worker_line(self, worker: WorkerStatus):
        """Draw a single worker status line."""
        # Format components
        icon = worker.get_status_icon()
        color = worker.get_status_color()
        
        # Truncate scenario name if needed
        max_scenario_len = 30
        scenario = worker.scenario_name[:max_scenario_len]
        if len(worker.scenario_name) > max_scenario_len:
            scenario += "..."
        
        # Format message
        max_message_len = self.term_width - 60
        message = worker.message[:max_message_len]
        if len(worker.message) > max_message_len:
            message += "..."
        
        # Build line
        line = (
            f"{color}{icon} {worker.worker_id:<12} "
            f"{scenario:<35} "
            f"[{worker.get_elapsed_time():>5}] "
            f"{message}{Colors.RESET}"
        )
        
        # Clear line and print
        print(f"{Colors.CLEAR_LINE}{line}")
    
    def _draw_footer(self):
        """Draw the footer section."""
        print()
        print("=" * self.term_width)
        print(f"{Colors.DIM}Press Ctrl+C to stop monitoring{Colors.RESET}")


# Simple console monitor for non-terminal environments
class SimpleMonitor:
    """Simple text-based monitor for environments without terminal control."""
    
    def __init__(self, status_queue: Queue, scenarios: Dict[str, Any]):
        self.status_queue = status_queue
        self.scenarios = scenarios
        self.running = False
        self.last_update = {}
        
    def run(self):
        """Run simple monitoring."""
        self.running = True
        print(" Parallel Execution Monitor (Simple Mode)")
        print("=" * 60)
        
        while self.running:
            try:
                update = self.status_queue.get(timeout=1)
                self._print_update(update)
            except Empty:
                continue
            except KeyboardInterrupt:
                break
    
    def stop(self):
        """Stop the monitor."""
        self.running = False
    
    def _print_update(self, update: Dict[str, Any]):
        """Print a status update."""
        worker_id = update.get('worker_id')
        scenario = update.get('scenario')
        status = update.get('status')
        message = update.get('message', '')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Get status icon
        icons = {
            "starting": "",
            "running": "",
            "completed": "",
            "failed": ""
        }
        icon = icons.get(status, "ℹ")
        
        print(f"[{timestamp}] {icon} {worker_id}: {scenario} - {message}")


# Factory function to create appropriate monitor
def create_monitor(status_queue: Queue, scenarios: Dict[str, Any]) -> Any:
    """Create appropriate monitor based on environment."""
    # Check if we have a proper terminal
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        try:
            # Try to use the full terminal monitor
            return ParallelMonitor(status_queue, scenarios)
        except:
            # Fall back to simple monitor
            return SimpleMonitor(status_queue, scenarios)
    else:
        # Use simple monitor for non-terminal environments
        return SimpleMonitor(status_queue, scenarios)


# Demo
if __name__ == "__main__":
    from queue import Queue
    import random
    
    # Create demo queue and scenarios
    status_queue = Queue()
    scenarios = {
        f"worker_{i}": f"test_scenario_{i}"
        for i in range(4)
    }
    
    # Create monitor
    monitor = create_monitor(status_queue, scenarios)
    
    # Start monitor in thread
    monitor_thread = threading.Thread(target=monitor.run, daemon=True)
    monitor_thread.start()
    
    # Simulate status updates
    statuses = ["starting", "running", "executing", "completed", "failed"]
    messages = [
        "Initializing test environment",
        "Running test scenario",
        "Executing test steps",
        "Test completed successfully",
        "Test failed with error"
    ]
    
    try:
        for i in range(20):
            worker_id = f"worker_{random.randint(0, 3)}"
            status = random.choice(statuses)
            message = random.choice(messages)
            
            status_queue.put({
                'worker_id': worker_id,
                'scenario': scenarios[worker_id],
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
            
            time.sleep(random.uniform(0.5, 2))
    
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()
        print("\nMonitor stopped")