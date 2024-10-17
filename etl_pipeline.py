from models.models import (
    DimGame,
    DimDeveloper,
    DimPublisher,
    DimGenre,
    DimCategory,
    DimPlatform,
    DimLanguage,
    DimDate,
    BridgeGameDeveloper,
    BridgeGamePublisher,
    BridgeGameGenre,
    BridgeGameCategory,
    BridgeGamePlatform,
    BridgeGameLanguage,
    FactGameMetrics,
    db
)

def test_connection():
    try:
        db.connect()
        print("Connected to MySQL database!")
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    test_connection()

