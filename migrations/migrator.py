"""
Database Migration Manager for ExpenseMate.
Handles versioned schema and data migrations safely with transaction rollback support.
"""
import os
import sqlite3
import importlib.util
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_migration_table(conn):
    """Creates the schema_migrations tracking table if it does not exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

def get_applied_migrations(conn):
    """Returns a set of all migration versions that have been successfully applied."""
    ensure_migration_table(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_migrations ORDER BY version ASC;")
    return {row[0] for row in cursor.fetchall()}

def get_migration_files():
    """Discovers and sorts all migration files matching pattern '00X_*.py'."""
    files = []
    for f in os.listdir(MIGRATIONS_DIR):
        if f.endswith('.py') and not f.startswith('__') and f != 'migrator.py':
            files.append(f)
    files.sort()
    return files

def load_migration_module(file_name):
    """Dynamically loads a migration module by file name."""
    module_name = file_name[:-3]
    file_path = os.path.join(MIGRATIONS_DIR, file_name)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_migrations(conn):
    """
    Applies all pending migrations in sequential order.
    Returns the list of applied migration versions.
    """
    ensure_migration_table(conn)
    applied = get_applied_migrations(conn)
    files = get_migration_files()
    newly_applied = []

    for f in files:
        version = f.split('_')[0]
        if version not in applied:
            logger.info(f"Applying migration: {f} (version {version})...")
            module = load_migration_module(f)
            if hasattr(module, 'up'):
                try:
                    module.up(conn)
                    conn.execute("INSERT INTO schema_migrations (version) VALUES (?);", (version,))
                    conn.commit()
                    newly_applied.append(version)
                    logger.info(f"Migration {f} applied successfully.")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to apply migration {f}: {e}")
                    raise
    return newly_applied

def rollback_migration(conn, target_version=None):
    """
    Rolls back the latest migration, or down to a specified target version.
    """
    ensure_migration_table(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_migrations ORDER BY version DESC;")
    rows = cursor.fetchall()
    if not rows:
        logger.info("No migrations to rollback.")
        return []

    rolled_back = []
    files_map = {f.split('_')[0]: f for f in get_migration_files()}

    for (version,) in rows:
        if target_version and version <= target_version:
            break
        f = files_map.get(version)
        if not f:
            logger.warning(f"Migration file for version {version} not found.")
            continue

        logger.info(f"Rolling back migration: {f} (version {version})...")
        module = load_migration_module(f)
        if hasattr(module, 'down'):
            try:
                module.down(conn)
                conn.execute("DELETE FROM schema_migrations WHERE version = ?;", (version,))
                conn.commit()
                rolled_back.append(version)
                logger.info(f"Migration {f} rolled back successfully.")
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to rollback migration {f}: {e}")
                raise
        # If no target specified, rollback only the single latest migration
        if target_version is None:
            break

    return rolled_back
