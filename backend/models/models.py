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
    Reviews = TextField(null=True)
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
    Tags = TextField(null=True)
    CreatedAt = DateTimeField(default=datetime.now)
    UpdatedAt = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.UpdatedAt = datetime.now()
        return super(GameData, self).save(*args, **kwargs)

    class Meta:
        table_name = 'games'

class BasePendingGame(BaseModel):
    AppID = IntegerField(primary_key=True)
    Name = CharField()
    ReleaseDate = DateTimeField(null=True)
    RequiredAge = IntegerField(default=0)
    Price = FloatField(default=0.0)
    DetailedDescription = TextField(null=True)
    AboutGame = TextField(null=True)
    ShortDescription = TextField(null=True)
    Reviews = TextField(null=True)
    Website = CharField(null=True)
    SupportURL = CharField(null=True)
    SupportEmail = CharField(null=True)
    HeaderImage = CharField(null=True)
    Windows = BooleanField(default=False)
    Mac = BooleanField(default=False)
    Linux = BooleanField(default=False)
    MetacriticScore = IntegerField(default=0)
    MetacriticURL = CharField(null=True)
    Achievements = IntegerField(default=0)
    Recommendations = IntegerField(default=0)
    Notes = TextField(null=True)
    SupportedLanguages = TextField(null=True)
    FullAudioLanguages = TextField(null=True)
    Developers = TextField(null=True)
    Publishers = TextField(null=True)
    Categories = TextField(null=True)
    Genres = TextField(null=True)
    Screenshots = TextField(null=True)
    Movies = TextField(null=True)
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
    Tags = TextField(null=True)

    # Pending-specific fields
    SyncStatus = CharField(null=False, default='PENDING')  # PENDING, SYNCED, FAILED
    CreatedAt = DateTimeField(default=datetime.now)
    LastSyncAttempt = DateTimeField(null=True)
    SyncRetries = IntegerField(default=0)
    ErrorMessage = TextField(null=True)

    class Meta:
        abstract = True

    def increment_retry(self, error_message=None):
        """Increment the retry count and update sync attempt timestamp"""
        self.SyncRetries += 1
        self.ErrorMessage = error_message
        self.LastSyncAttempt = datetime.now()
        self.save()

# Pending Windows games table
class PendingWindowsGames(BasePendingGame):
    class Meta:
        table_name = 'pending_windows_games'

# Pending multi-platform games table
class PendingMultiOSGames(BasePendingGame):
    class Meta:
        table_name = 'pending_multi_os_games'

