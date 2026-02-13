#!/usr/bin/env python
"""
Scheduled Tasks for Time Capsule Application

This script is designed to be run by PythonAnywhere's scheduled tasks feature
or any other task scheduler (cron, etc.).

Usage:
    python tasks.py                    # Run all tasks
    python tasks.py delivery           # Only process scheduled deliveries
    python tasks.py reminders          # Only send reminders
    python tasks.py heartbeat          # Only process heartbeat checks
"""

import os
import sys
from datetime import datetime

# Add project directory to path (adjust for your deployment)
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
env_file = os.path.join(project_home, '.env.production')
if not os.path.exists(env_file):
    env_file = os.path.join(project_home, '.env')
load_dotenv(env_file)


def run_delivery_task():
    """Process all scheduled capsules that are due for delivery."""
    from app import create_app
    from app.config import ProductionConfig
    from app.services.scheduler_service import process_scheduled_capsules
    
    app = create_app(ProductionConfig)
    
    with app.app_context():
        print(f"[{datetime.now()}] Processing scheduled capsules...")
        result = process_scheduled_capsules()
        print(f"[{datetime.now()}] Delivery result: {result}")
        return result


def run_reminders_task():
    """Send reminder emails for upcoming capsule deliveries."""
    from app import create_app
    from app.config import ProductionConfig
    from app.services.scheduler_service import send_delivery_reminders
    
    app = create_app(ProductionConfig)
    
    with app.app_context():
        print(f"[{datetime.now()}] Sending delivery reminders...")
        result = send_delivery_reminders()
        print(f"[{datetime.now()}] Reminders result: {result}")
        return result


def run_heartbeat_task():
    """Process heartbeat checks for event-based capsules."""
    from app import create_app
    from app.config import ProductionConfig
    from app.services.scheduler_service import process_heartbeat_checks
    
    app = create_app(ProductionConfig)
    
    with app.app_context():
        print(f"[{datetime.now()}] Processing heartbeat checks...")
        result = process_heartbeat_checks()
        print(f"[{datetime.now()}] Heartbeat result: {result}")
        return result


def run_all_tasks():
    """Run all scheduled tasks."""
    print("=" * 50)
    print(f"Time Capsule Scheduled Tasks - {datetime.now()}")
    print("=" * 50)
    
    run_delivery_task()
    print("-" * 50)
    run_reminders_task()
    print("-" * 50)
    run_heartbeat_task()
    
    print("=" * 50)
    print("All tasks completed!")
    print("=" * 50)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Time Capsule scheduled tasks')
    parser.add_argument('task', nargs='?', default='all',
                        choices=['all', 'delivery', 'reminders', 'heartbeat'],
                        help='Which task to run (default: all)')
    
    args = parser.parse_args()
    
    if args.task == 'delivery':
        run_delivery_task()
    elif args.task == 'reminders':
        run_reminders_task()
    elif args.task == 'heartbeat':
        run_heartbeat_task()
    else:
        run_all_tasks()
