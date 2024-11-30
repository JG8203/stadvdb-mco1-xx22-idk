from peewee import *
from datetime import datetime

# Base model class
class BaseModel(Model):
    class Meta:
        database = None  # Will be assigned when database connection is established

# Main game data table
class GameData(BaseModel):
    AppID = IntegerField(primary_key=True)
    Name = CharField()
    ReleaseDate = DateTimeField(null=True)
    RequiredAge = IntegerField(default=0)
    Price = FloatField(default=0.0)
    DetailedDescription = TextField(null=True)
    AboutGame = TextField(null=True)
    ShortDescription = TextField(null=True)
    Website = CharField(null=True)
    HeaderImage = CharField(null=True)
    SupportURL = CharField(null=True)
    SupportEmail = CharField(null=True)
    Windows = BooleanField(default=False)
    Mac = BooleanField(default=False)
    Linux = BooleanField(default=False)
    MetacriticScore = IntegerField(default=0)
    MetacriticURL = CharField(null=True)
    Achievements = IntegerField(default=0)
    Recommendations = IntegerField(default=0)
    Notes = TextField(null=True)
    SupportedLanguages = TextField(null=True)  # Stored as comma-separated
    FullAudioLanguages = TextField(null=True)  # Stored as comma-separated
    Developers = TextField(null=True)  # Stored as comma-separated
    Publishers = TextField(null=True)  # Stored as comma-separated
    Categories = TextField(null=True)  # Stored as comma-separated
    Genres = TextField(null=True)  # Stored as comma-separated
    Screenshots = TextField(null=True)  # Stored as comma-separated URLs
    Movies = TextField(null=True)  # Stored as comma-separated URLs
    UserScore = FloatField(default=0.0)
    ScoreRank = CharField(null=True)
    PositiveReviews = IntegerField(default=0)
    NegativeReviews = IntegerField(default=0)
    EstimatedOwnersMin = IntegerField(default=0)
    EstimatedOwnersMax = IntegerField(default=0)
    AvgPlaytimeForever = IntegerField(default=0)
    AvgPlaytimeTwoWeeks = IntegerField(default=0)
    MedianPlaytimeForever = IntegerField(default=0)
    MedianPlaytimeTwoWeeks = IntegerField(default=0)
    PeakCCU = IntegerField(default=0)
    Tags = TextField(null=True)  # Stored as JSON string of tag:count pairs
    CreatedAt = DateTimeField(default=datetime.now)
    UpdatedAt = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.UpdatedAt = datetime.now()
        return super(GameData, self).save(*args, **kwargs)

    class Meta:
        table_name = 'games'

# Base model for pending tables
class BasePendingGame(BaseModel):
    AppID = IntegerField(primary_key=True)
    Name = CharField()
    ReleaseDate = DateTimeField(null=True)
    RequiredAge = IntegerField(default=0)
    Price = FloatField(default=0.0)
    DetailedDescription = TextField(null=True)
    AboutGame = TextField(null=True)
    ShortDescription = TextField(null=True)
    Website = CharField(null=True)
    HeaderImage = CharField(null=True)
    Windows = BooleanField(default=False)
    Mac = BooleanField(default=False)
    Linux = BooleanField(default=False)
    Developers = TextField(null=True)
    Publishers = TextField(null=True)
    Categories = TextField(null=True)
    Genres = TextField(null=True)
    Tags = TextField(null=True)
    SyncStatus = CharField()  # PENDING, SYNCED, FAILED
    CreatedAt = DateTimeField(default=datetime.now)
    LastSyncAttempt = DateTimeField(null=True)
    SyncRetries = IntegerField(default=0)
    ErrorMessage = TextField(null=True)

    class Meta:
        abstract = True

# Pending Windows games table
class PendingWindowsGames(BasePendingGame):
    class Meta:
        table_name = 'pending_windows_games'

    def increment_retry(self, error_message=None):
        self.SyncRetries += 1
        self.ErrorMessage = error_message
        self.LastSyncAttempt = datetime.now()
        self.save()

# Pending multi-platform games table
class PendingMultiOSGames(BasePendingGame):
    class Meta:
        table_name = 'pending_multi_os_games'

    def increment_retry(self, error_message=None):
        self.SyncRetries += 1
        self.ErrorMessage = error_message
        self.LastSyncAttempt = datetime.now()
        self.save()

# Node status tracking table
class NodeStatus(BaseModel):
    NodeName = CharField(unique=True)
    IsAvailable = BooleanField(default=True)
    LastChecked = DateTimeField(default=datetime.now)
    LastSync = DateTimeField(null=True)
    FailureCount = IntegerField(default=0)
    LastError = TextField(null=True)

    class Meta:
        table_name = 'node_status'

    @classmethod
    def update_status(cls, node_name, is_available, error=None):
        node, created = cls.get_or_create(NodeName=node_name)
        node.IsAvailable = is_available
        node.LastChecked = datetime.now()
        if not is_available:
            node.FailureCount += 1
            node.LastError = error
        else:
            node.FailureCount = 0
            node.LastError = None
        node.save()

# Sync history tracking table
class SyncHistory(BaseModel):
    SyncID = AutoField()
    GameID = IntegerField()
    NodeName = CharField()
    SyncType = CharField()  # WINDOWS, MULTI_OS
    Status = CharField()  # SUCCESS, FAILED
    AttemptedAt = DateTimeField(default=datetime.now)
    CompletedAt = DateTimeField(null=True)
    ErrorMessage = TextField(null=True)

    class Meta:
        table_name = 'sync_history'

    @classmethod
    def log_sync_attempt(cls, game_id, node_name, sync_type, status, error=None):
        return cls.create(
            GameID=game_id,
            NodeName=node_name,
            SyncType=sync_type,
            Status=status,
            CompletedAt=datetime.now() if status == 'SUCCESS' else None,
            ErrorMessage=error
        )
