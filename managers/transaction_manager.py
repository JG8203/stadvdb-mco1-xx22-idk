from db import get_database
from models.game import DimGame
from models.transaction import TransactionLog
from models.node_status import NodeStatus
from peewee import OperationalError
from datetime import datetime
import uuid
import json

class TransactionManager:
    def __init__(self):
        self.isolation_level = 'REPEATABLE READ'  # Default isolation level

    def set_isolation_level(self, level):
        """Set transaction isolation level."""
        valid_levels = ['READ UNCOMMITTED', 'READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE']
        if level not in valid_levels:
            raise ValueError(f"Invalid isolation level. Must be one of {valid_levels}")
        self.isolation_level = level

    def _get_target_nodes(self, game_data):
        """Determine which nodes should receive this data based on platform."""
        targets = ['node1']  # Central node always gets data

        if game_data.get('Windows') and not game_data.get('Mac') and not game_data.get('Linux'):
            targets.append('node2')  # Windows-only -> Node 2
        elif game_data.get('Windows') and (game_data.get('Mac') or game_data.get('Linux')):
            targets.append('node3')  # Multi-platform -> Node 3

        return targets

    def _log_transaction(self, transaction_id, operation, record_id, node_name, old_data=None, new_data=None, status='PENDING', error_message=None):
        """Log transaction details in the central node's database."""
        db = get_database('node1')  # Central node database
        TransactionLog.bind_database(db)
        db.connect()
        node_id = {'node1': 1, 'node2': 2, 'node3': 3}[node_name]
        TransactionLog.create(
            transaction_id=transaction_id,
            node_id=node_id,
            operation=operation,
            record_id=record_id,
            old_data=json.dumps(old_data) if old_data else None,
            new_data=json.dumps(new_data) if new_data else None,
            timestamp=datetime.now(),
            status=status,
            error_message=error_message,
            processed=(status == 'COMMITTED')
        )
        db.close()

    def _is_node_online(self, node_id):
        node_name = {1: 'node1', 2: 'node2', 3: 'node3'}[node_id]
        try:
            db = get_database(node_name)
            db.connect()
            db.close()
            return True
        except OperationalError:
            return False
        except Exception as e:
            print(f"Error checking node {node_id} status: {e}")
            return False


    def create_game(self, game_data):
        """Create a new game record across appropriate nodes."""
        transaction_id = str(uuid.uuid4())
        target_nodes = self._get_target_nodes(game_data)
        success = True
        record_id = None

        for node_name in target_nodes:
            node_id = {'node1': 1, 'node2': 2, 'node3': 3}[node_name]

            try:
                if not self._is_node_online(node_id):
                    # Node is offline; log transaction as pending
                    self._log_transaction(
                        transaction_id=transaction_id,
                        operation='INSERT',
                        record_id=None,
                        node_name=node_name,
                        new_data=game_data,
                        status='PENDING',
                        error_message='Node offline'
                    )
                    success = False
                    continue

                db = get_database(node_name)
                DimGame.bind_database(db)
                
                db.connect()
                db.execute_sql(f"SET TRANSACTION ISOLATION LEVEL {self.isolation_level}")
                db.begin()
                
                try:
                    game = DimGame.create(**game_data)
                    record_id = game.GameID  # Capture the record ID
                    db.commit()
                    
                    self._log_transaction(
                        transaction_id=transaction_id,
                        operation='INSERT',
                        record_id=record_id,
                        node_name=node_name,
                        new_data=game_data,
                        status='COMMITTED'
                    )
                except Exception as e:
                    db.rollback()
                    success = False
                    self._log_transaction(
                        transaction_id=transaction_id,
                        operation='INSERT',
                        record_id=None,
                        node_name=node_name,
                        new_data=game_data,
                        status='FAILED',
                        error_message=str(e)
                    )
                    print(f"Error creating game on {node_name}: {e}")
                    
            except OperationalError as e:
                # Handle connection errors
                success = False
                # Update node status to OFFLINE
                self._update_node_status(node_id, 'OFFLINE')
                self._log_transaction(
                    transaction_id=transaction_id,
                    operation='INSERT',
                    record_id=None,
                    node_name=node_name,
                    new_data=game_data,
                    status='PENDING',
                    error_message=f'OperationalError: {str(e)}'
                )
                print(f"OperationalError connecting to {node_name}: {e}")
                
            finally:
                try:
                    db.close()
                except:
                    pass  # Ignore errors when trying to close an unopened connection

        return success

    def read_game(self, game_id):
        """Read a game record from the central node."""
        db = get_database('node1')
        DimGame.bind_database(db)
        try:
            db.connect()
            game = DimGame.get_or_none(DimGame.GameID == game_id)
            return game.__data__ if game else None
        except Exception as e:
            print(f"Error reading game: {e}")
            return None
        finally:
            db.close()

    def update_game(self, game_id, game_data):
        """Update a game record across appropriate nodes."""
        transaction_id = str(uuid.uuid4())
        success = True
        old_data = None

        # Read existing data from central node
        db_central = get_database('node1')
        DimGame.bind_database(db_central)
        try:
            db_central.connect()
            old_game = DimGame.get_or_none(DimGame.GameID == game_id)
            if not old_game:
                print("Game not found on central node")
                return False
            old_data = old_game.__data__
        finally:
            db_central.close()

        target_nodes = self._get_target_nodes(game_data)

        # Update on each target node
        for node_name in target_nodes:
            node_id = {'node1': 1, 'node2': 2, 'node3': 3}[node_name]

            if not self._is_node_online(node_id):
                # Node is offline; log transaction as pending
                self._log_transaction(
                    transaction_id=transaction_id,
                    operation='UPDATE',
                    record_id=game_id,
                    node_name=node_name,
                    old_data=old_data,
                    new_data=game_data,
                    status='PENDING',
                    error_message='Node offline'
                )
                success = False
                continue

            db = get_database(node_name)
            DimGame.bind_database(db)
            try:
                db.connect()
                db.execute_sql(f"SET TRANSACTION ISOLATION LEVEL {self.isolation_level}")
                db.begin()
                query = DimGame.update(**game_data).where(DimGame.GameID == game_id)
                rows_updated = query.execute()
                if rows_updated == 0:
                    success = False
                    print(f"Game not found on {node_name}")
                    self._log_transaction(
                        transaction_id=transaction_id,
                        operation='UPDATE',
                        record_id=game_id,
                        node_name=node_name,
                        old_data=old_data,
                        new_data=game_data,
                        status='FAILED',
                        error_message='Game not found on node'
                    )
                else:
                    db.commit()
                    self._log_transaction(
                        transaction_id=transaction_id,
                        operation='UPDATE',
                        record_id=game_id,
                        node_name=node_name,
                        old_data=old_data,
                        new_data=game_data,
                        status='COMMITTED'
                    )
            except Exception as e:
                db.rollback()
                success = False
                self._log_transaction(
                    transaction_id=transaction_id,
                    operation='UPDATE',
                    record_id=game_id,
                    node_name=node_name,
                    old_data=old_data,
                    new_data=game_data,
                    status='FAILED',
                    error_message=str(e)
                )
                print(f"Error updating game on {node_name}: {e}")
            finally:
                db.close()

        return success

    def delete_game(self, game_id):
        """Delete a game record from all nodes."""
        transaction_id = str(uuid.uuid4())
        success = True
        old_data = None

        # Read existing data from central node
        db_central = get_database('node1')
        DimGame.bind_database(db_central)
        try:
            db_central.connect()
            old_game = DimGame.get_or_none(DimGame.GameID == game_id)
            if not old_game:
                print("Game not found on central node")
                return False
            old_data = old_game.__data__
        finally:
            db_central.close()

        target_nodes = ['node1', 'node2', 'node3']

        # Delete from each node
        for node_name in target_nodes:
            node_id = {'node1': 1, 'node2': 2, 'node3': 3}[node_name]

            if not self._is_node_online(node_id):
                # Node is offline; log transaction as pending
                self._log_transaction(
                    transaction_id=transaction_id,
                    operation='DELETE',
                    record_id=game_id,
                    node_name=node_name,
                    old_data=old_data,
                    status='PENDING',
                    error_message='Node offline'
                )
                success = False
                continue

            db = get_database(node_name)
            DimGame.bind_database(db)
            try:
                db.connect()
                db.execute_sql(f"SET TRANSACTION ISOLATION LEVEL {self.isolation_level}")
                db.begin()
                query = DimGame.delete().where(DimGame.GameID == game_id)
                rows_deleted = query.execute()
                if rows_deleted == 0:
                    success = False
                    print(f"Game not found on {node_name}")
                    self._log_transaction(
                        transaction_id=transaction_id,
                        operation='DELETE',
                        record_id=game_id,
                        node_name=node_name,
                        old_data=old_data,
                        status='FAILED',
                        error_message='Game not found on node'
                    )
                else:
                    db.commit()
                    self._log_transaction(
                        transaction_id=transaction_id,
                        operation='DELETE',
                        record_id=game_id,
                        node_name=node_name,
                        old_data=old_data,
                        status='COMMITTED'
                    )
            except Exception as e:
                db.rollback()
                success = False
                self._log_transaction(
                    transaction_id=transaction_id,
                    operation='DELETE',
                    record_id=game_id,
                    node_name=node_name,
                    old_data=old_data,
                    status='FAILED',
                    error_message=str(e)
                )
                print(f"Error deleting game on {node_name}: {e}")
            finally:
                db.close()

        return success

    def retry_failed_transactions(self):
        """Retry failed or pending transactions when nodes become available."""
        db_central = get_database('node1')
        TransactionLog.bind_database(db_central)
        NodeStatus.bind_database(db_central)
        db_central.connect()

        pending_transactions = TransactionLog.select().where(
            ((TransactionLog.status == 'PENDING') | (TransactionLog.status == 'FAILED')) &
            (TransactionLog.processed == False)
        )

        for transaction in pending_transactions:
            node_name = {1: 'node1', 2: 'node2', 3: 'node3'}[transaction.node_id]
            node_status = NodeStatus.get(NodeStatus.node_id == transaction.node_id)

            if node_status.status == 'ONLINE':
                # Retry the transaction
                db_node = get_database(node_name)
                DimGame.bind_database(db_node)
                try:
                    db_node.connect()
                    db_node.execute_sql(f"SET TRANSACTION ISOLATION LEVEL {self.isolation_level}")
                    db_node.begin()

                    if transaction.operation == 'INSERT':
                        game_data = json.loads(transaction.new_data)
                        DimGame.create(**game_data)
                    elif transaction.operation == 'UPDATE':
                        game_data = json.loads(transaction.new_data)
                        query = DimGame.update(**game_data).where(DimGame.GameID == transaction.record_id)
                        query.execute()
                    elif transaction.operation == 'DELETE':
                        query = DimGame.delete().where(DimGame.GameID == transaction.record_id)
                        query.execute()

                    db_node.commit()
                    # Update transaction log
                    TransactionLog.update(
                        status='COMMITTED',
                        processed=True,
                        error_message=None
                    ).where(TransactionLog.log_id == transaction.log_id).execute()
                    print(f"Successfully retried transaction {transaction.transaction_id} on {node_name}")
                except Exception as e:
                    db_node.rollback()
                    # Update error message
                    TransactionLog.update(
                        error_message=str(e)
                    ).where(TransactionLog.log_id == transaction.log_id).execute()
                    print(f"Error retrying transaction {transaction.transaction_id} on {node_name}: {e}")
                finally:
                    db_node.close()

        db_central.close()
   
    def _update_node_status(self, node_id, status):
        """Update the status of a node in the NodeStatus table."""
        db_central = get_database('node1')  # Central node database
        NodeStatus.bind_database(db_central)
        try:
            db_central.connect()
            NodeStatus.update(
                status=status,
                last_checked=datetime.now()
            ).where(NodeStatus.node_id == node_id).execute()
        except Exception as e:
            print(f"Error updating node status for node {node_id}: {e}")
        finally:
            db_central.close()
