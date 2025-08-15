#!/usr/bin/env python3
"""
Demo parallel test script that integrates with the parallel debugging system.
Shows how to use session state, report metrics, and handle parallel execution.
"""

import os
import sys
import json
import time
import random
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from debug_session_state import DebugSessionState


async def demo_parallel_test():
    """Demo test that can run in parallel with proper session management."""
    
    # Get worker information from environment
    worker_id = os.environ.get('PARALLEL_WORKER_ID', 'unknown')
    session_id = os.environ.get('DEBUG_SESSION_ID', 'unknown')
    scenario_name = os.environ.get('PARALLEL_SCENARIO', 'demo')
    base_url = os.environ.get('BASE_URL', 'http://localhost:3000')
    
    print(f"Starting {scenario_name} on {worker_id} (session: {session_id})")
    
    # Initialize session state for this worker
    try:
        state = DebugSessionState(session_id)
        state.set_current_step("test_start", f"Starting {scenario_name}")
    except Exception as e:
        print(f"Warning: Could not initialize session state: {e}")
        state = None
    
    # Simulate test execution
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to page
            print(f"Navigating to {base_url}")
            await page.goto(base_url)
            
            # Save checkpoint
            if state:
                state.create_checkpoint("navigation_complete", "Successfully loaded page")
            
            # Simulate some work
            await asyncio.sleep(random.uniform(1, 3))
            
            # Step 2: Perform test actions
            # This is where you'd put your actual test logic
            
            # Report a metric
            metric = {
                "response_time": random.uniform(0.5, 2.0),
                "page_load_time": random.uniform(1.0, 3.0)
            }
            print(f"METRIC: {json.dumps(metric)}")
            
            # Simulate finding an issue (sometimes)
            if random.random() < 0.3:
                finding = {
                    "type": "observation",
                    "description": f"Slow page load detected in {scenario_name}",
                    "evidence": f"Page load took {metric['page_load_time']:.2f}s"
                }
                print(f"FINDING: {json.dumps(finding)}")
                
                if state:
                    state.add_finding(**finding)
            
            # Simulate success/failure
            if random.random() < 0.8:
                print(f" Test {scenario_name} completed successfully")
                if state:
                    state.create_checkpoint("test_complete", "All assertions passed")
                return 0
            else:
                raise Exception(f"Test assertion failed in {scenario_name}")
            
        except Exception as e:
            print(f" Test {scenario_name} failed: {str(e)}")
            
            if state:
                state.record_failed_attempt(
                    f"Test execution for {scenario_name}",
                    str(e),
                    {"url": page.url, "worker": worker_id}
                )
            
            # Take screenshot on failure
            screenshot_path = f"/tmp/failure_{worker_id}_{int(time.time())}.png"
            await page.screenshot(path=screenshot_path)
            print(f"ARTIFACT: {screenshot_path}")
            
            return 1
            
        finally:
            await browser.close()
            
            if state:
                state.complete_current_step(f"Test {scenario_name} finished")


def main():
    """Entry point for the test script."""
    # Run the async test
    result = asyncio.run(demo_parallel_test())
    sys.exit(result)


if __name__ == "__main__":
    main()