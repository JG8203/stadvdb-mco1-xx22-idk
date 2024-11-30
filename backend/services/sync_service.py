import time
import logging
from datetime import datetime
from peewee import *
from models.models import GameData, PendingWindowsGames, PendingMultiOSGames
from peewee import OperationalError

class GameSyncService:
    def __init__(self, db_manager, sync_interval=10):  # sync_interval in seconds
        self.db_manager = db_manager
        self.sync_interval = sync_interval
        self.logger = logging.getLogger(__name__)
        self.is_running = False

    def start(self):
        """Start the sync service"""
        self.logger.info("Starting Game Sync Service...")
        self.is_running = True

        while self.is_running:
            try:
                if self.db_manager.is_master_up():
                    self.sync_all()
                else:
                    self.logger.warning("Master node is down, skipping sync cycle")

                time.sleep(self.sync_interval)
            except Exception as e:
                self.logger.error(f"Error in sync cycle: {str(e)}")
                time.sleep(self.sync_interval)

    def stop(self):
        """Stop the sync service"""
        self.logger.info("Stopping Game Sync Service...")
        self.is_running = False

    def sync_all(self):
        """Sync all pending games to their respective nodes"""
        # Sync Windows-only games if Slave A is up
        if self.db_manager.is_slave_a_up():
            self.sync_windows_games()
        else:
            self.logger.info("Slave A is down, cannot sync Windows games.")

        # Sync multi-platform games if Slave B is up
        if self.db_manager.is_slave_b_up():
            self.sync_multi_platform_games()
        else:
            self.logger.info("Slave B is down, cannot sync Multi-platform games.")

    def sync_windows_games(self):
        """Sync pending Windows-only games to Slave A"""
        try:
            # Get pending Windows games
            pending_games = (PendingWindowsGames
                           .select()
                           .where(
                               (PendingWindowsGames.SyncStatus == 'PENDING') |
                               (PendingWindowsGames.SyncStatus == 'FAILED')
                           )
                           .order_by(PendingWindowsGames.CreatedAt))

            for game in pending_games:
                try:
                    self.logger.info(f"Attempting to sync Windows game: {game.Name} (ID: {game.AppID})")

                    # Get Slave A connection
                    slave_a_db = self.db_manager.get_connection('slave_a')
                    if slave_a_db is None:
                        raise Exception("Slave A is down.")

                    # Set the database for GameData model
                    GameData._meta.database = slave_a_db

                    # Check if game already exists in slave_a
                    existing_game = GameData.select().where(GameData.AppID == game.AppID).exists()

                    if not existing_game:
                        # Prepare game data
                        game_data = self._prepare_game_data(game)

                        # Write to Slave A
                        with slave_a_db.atomic():
                            GameData.create(**game_data)

                        # Update sync status
                        game.SyncStatus = 'SYNCED'
                        game.LastSyncAttempt = datetime.now()
                        game.save()

                        self.logger.info(f"Successfully synced Windows game: {game.Name} (ID: {game.AppID})")
                    else:
                        game.SyncStatus = 'SYNCED'
                        game.LastSyncAttempt = datetime.now()
                        game.save()
                        self.logger.info(f"Game already exists in Slave A: {game.Name} (ID: {game.AppID})")

                except Exception as e:
                    self.logger.error(f"Failed to sync Windows game {game.Name} (ID: {game.AppID}): {str(e)}")
                    game.SyncStatus = 'FAILED'
                    game.LastSyncAttempt = datetime.now()
                    game.save()

        except Exception as e:
            self.logger.error(f"Error in Windows games sync process: {str(e)}")

    def sync_multi_platform_games(self):
        """Sync pending multi-platform games to Slave B"""
        try:
            # Get pending multi-platform games
            pending_games = (PendingMultiOSGames
                           .select()
                           .where(
                               (PendingMultiOSGames.SyncStatus == 'PENDING') |
                               (PendingMultiOSGames.SyncStatus == 'FAILED')
                           )
                           .order_by(PendingMultiOSGames.CreatedAt))

            for game in pending_games:
                try:
                    self.logger.info(f"Attempting to sync Multi-platform game: {game.Name} (ID: {game.AppID})")

                    # Get Slave B connection
                    slave_b_db = self.db_manager.get_connection('slave_b')
                    if slave_b_db is None:
                        raise Exception("Slave B is down.")

                    # Set the database for GameData model
                    GameData._meta.database = slave_b_db

                    # Check if game already exists in slave_b
                    existing_game = GameData.select().where(GameData.AppID == game.AppID).exists()

                    if not existing_game:
                        # Prepare game data
                        game_data = self._prepare_game_data(game)

                        # Write to Slave B
                        with slave_b_db.atomic():
                            GameData.create(**game_data)

                        # Update sync status
                        game.SyncStatus = 'SYNCED'
                        game.LastSyncAttempt = datetime.now()
                        game.save()

                        self.logger.info(f"Successfully synced Multi-platform game: {game.Name} (ID: {game.AppID})")
                    else:
                        game.SyncStatus = 'SYNCED'
                        game.LastSyncAttempt = datetime.now()
                        game.save()
                        self.logger.info(f"Game already exists in Slave B: {game.Name} (ID: {game.AppID})")

                except Exception as e:
                    self.logger.error(f"Failed to sync Multi-platform game {game.Name} (ID: {game.AppID}): {str(e)}")
                    game.SyncStatus = 'FAILED'
                    game.LastSyncAttempt = datetime.now()
                    game.save()

        except Exception as e:
            self.logger.error(f"Error in Multi-platform games sync process: {str(e)}")

    def _prepare_game_data(self, game):
        """Prepare game data for insertion"""
        return {
            'AppID': game.AppID,
            'Name': game.Name,
            'ReleaseDate': game.ReleaseDate,
            'RequiredAge': game.RequiredAge,
            'Price': game.Price,
            'DetailedDescription': game.DetailedDescription,
            'AboutGame': game.AboutGame,
            'ShortDescription': game.ShortDescription,
            'Website': game.Website,
            'HeaderImage': game.HeaderImage,
            'Windows': game.Windows,
            'Mac': game.Mac,
            'Linux': game.Linux,
            'Developers': game.Developers,
            'Publishers': game.Publishers,
            'Categories': game.Categories,
            'Genres': game.Genres,
            'Tags': game.Tags
        }

    def get_sync_status(self):
        """Get current sync status"""
        try:
            pending_windows = PendingWindowsGames.select().where(
                PendingWindowsGames.SyncStatus.in_(['PENDING', 'FAILED'])
            ).count()

            pending_multi_os = PendingMultiOSGames.select().where(
                PendingMultiOSGames.SyncStatus.in_(['PENDING', 'FAILED'])
            ).count()

            return {
                'pending_windows_games': pending_windows,
                'pending_multi_os_games': pending_multi_os,
                'last_sync_attempt': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting sync status: {str(e)}")
            return None
