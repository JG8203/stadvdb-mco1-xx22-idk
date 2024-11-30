from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import threading
from peewee import *
from services.db_manager import DatabaseManager
from services.write_coordinator import GameWriteCoordinator
from services.sync_service import GameSyncService
from models.models import GameData, PendingWindowsGames, PendingMultiOSGames

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
db_manager = DatabaseManager()
write_coordinator = GameWriteCoordinator(db_manager)
sync_service = GameSyncService(db_manager)

# Start sync service in background thread
sync_thread = threading.Thread(target=sync_service.start, daemon=True)
sync_thread.start()

def validate_game_data(data):
    """Validate incoming game data"""
    required_fields = [
        'name', 'release_date', 'required_age', 'price',
        'about_game', 'windows', 'mac', 'linux'
    ]
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Platform validation
    if not any([data.get('windows'), data.get('mac'), data.get('linux')]):
        errors.append("At least one platform must be selected")
    
    # Basic type validation
    if 'price' in data and not isinstance(data['price'], (int, float)):
        errors.append("Price must be a number")
        
    if 'required_age' in data and not isinstance(data['required_age'], int):
        errors.append("Required age must be an integer")
    
    return errors

@app.route('/api/games', methods=['POST'])
def create_game():
    """Create a new game"""
    if not db_manager.is_master_up():
        return jsonify({
            'error': 'Master node is down. No writes allowed.'
        }), 503

    data = request.json
    
    # Validate request data
    errors = validate_game_data(data)
    if errors:
        return jsonify({
            'error': 'Validation failed',
            'details': errors
        }), 400

    try:
        # Process the game creation through write coordinator
        result = write_coordinator.write_game(data)
        
        return jsonify({
            'message': 'Game created successfully',
            'data': result
        }), 201

    except Exception as e:
        logger.error(f"Error creating game: {str(e)}")
        return jsonify({
            'error': 'Failed to create game',
            'details': str(e)
        }), 500

@app.route('/api/nodes/crash/<node>', methods=['POST'])
def crash_node(node):
    """Simulate node crash"""
    if node not in ['master', 'slave_a', 'slave_b']:
        return jsonify({'error': 'Invalid node specified'}), 400
    
    try:
        db_manager.crash_node(node)
        return jsonify({'message': f'{node} node crashed successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to crash {node}: {str(e)}'}), 500

@app.route('/api/nodes/restore/<node>', methods=['POST'])
def restore_node(node):
    """Restore crashed node"""
    if node not in ['master', 'slave_a', 'slave_b']:
        return jsonify({'error': 'Invalid node specified'}), 400
    
    try:
        db_manager.restore_node(node)
        return jsonify({'message': f'{node} node restored successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to restore {node}: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check health status of all nodes"""
    return jsonify({
        'master': {
            'status': 'up' if db_manager.is_master_up() else 'down',
            'connection': db_manager.check_master_connection()
        },
        'slave_a': {
            'status': 'up' if db_manager.is_slave_a_up() else 'down',
            'connection': db_manager.check_slave_a_connection()
        },
        'slave_b': {
            'status': 'up' if db_manager.is_slave_b_up() else 'down',
            'connection': db_manager.check_slave_b_connection()
        }
    })

@app.route('/api/pending', methods=['GET'])
def get_pending_sync():
    """Get pending sync status"""
    try:
        pending_windows = PendingWindowsGames.select().where(
            PendingWindowsGames.SyncStatus.in_(['PENDING', 'FAILED'])
        ).count()
        
        pending_multi_os = PendingMultiOSGames.select().where(
            PendingMultiOSGames.SyncStatus.in_(['PENDING', 'FAILED'])
        ).count()
        
        return jsonify({
            'pending_windows_games': pending_windows,
            'pending_multi_os_games': pending_multi_os
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get pending sync status: {str(e)}'}), 500

@app.route('/api/games/sample', methods=['POST'])
def create_sample_game():
    """Create a sample game for testing"""
    sample_game = {
        'name': 'Sample Game',
        'release_date': datetime.now().isoformat(),
        'required_age': 0,
        'price': 9.99,
        'about_game': 'This is a sample game for testing.',
        'windows': True,
        'mac': False,
        'linux': False,
        'developers': ['Sample Developer'],
        'publishers': ['Sample Publisher'],
        'categories': ['Single-player'],
        'genres': ['Action'],
        'tags': {'Action': 10, 'Adventure': 5}
    }
    
    return create_game()

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create all necessary tables before starting
    db_manager.create_tables()
    
    # Start the Flask application
    app.run(debug=True, port=5000)
