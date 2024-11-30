from peewee import *
import logging
from models.models import (
    GameData, PendingWindowsGames, PendingMultiOSGames,
    NodeStatus, SyncHistory
)
from datetime import datetime

class DatabaseMigration:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def run_migrations(self):
        """Run all migrations across all nodes"""
        try:
            self.logger.info("Starting database migrations...")
            
            # Drop existing tables first
            self.drop_all_tables()
            
            # Master node migrations
            if self.db_manager.is_master_up():
                self.migrate_master()
            else:
                raise Exception("Master node must be available for migrations")

            # Slave A migrations
            if self.db_manager.is_slave_a_up():
                self.migrate_slave_a()
            else:
                self.logger.warning("Slave A node is down, skipping migrations")

            # Slave B migrations
            if self.db_manager.is_slave_b_up():
                self.migrate_slave_b()
            else:
                self.logger.warning("Slave B node is down, skipping migrations")

            self.logger.info("Database migrations completed successfully")
            
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            raise

    def drop_all_tables(self):
        """Drop all existing tables to ensure clean migration"""
        try:
            # Drop tables in master
            if self.db_manager.is_master_up():
                self.db_manager.master_db.drop_tables([
                    GameData, PendingWindowsGames, PendingMultiOSGames,
                    NodeStatus, SyncHistory
                ], safe=True)
            
            # Drop tables in slaves
            if self.db_manager.is_slave_a_up():
                self.db_manager.slave_a_db.drop_tables([GameData], safe=True)
            
            if self.db_manager.is_slave_b_up():
                self.db_manager.slave_b_db.drop_tables([GameData], safe=True)
                
        except Exception as e:
            self.logger.warning(f"Error dropping tables: {str(e)}")

    def migrate_master(self):
        """Run migrations on master node"""
        self.logger.info("Running migrations on master node...")
        
        # Bind models to master database
        GameData._meta.database = self.db_manager.master_db
        PendingWindowsGames._meta.database = self.db_manager.master_db
        PendingMultiOSGames._meta.database = self.db_manager.master_db
        NodeStatus._meta.database = self.db_manager.master_db
        SyncHistory._meta.database = self.db_manager.master_db
        
        try:
            # Create tables without transaction
            self.db_manager.master_db.create_tables([
                GameData,
                PendingWindowsGames,
                PendingMultiOSGames,
                NodeStatus,
                SyncHistory
            ], safe=True)

            # Initialize node status records
            self._initialize_node_status()
            
            self.logger.info("Master node migration completed")
            
        except Exception as e:
            self.logger.error(f"Master node migration failed: {str(e)}")
            raise

    def migrate_slave_a(self):
        """Run migrations on Slave A (Windows) node"""
        self.logger.info("Running migrations on Slave A node...")
        
        # Bind GameData model to slave_a database
        GameData._meta.database = self.db_manager.slave_a_db
        
        try:
            # Create only GameData table on Slave A
            self.db_manager.slave_a_db.create_tables([GameData], safe=True)
            self.logger.info("Slave A node migration completed")
            
        except Exception as e:
            self.logger.error(f"Slave A node migration failed: {str(e)}")
            raise

    def migrate_slave_b(self):
        """Run migrations on Slave B (Multi-platform) node"""
        self.logger.info("Running migrations on Slave B node...")
        
        # Bind GameData model to slave_b database
        GameData._meta.database = self.db_manager.slave_b_db
        
        try:
            # Create only GameData table on Slave B
            self.db_manager.slave_b_db.create_tables([GameData], safe=True)
            self.logger.info("Slave B node migration completed")
            
        except Exception as e:
            self.logger.error(f"Slave B node migration failed: {str(e)}")
            raise

    def _initialize_node_status(self):
        """Initialize node status records if they don't exist"""
        nodes = ['master', 'slave_a', 'slave_b']
        for node in nodes:
            try:
                NodeStatus.get_or_create(
                    NodeName=node,
                    defaults={
                        'IsAvailable': True,
                        'LastChecked': datetime.now(),
                        'FailureCount': 0
                    }
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize node status for {node}: {str(e)}")

    def rollback_migration(self, node):
        """Rollback migrations for a specific node"""
        self.logger.info(f"Rolling back migrations for {node} node...")
        
        try:
            db = self.db_manager.get_connection(node)
            
            # Bind models to the appropriate database
            if node == 'master':
                GameData._meta.database = db
                PendingWindowsGames._meta.database = db
                PendingMultiOSGames._meta.database = db
                NodeStatus._meta.database = db
                SyncHistory._meta.database = db
            else:
                GameData._meta.database = db
            
            # Drop tables without transaction
            if node == 'master':
                db.drop_tables([
                    GameData,
                    PendingWindowsGames,
                    PendingMultiOSGames,
                    NodeStatus,
                    SyncHistory
                ], safe=True)
            else:
                db.drop_tables([GameData], safe=True)
                    
            self.logger.info(f"Rollback completed for {node} node")
            
        except Exception as e:
            self.logger.error(f"Rollback failed for {node} node: {str(e)}")
            raise

def run_migrations(db_manager):
    """Helper function to run all migrations"""
    migration = DatabaseMigration(db_manager)
    migration.run_migrations()

# Example usage
if __name__ == "__main__":
    from services.db_manager import DatabaseManager
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    db_manager = DatabaseManager()
    
    try:
        run_migrations(db_manager)
    except Exception as e:
        print(f"Migration failed: {str(e)}")
    finally:
        db_manager.cleanup()
