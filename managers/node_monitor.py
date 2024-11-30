import threading
import time
from db import get_database
from models.node_status import NodeStatus
from peewee import OperationalError

class NodeMonitor:
    def __init__(self, check_interval=5):
        self.check_interval = check_interval  # Seconds
        self.nodes = ['node1', 'node2', 'node3']
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._monitor_nodes, daemon=True).start()

    def stop(self):
        self.running = False

    def _monitor_nodes(self):
        while self.running:
            for idx, node_name in enumerate(self.nodes, start=1):
                self._check_node_status(node_name, idx)
            time.sleep(self.check_interval)

    def _check_node_status(self, node_name, node_id):
        try:
            db_node = get_database(node_name)
            try:
                db_node.connect()
                node_status = 'ONLINE'
                db_node.close()
            except OperationalError:
                node_status = 'OFFLINE'

            # Try to update status in central node
            db_central = get_database('node1')
            try:
                NodeStatus.bind_database(db_central)
                db_central.connect()
                NodeStatus.update(
                    status=node_status,
                    last_checked=time.strftime('%Y-%m-%d %H:%M:%S')
                ).where(NodeStatus.node_id == node_id).execute()
                db_central.close()
            except OperationalError:
                # Central node is down, log to console
                print(f"Central node (node1) is offline. Status of {node_name}: {node_status}")
        except Exception as e:
            print(f"Error monitoring node {node_name}: {e}")

