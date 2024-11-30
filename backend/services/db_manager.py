from peewee import *
import logging
from models.models import GameData, PendingWindowsGames, PendingMultiOSGames

class DatabaseManager:
    def __init__(self):
        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Database configurations
        self.db_configs = {
            'master': {
                'host': 'localhost',
                'port': 3306,
                'user': 'admin',
                'password': 'password',
                'database': 'games'
            },
            'slave_a': {
                'host': 'localhost',
                'port': 3307,
                'user': 'admin',
                'password': 'password',
                'database': 'games'
            },
            'slave_b': {
                'host': 'localhost',
                'port': 3308,
                'user': 'admin',
                'password': 'password',
                'database': 'games'
            }
        }

        # Initialize database connections
        self.master_db = MySQLDatabase(**self.db_configs['master'])
        self.slave_a_db = MySQLDatabase(**self.db_configs['slave_a'])
        self.slave_b_db = MySQLDatabase(**self.db_configs['slave_b'])

        # Node status tracking
        self.node_status = {
            'master': True,
            'slave_a': True,
            'slave_b': True
        }

        # Bind models to master database for pending tables
        self.bind_models()

    def bind_models(self):
        """Bind models to appropriate databases"""
        # Bind main GameData model to master database
        GameData._meta.database = self.master_db

        # Bind pending tables to master database
        PendingWindowsGames._meta.database = self.master_db
        PendingMultiOSGames._meta.database = self.master_db

    def create_tables(self):
        """Create all necessary tables in the databases"""
        try:
            # Create tables in master
            with self.master_db:
                self.master_db.create_tables([
                    GameData,
                    PendingWindowsGames,
                    PendingMultiOSGames
                ], safe=True)

            # Create GameData table in slave_a
            with self.slave_a_db:
                self.slave_a_db.create_tables([GameData], safe=True)

            # Create GameData table in slave_b
            with self.slave_b_db:
                self.slave_b_db.create_tables([GameData], safe=True)

            self.logger.info("All tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating tables: {str(e)}")
            raise

    def check_connection(self, db):
        """Check if database connection is alive"""
        try:
            if db.is_closed():
                db.connect()
            db.execute_sql('SELECT 1')
            return True
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            return False

    def check_master_connection(self):
        """Check master node connection"""
        if not self.node_status['master']:
            return False
        return self.check_connection(self.master_db)

    def check_slave_a_connection(self):
        """Check slave A node connection"""
        if not self.node_status['slave_a']:
            return False
        return self.check_connection(self.slave_a_db)

    def check_slave_b_connection(self):
        """Check slave B node connection"""
        if not self.node_status['slave_b']:
            return False
        return self.check_connection(self.slave_b_db)

    def is_master_up(self):
        """Check if master node is up"""
        return self.node_status['master']

    def is_slave_a_up(self):
        """Check if slave A node is up"""
        return self.node_status['slave_a']

    def is_slave_b_up(self):
        """Check if slave B node is up"""
        return self.node_status['slave_b']

    def crash_node(self, node):
        """Simulate node crash"""
        if node not in self.node_status:
            raise ValueError(f"Invalid node: {node}")

        self.node_status[node] = False
        self.logger.info(f"Node {node} crashed")

        # Close database connection
        if node == 'master':
            if not self.master_db.is_closed():
                self.master_db.close()
        elif node == 'slave_a':
            if not self.slave_a_db.is_closed():
                self.slave_a_db.close()
        elif node == 'slave_b':
            if not self.slave_b_db.is_closed():
                self.slave_b_db.close()

    def restore_node(self, node):
        """Restore crashed node"""
        if node not in self.node_status:
            raise ValueError(f"Invalid node: {node}")

        self.node_status[node] = True
        self.logger.info(f"Node {node} restored")

        # Attempt to reconnect database
        try:
            if node == 'master':
                self.master_db.connect(reuse_if_open=True)
                if self.check_master_connection():
                    self.bind_models()  # Rebind models after reconnection
            elif node == 'slave_a':
                self.slave_a_db.connect(reuse_if_open=True)
            elif node == 'slave_b':
                self.slave_b_db.connect(reuse_if_open=True)
        except Exception as e:
            self.logger.error(f"Error restoring node {node}: {str(e)}")
            self.node_status[node] = False
            raise

    def get_connection(self, node):
        """Get database connection for specified node, if it's up"""
        if not self.node_status.get(node, False):
            return None  # Node is down

        if node == 'master':
            return self.master_db
        elif node == 'slave_a':
            return self.slave_a_db
        elif node == 'slave_b':
            return self.slave_b_db
        else:
            raise ValueError(f"Invalid node: {node}")

    def cleanup(self):
        """Clean up database connections"""
        for db in [self.master_db, self.slave_a_db, self.slave_b_db]:
            if not db.is_closed():
                db.close()

    def __del__(self):
        """Destructor to ensure connections are closed"""
        self.cleanup()
