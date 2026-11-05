"""
CLI Entry point for managing ExpenseMate Database Migrations.
Usage:
    python manage_migrations.py up
    python manage_migrations.py down
    python manage_migrations.py status
"""
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from migrations.migrator import run_migrations, rollback_migration, get_applied_migrations, get_migration_files

def show_status():
    with get_db() as conn:
        applied = get_applied_migrations(conn)
        files = get_migration_files()
        print("=== Database Migration Status ===")
        for f in files:
            version = f.split('_')[0]
            status = "[APPLIED]" if version in applied else "[PENDING]"
            print(f"  {status} {f}")

def migrate_up():
    print("Running pending migrations...")
    with get_db() as conn:
        applied = run_migrations(conn)
        if applied:
            print(f"Successfully applied {len(applied)} migration(s): {', '.join(applied)}")
        else:
            print("No pending migrations. Database is up to date.")

def migrate_down():
    print("Rolling back latest migration...")
    with get_db() as conn:
        rolled_back = rollback_migration(conn)
        if rolled_back:
            print(f"Successfully rolled back {len(rolled_back)} migration(s): {', '.join(rolled_back)}")
        else:
            print("No migrations to rollback.")

if __name__ == '__main__':
    command = sys.argv[1].lower() if len(sys.argv) > 1 else 'status'
    if command == 'up':
        migrate_up()
    elif command == 'down':
        migrate_down()
    elif command == 'status':
        show_status()
    else:
        print(f"Unknown command: '{command}'. Use 'up', 'down', or 'status'.")
