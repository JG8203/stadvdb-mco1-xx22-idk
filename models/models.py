from peewee import (
    Model,
    MySQLDatabase,
    AutoField,
    IntegerField,
    CharField,
    TextField,
    DateField,
    ForeignKeyField,
    BooleanField,
    DecimalField,
)

db = MySQLDatabase(
    database='games',
    user='admin',
    password='password',
    host='localhost',
    port=3306,
    charset='utf8mb4'
)

class BaseModel(Model):
    class Meta:
        database = db

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
    Windows = BooleanField()
    Mac = BooleanField()
    Linux = BooleanField()

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

class DimLanguage(BaseModel):
    LanguageID = AutoField()
    LanguageName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Language'

class DimTag(BaseModel):
    TagID = AutoField()
    TagName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Tag'

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

class BridgeGameLanguage(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='languages', on_delete='CASCADE')
    LanguageID = ForeignKeyField(DimLanguage, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Language'
        primary_key = False
        indexes = (
            (('GameID', 'LanguageID'), True),
        )

class DimTag(BaseModel):
    TagID = AutoField()
    TagName = CharField(unique=True)

    class Meta:
        table_name = 'Dim_Tag'

class BridgeGameTag(BaseModel):
    GameID = ForeignKeyField(DimGame, backref='tags', on_delete='CASCADE')
    TagID = ForeignKeyField(DimTag, backref='games', on_delete='CASCADE')

    class Meta:
        table_name = 'Bridge_Game_Tag'
        primary_key = False
        indexes = (
            (('GameID', 'TagID'), True),
        )

class FactGameMetrics(BaseModel):
    FactID = AutoField()
    GameID = ForeignKeyField(DimGame, backref='metrics', on_delete='CASCADE')
    Price = DecimalField(max_digits=10, decimal_places=2, null=True)
    EstimatedOwners = IntegerField(null=True)
    PeakCCU = IntegerField(null=True)
    AvgPlaytimeForever = IntegerField(null=True)
    AvgPlaytimeTwoWeeks = IntegerField(null=True)
    MedianPlaytimeForever = IntegerField(null=True)
    MedianPlaytimeTwoWeeks = IntegerField(null=True)
    PositiveReviews = IntegerField(null=True)
    NegativeReviews = IntegerField(null=True)
    MetacriticScore = IntegerField(null=True)
    UserScore = DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        table_name = 'Fact_GameMetrics'
