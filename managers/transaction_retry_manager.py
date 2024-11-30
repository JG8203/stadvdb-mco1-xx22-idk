import threading
import time
from managers.transaction_manager import TransactionManager

class TransactionRetryManager:
    def __init__(self, check_interval=10):
        self.check_interval = check_interval  # Seconds
        self.transaction_manager = TransactionManager()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._retry_transactions, daemon=True).start()

    def stop(self):
        self.running = False

    def _retry_transactions(self):
        while self.running:
            self.transaction_manager.retry_failed_transactions()
            time.sleep(self.check_interval)
