from peewee import (
    Model, MySQLDatabase, AutoField, IntegerField, CharField, TextField, DateField,
    ForeignKeyField, BooleanField, DecimalField
)

# Database connection
db = MySQLDatabase(
    'games',
    user='admin',
    password='password',
    host='stadvb.chsuys826h4e.ap-southeast-2.rds.amazonaws.com',
    port=3306,
    charset='utf8mb4'
)

class BaseModel(Model):
    class Meta:
        database = db

# Dimension tables
class DimGame(BaseModel):
    GameID = AutoField()
    AppID = IntegerField(unique=True)
    Name = CharField()
    ReleaseDate = DateField(null=True)
    RequiredAge = IntegerField(null=True)
    AboutGame = TextField(null=True)
    Website = CharField(null=True)
    SupportURL = CharField(null=True)
    SupportEmail = CharField(null=True)
    HeaderImage = CharField(null=True)
    Notes = TextField(null=True)

    class Meta:
        table_name = 'Dim_Game'

class DimDeveloper(BaseModel):
    DeveloperID = AutoField()
    DeveloperName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Developer'

class DimPublisher(BaseModel):
    PublisherID = AutoField()
    PublisherName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Publisher'

class DimGenre(BaseModel):
    GenreID = AutoField()
    GenreName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Genre'

class DimCategory(BaseModel):
    CategoryID = AutoField()
    CategoryName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Category'

class DimPlatform(BaseModel):
    PlatformID = AutoField()
    PlatformName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Platform'

class DimLanguage(BaseModel):
    LanguageID = AutoField()
    LanguageName = CharField(unique=True)
    IsFullAudio = BooleanField(default=False)

    class Meta:
        table_name = 'Dim_Language'

class DimDate(BaseModel):
    DateID = IntegerField(primary_key=True)  # Using YYYYMMDD format as key
    Date = DateField()
    Day = IntegerField()
    Month = IntegerField()
    Quarter = IntegerField()
    Year = IntegerField()
    Weekday = CharField()

    class Meta:
        table_name = 'Dim_Date'

# Bridge tables (for many-to-many relationships)
class BridgeGameDeveloper(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='developers', on_delete='CASCADE')
    DeveloperID = ForeignKeyField(DimDeveloper, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Developer'
        primary_key = False
        indexes = (
            (('GameID', 'DeveloperID'), True),
        )

class BridgeGamePublisher(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='publishers', on_delete='CASCADE')
    PublisherID = ForeignKeyField(DimPublisher, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Publisher'
        primary_key = False
        indexes = (
            (('GameID', 'PublisherID'), True),
        )

class BridgeGameGenre(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='genres', on_delete='CASCADE')
    GenreID = ForeignKeyField(DimGenre, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Genre'
        primary_key = False
        indexes = (
            (('GameID', 'GenreID'), True),
        )

class BridgeGameCategory(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='categories', on_delete='CASCADE')
    CategoryID = ForeignKeyField(DimCategory, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Category'
        primary_key = False
        indexes = (
            (('GameID', 'CategoryID'), True),
        )

class BridgeGamePlatform(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='platforms', on_delete='CASCADE')
    PlatformID = ForeignKeyField(DimPlatform, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Platform'
        primary_key = False
        indexes = (
            (('GameID', 'PlatformID'), True),
        )

class BridgeGameLanguage(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='languages', on_delete='CASCADE')
    LanguageID = ForeignKeyField(DimLanguage, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Language'
        primary_key = False
        indexes = (
            (('GameID', 'LanguageID'), True),
        )

# Fact table
class FactGameMetrics(BaseModel):
    FactID = AutoField()
    GameID = ForeignKeyField(DimGame, backref='metrics', on_delete='CASCADE')
    DateID = ForeignKeyField(DimDate, backref='metrics', on_delete='CASCADE')
    Price = DecimalField(max_digits=10, decimal_places=2, null=True)
    Discount = DecimalField(max_digits=5, decimal_places=2, null=True)
    EstimatedOwners = IntegerField(null=True)
    PeakCCU = IntegerField(null=True)
    AvgPlaytimeForever = IntegerField(null=True)
    AvgPlaytimeTwoWeeks = IntegerField(null=True)
    MedianPlaytimeForever = IntegerField(null=True)
    MedianPlaytimeTwoWeeks = IntegerField(null=True)
    PositiveReviews = IntegerField(null=True)
    NegativeReviews = IntegerField(null=True)
    MetacriticScore = IntegerField(null=True)
    UserScore = DecimalField(max_digits=3, decimal_places=1, null=True)

    class Meta:
        table_name = 'Fact_GameMetrics'

