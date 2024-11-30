import logging
from datetime import datetime
from peewee import *
from models.models import GameData, PendingWindowsGames, PendingMultiOSGames
from peewee import OperationalError

class GameWriteCoordinator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def write_game(self, game_data):
        """Main method to handle game creation and routing"""
        if not self.db_manager.is_master_up():
            raise Exception("Master node is down. Cannot process writes.")

        try:
            # Generate new AppID
            new_app_id = self._generate_app_id()
            game_data['app_id'] = new_app_id

            # Prepare game data for insertion
            processed_data = self._prepare_game_data(game_data)

            # Determine target nodes based on platform
            windows_only = game_data.get('windows', False) and not (game_data.get('mac', False) or game_data.get('linux', False))
            multi_platform = game_data.get('windows', False) and (game_data.get('mac', False) or game_data.get('linux', False))

            # Always write to master first
            master_game = self._write_to_master(processed_data)

            if windows_only:
                self._handle_windows_write(processed_data)
            elif multi_platform:
                self._handle_multiplatform_write(processed_data)

            return {
                'AppID': master_game.AppID,
                'Name': master_game.Name,
                'ReleaseDate': master_game.ReleaseDate.isoformat() if master_game.ReleaseDate else None,
                'RequiredAge': master_game.RequiredAge,
                'Price': float(master_game.Price),
                'AboutGame': master_game.AboutGame,
                'Website': master_game.Website,
                'HeaderImage': master_game.HeaderImage,
                'Windows': master_game.Windows,
                'Mac': master_game.Mac,
                'Linux': master_game.Linux,
                'Developers': master_game.Developers.split(',') if master_game.Developers else [],
                'Publishers': master_game.Publishers.split(',') if master_game.Publishers else [],
                'Categories': master_game.Categories.split(',') if master_game.Categories else [],
                'Genres': master_game.Genres.split(',') if master_game.Genres else []
            }

        except Exception as e:
            self.logger.error(f"Error in write operation: {str(e)}")
            raise

    def _generate_app_id(self):
        """Generate a new unique AppID using master node"""
        try:
            if not self.db_manager.is_master_up():
                raise Exception("Master node is down. Cannot generate AppID.")

            GameData._meta.database = self.db_manager.master_db
            max_id = GameData.select(fn.MAX(GameData.AppID)).scalar() or 0
            new_id = max_id + 1

            return new_id
        except OperationalError as e:
            self.logger.error(f"Cannot connect to master database: {str(e)}")
            raise Exception("Cannot generate AppID because the master node is down.")
        except Exception as e:
            self.logger.error(f"Unexpected error generating AppID: {str(e)}")
            raise

    def _prepare_game_data(self, data):
        """Prepare game data for database insertion"""
        return {
            'AppID': data.get('app_id'),
            'Name': data['name'],
            'ReleaseDate': datetime.fromisoformat(data['release_date']) if isinstance(data['release_date'], str) else data['release_date'],
            'RequiredAge': data.get('required_age', 0),
            'Price': data.get('price', 0.0),
            'DetailedDescription': data.get('detailed_description', ''),
            'AboutGame': data.get('about_game', ''),
            'ShortDescription': data.get('short_description', ''),
            'Reviews': data.get('reviews', ''),
            'Website': data.get('website', ''),
            'SupportURL': data.get('support_url', ''),
            'SupportEmail': data.get('support_email', ''),
            'HeaderImage': data.get('header_image', ''),
            'Windows': data.get('windows', False),
            'Mac': data.get('mac', False),
            'Linux': data.get('linux', False),
            'MetacriticScore': data.get('metacritic_score', 0),
            'MetacriticURL': data.get('metacritic_url', ''),
            'Achievements': data.get('achievements', 0),
            'Recommendations': data.get('recommendations', 0),
            'Notes': data.get('notes', ''),
            'SupportedLanguages': ','.join(data.get('supported_languages', [])),
            'FullAudioLanguages': ','.join(data.get('full_audio_languages', [])),
            'Developers': ','.join(data.get('developers', [])),
            'Publishers': ','.join(data.get('publishers', [])),
            'Categories': ','.join(data.get('categories', [])),
            'Genres': ','.join(data.get('genres', [])),
            'Screenshots': ','.join(data.get('screenshots', [])),
            'Movies': ','.join(data.get('movies', [])),
            'UserScore': data.get('user_score', 0.0),
            'ScoreRank': data.get('score_rank', ''),
            'PositiveReviews': data.get('positive', 0),
            'NegativeReviews': data.get('negative', 0),
            'EstimatedOwnersMin': data.get('estimated_owners_min', 0),
            'EstimatedOwnersMax': data.get('estimated_owners_max', 0),
            'AvgPlaytimeForever': data.get('average_playtime_forever', 0),
            'AvgPlaytimeTwoWeeks': data.get('average_playtime_2weeks', 0),
            'MedianPlaytimeForever': data.get('median_playtime_forever', 0),
            'MedianPlaytimeTwoWeeks': data.get('median_playtime_2weeks', 0),
            'PeakCCU': data.get('peak_ccu', 0),
            'Tags': str(data.get('tags', {}))  # Convert dict to string
        }

    def _write_to_master(self, game_data):
        """Write game data to master node with verification"""
        try:
            GameData._meta.database = self.db_manager.master_db
            game = GameData.create(**game_data)

            # Verify the write
            if self._verify_write(self.db_manager.master_db, game_data['AppID']):
                self.logger.info(f"Successfully verified write to master for game {game_data['Name']} (ID: {game_data['AppID']})")
                return game
            else:
                raise Exception("Write verification failed")
        except IntegrityError:
            # If we hit a duplicate key, try with a new ID
            game_data['AppID'] = self._generate_app_id()
            return self._write_to_master(game_data)
        except OperationalError as e:
            self.logger.error(f"Master node is down: {str(e)}")
            raise Exception("Master node is down. Cannot write data.")
        except Exception as e:
            self.logger.error(f"Failed to write to master: {str(e)}")
            raise

    def _verify_write(self, db, app_id):
        """Verify that game data was successfully written to the database"""
        try:
            GameData._meta.database = db
            game = GameData.get_or_none(GameData.AppID == app_id)
            return game is not None
        except Exception as e:
            self.logger.error(f"Error verifying write: {str(e)}")
            return False

    def _write_to_slave(self, db, game_data):
        """Write game data to slave node with verification"""
        if db is None:
            self.logger.info("Slave node is down, cannot write data.")
            return False

        try:
            GameData._meta.database = db

            if not GameData.select().where(GameData.AppID == game_data['AppID']).exists():
                game = GameData.create(**game_data)
                # Verify the write
                if self._verify_write(db, game_data['AppID']):
                    self.logger.info(f"Successfully verified write to slave for game {game_data['Name']} (ID: {game_data['AppID']})")
                    return True
                else:
                    self.logger.error(f"Write verification failed for slave node")
                    return False
            else:
                self.logger.warning(f"Game {game_data['AppID']} already exists in slave node")
                return True  # Already exists means it's effectively written

        except OperationalError as e:
            self.logger.error(f"Failed to write to slave node: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error writing to slave: {str(e)}")
            return False

    def _handle_windows_write(self, game_data):
        slave_a_db = self.db_manager.get_connection('slave_a')
        if slave_a_db is not None:
            success = self._write_to_slave(slave_a_db, game_data)
            if not success:
                self._store_in_pending_windows(game_data)
        else:
            # Node is down, store in pending table
            self._store_in_pending_windows(game_data)
            self.logger.info(f"Slave A is down, stored game {game_data['Name']} in pending table")

    def _handle_multiplatform_write(self, game_data):
        """Handle write operation for multi-platform games with verification"""
        slave_b_db = self.db_manager.get_connection('slave_b')
        if slave_b_db is not None:
            success = self._write_to_slave(slave_b_db, game_data)
            if not success:
                self._store_in_pending_multiplatform(game_data)
        else:
            self.logger.info(f"Slave B is down, storing game {game_data['Name']} in pending table")
            self._store_in_pending_multiplatform(game_data)

    def _store_in_pending_windows(self, game_data):
        try:
            # Ensure we're using master database
            PendingWindowsGames._meta.database = self.db_manager.master_db

            # Check if entry already exists
            existing = PendingWindowsGames.get_or_none(PendingWindowsGames.AppID == game_data['AppID'])

            if existing:
                # Update existing entry
                existing.SyncStatus = 'PENDING'
                existing.LastSyncAttempt = None
                existing.SyncRetries = 0
                existing.ErrorMessage = None
                existing.save()
                self.logger.info(f"Updated existing pending Windows game: {game_data['Name']}")
            else:
                # Create new pending entry with all fields matching GameData
                pending_data = game_data.copy()
                # Add pending-specific fields
                pending_data.update({
                    'SyncStatus': 'PENDING',
                    'LastSyncAttempt': None,
                    'SyncRetries': 0,
                    'ErrorMessage': None,
                    'CreatedAt': datetime.now()
                })

                # Create new pending entry
                PendingWindowsGames.create(**pending_data)
                self.logger.info(f"Successfully stored Windows game in pending table: {game_data['Name']}")

        except Exception as e:
            self.logger.error(f"Failed to store in pending Windows table: {str(e)}")
            raise Exception(f"Failed to store game in pending table: {str(e)}")

    def _store_in_pending_multiplatform(self, game_data):
        try:
            # Ensure we're using master database
            PendingMultiOSGames._meta.database = self.db_manager.master_db

            # Check if entry already exists
            existing = PendingMultiOSGames.get_or_none(PendingMultiOSGames.AppID == game_data['AppID'])

            if existing:
                # Update existing entry
                existing.SyncStatus = 'PENDING'
                existing.LastSyncAttempt = None
                existing.SyncRetries = 0
                existing.ErrorMessage = None
                existing.save()
                self.logger.info(f"Updated existing pending Multi-platform game: {game_data['Name']}")
            else:
                # Create new pending entry with all fields matching GameData
                pending_data = game_data.copy()
                # Add pending-specific fields
                pending_data.update({
                    'SyncStatus': 'PENDING',
                    'LastSyncAttempt': None,
                    'SyncRetries': 0,
                    'ErrorMessage': None,
                    'CreatedAt': datetime.now()
                })

                # Create new pending entry
                PendingMultiOSGames.create(**pending_data)
                self.logger.info(f"Successfully stored Multi-platform game in pending table: {game_data['Name']}")

        except Exception as e:
            self.logger.error(f"Failed to store in pending Multi-platform table: {str(e)}")
            raise Exception(f"Failed to store game in pending table: {str(e)}")
