import React, { useState, useEffect } from 'react';
import { 
  AlertCircle, 
  CheckCircle, 
  RefreshCw, 
  Plus, 
  Settings,
  AlertTriangle,
  Server,
  Database,
  Zap,
  Shield,
  Clock,
  Trash2,
  Edit2,
  X,
  List,
  Filter,
  Search
} from 'lucide-react';

const DatabaseInterface = () => {
  const [healthStatus, setHealthStatus] = useState({});
  const [pendingSync, setPendingSync] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [showGameForm, setShowGameForm] = useState(false);
  const [selectedGameId, setSelectedGameId] = useState(null);
  const [games, setGames] = useState([]);
  const [selectedNode, setSelectedNode] = useState('slave_a');

  const [gameFormData, setGameFormData] = useState({
    name: '',
    release_date: new Date().toISOString().split('T')[0],
    required_age: 0,
    price: 0,
    about_game: '',
    windows: false,
    mac: false,
    linux: false,
    developers: [''],
    publishers: [''],
    categories: [''],
    genres: [''],
    tags: {}
  });

  useEffect(() => {
    fetchHealthStatus();
    fetchPendingSync();
    const interval = setInterval(() => {
      fetchHealthStatus();
      fetchPendingSync();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchHealthStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/health');
      const data = await response.json();
      setHealthStatus(data);
    } catch (error) {
      console.error('Failed to fetch health status:', error);
    }
  };

  const fetchPendingSync = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/pending');
      const data = await response.json();
      setPendingSync(data);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch pending sync:', error);
      setIsLoading(false);
    }
  };

  const handleCrashNode = async (node) => {
    try {
      await fetch(`http://localhost:5000/api/nodes/crash/${node}`, {
        method: 'POST'
      });
      fetchHealthStatus();
    } catch (error) {
      console.error(`Failed to crash ${node}:`, error);
    }
  };

  const handleRestoreNode = async (node) => {
    try {
      await fetch(`http://localhost:5000/api/nodes/restore/${node}`, {
        method: 'POST'
      });
      fetchHealthStatus();
    } catch (error) {
      console.error(`Failed to restore ${node}:`, error);
    }
  };

  const handleCreateGame = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/api/games', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gameFormData)
      });
      const data = await response.json();
      if (response.ok) {
        setShowGameForm(false);
        setGameFormData({
          name: '',
          release_date: new Date().toISOString().split('T')[0],
          required_age: 0,
          price: 0,
          about_game: '',
          windows: false,
          mac: false,
          linux: false,
          developers: [''],
          publishers: [''],
          categories: [''],
          genres: [''],
          tags: {}
        });
      } else {
        alert(data.error);
      }
    } catch (error) {
      console.error('Failed to create game:', error);
    }
  };

  const createSampleGame = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/games/sample', {
        method: 'POST'
      });
      if (response.ok) {
        alert('Sample game created successfully');
      } else {
        alert('Failed to create sample game');
      }
    } catch (error) {
      console.error('Failed to create sample game:', error);
    }
  };

  const GameDetails = ({ gameId, onClose }) => {
    const [gameData, setGameData] = useState(null);
    const [selectedNode, setSelectedNode] = useState('slave_a');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
  
    const fetchGameData = async (node) => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:5000/api/games/${gameId}?node=${node}`);
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || 'Failed to fetch game data');
        }
        const data = await response.json();
        setGameData(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
  
    useEffect(() => {
      fetchGameData(selectedNode);
    }, [gameId, selectedNode]);
  
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div className="bg-white p-6 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold">Game Details</h3>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-100 rounded-full"
            >
              <X size={20} />
            </button>
          </div>
  
          <div className="mb-4">
            <div className="flex gap-2 mb-4">
              {['master', 'slave_a', 'slave_b'].map((node) => (
                <button
                  key={node}
                  onClick={() => setSelectedNode(node)}
                  className={`px-3 py-1.5 rounded ${
                    selectedNode === node
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {node === 'slave_a' ? 'Windows Node' : 
                   node === 'slave_b' ? 'Multi-OS Node' : 
                   'Master Node'}
                </button>
              ))}
            </div>
  
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : error ? (
              <div className="text-red-500 py-4">{error}</div>
            ) : gameData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold">Basic Information</h4>
                    <div className="mt-2 space-y-2">
                      <p><span className="font-medium">Name:</span> {gameData.Name}</p>
                      <p><span className="font-medium">Release Date:</span> {gameData.ReleaseDate}</p>
                      <p><span className="font-medium">Required Age:</span> {gameData.RequiredAge}+</p>
                      <p><span className="font-medium">Price:</span> ${gameData.Price.toFixed(2)}</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold">Platform Support</h4>
                    <div className="mt-2 space-y-2">
                      <p>
                        <span className="font-medium">Windows:</span>
                        {gameData.Windows ? ' ✓' : ' ✗'}
                      </p>
                      <p>
                        <span className="font-medium">Mac:</span>
                        {gameData.Mac ? ' ✓' : ' ✗'}
                      </p>
                      <p>
                        <span className="font-medium">Linux:</span>
                        {gameData.Linux ? ' ✓' : ' ✗'}
                      </p>
                    </div>
                  </div>
                </div>
  
                <div>
                  <h4 className="font-semibold">About</h4>
                  <p className="mt-2 text-gray-700">{gameData.AboutGame}</p>
                </div>
  
                {gameData.Website && (
                  <div>
                    <h4 className="font-semibold">Website</h4>
                    <a 
                      href={gameData.Website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      {gameData.Website}
                    </a>
                  </div>
                )}
  
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold">Developers</h4>
                    <ul className="mt-2 list-disc list-inside">
                      {gameData.Developers.map((dev, index) => (
                        <li key={index}>{dev}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold">Publishers</h4>
                    <ul className="mt-2 list-disc list-inside">
                      {gameData.Publishers.map((pub, index) => (
                        <li key={index}>{pub}</li>
                      ))}
                    </ul>
                  </div>
                </div>
  
                <div>
                  <h4 className="font-semibold">Categories</h4>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {gameData.Categories.map((category, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 bg-gray-100 rounded-full text-sm"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
  
                <div>
                  <h4 className="font-semibold">Genres</h4>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {gameData.Genres.map((genre, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                      >
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>
  
                {Object.keys(gameData.Tags).length > 0 && (
                  <div>
                    <h4 className="font-semibold">Tags</h4>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {Object.entries(gameData.Tags).map(([tag, count], index) => (
                        <span 
                          key={index}
                          className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                        >
                          {tag} ({count})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    );
  };

  const NodeCard = ({ name, nodeKey }) => {
    const status = healthStatus[nodeKey]?.status === 'up' ? 'healthy' : 'error';
    
    return (
      <div className="p-6 border rounded-lg shadow-sm bg-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Server className="text-blue-500" size={24} />
            <div>
              <h3 className="text-lg font-semibold capitalize">{name}</h3>
              <p className="text-sm text-gray-500">Status: {healthStatus[nodeKey]?.status || 'Unknown'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {status === 'healthy' ? (
              <CheckCircle className="text-green-500" size={20} />
            ) : (
              <AlertCircle className="text-red-500" size={20} />
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={() => handleCrashNode(nodeKey)}
            className="px-3 py-1.5 text-sm bg-red-50 text-red-600 rounded-md hover:bg-red-100 flex items-center gap-2"
          >
            <Zap size={14} />
            Crash
          </button>
          <button 
            onClick={() => handleRestoreNode(nodeKey)}
            className="px-3 py-1.5 text-sm bg-green-50 text-green-600 rounded-md hover:bg-green-100 flex items-center gap-2"
          >
            <RefreshCw size={14} />
            Restore
          </button>
        </div>
      </div>
    );
  };

  const SyncStatus = ({ title, data }) => (
    <div className="p-6 border rounded-lg bg-white">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Database size={20} />
        {title}
      </h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            <span className="text-sm text-gray-600">Pending Creates</span>
          </div>
          <span className="font-semibold">{data.creates || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            <span className="text-sm text-gray-600">Pending Updates</span>
          </div>
          <span className="font-semibold">{data.updates || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            <span className="text-sm text-gray-600">Pending Deletes</span>
          </div>
          <span className="font-semibold">{data.deletes || 0}</span>
        </div>
      </div>
    </div>
  );

  const GameForm = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg w-full max-w-xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Create New Game</h3>
          <button
            onClick={() => setShowGameForm(false)}
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <X size={20} />
          </button>
        </div>
        
        <form onSubmit={handleCreateGame} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input
              type="text"
              value={gameFormData.name}
              onChange={(e) => setGameFormData({...gameFormData, name: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Release Date</label>
            <input
              type="date"
              value={gameFormData.release_date}
              onChange={(e) => setGameFormData({...gameFormData, release_date: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Required Age</label>
            <input
              type="number"
              value={gameFormData.required_age}
              onChange={(e) => setGameFormData({...gameFormData, required_age: parseInt(e.target.value)})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Price</label>
            <input
              type="number"
              step="0.01"
              value={gameFormData.price}
              onChange={(e) => setGameFormData({...gameFormData, price: parseFloat(e.target.value)})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">About Game</label>
            <textarea
              value={gameFormData.about_game}
              onChange={(e) => setGameFormData({...gameFormData, about_game: e.target.value})}
              className="w-full p-2 border rounded h-32"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Platform Support</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={gameFormData.windows}
                  onChange={(e) => setGameFormData({...gameFormData, windows: e.target.checked})}
                />
                Windows
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={gameFormData.mac}
                  onChange={(e) => setGameFormData({...gameFormData, mac: e.target.checked})}
                />
                Mac
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={gameFormData.linux}
                  onChange={(e) => setGameFormData({...gameFormData, linux: e.target.checked})}
                />
                Linux
              </label>
            </div>
          </div>
          <div className="flex gap-2 pt-4">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Create Game
            </button>
            <button
              type="button"
              onClick={() => setShowGameForm(false)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center gap-2">
          <RefreshCw className="animate-spin" size={20} />
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Database Management System</h1>
          <div className="flex items-center gap-2 text-gray-500">
            <Shield size={16} />
            <span>Master Node Status: {healthStatus.master?.status || 'Unknown'}</span>
            <span className="mx-2">•</span>
            <Clock size={16} />
            <span>Last Sync: Just now</span>
          </div>
        </header>

        {/* Game Management Buttons */}
        <div className="mb-8 flex justify-between items-center">
          <button
            onClick={() => setShowGameForm(true)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
          >
            <Plus size={16} />
            Create New Game
          </button>
          <button
            onClick={createSampleGame}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2"
          >
            <Plus size={16} />
            Create Sample Game
          </button>
        </div>

        <div className="space-y-8">
          {/* Node Status Section */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Server size={24} />
                Node Status
              </h2>
              <button 
                onClick={fetchHealthStatus}
                className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg hover:bg-gray-50"
              >
                <RefreshCw size={16} />
                Refresh Status
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <NodeCard name="Master Node" nodeKey="master" />
              <NodeCard name="Windows Node" nodeKey="slave_a" />
              <NodeCard name="Multi-OS Node" nodeKey="slave_b" />
            </div>
          </section>

          {/* Sync Status Section */}
          <section>
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Database size={24} />
              Synchronization Status
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SyncStatus 
                title="Windows Games" 
                data={{
                  creates: pendingSync.pending_windows_games,
                  updates: pendingSync.pending_windows_updates,
                  deletes: pendingSync.pending_windows_deletes
                }}
              />
              <SyncStatus 
                title="Multi-OS Games" 
                data={{
                  creates: pendingSync.pending_multi_os_games,
                  updates: pendingSync.pending_multi_os_updates,
                  deletes: pendingSync.pending_multi_os_deletes
                }}
              />
            </div>
          </section>
        </div>

        {/* Modals */}
        {showGameForm && <GameForm />}
        {selectedGameId && (
          <GameDetails 
            gameId={selectedGameId} 
            onClose={() => setSelectedGameId(null)} 
          />
        )}
      </div>
    </div>
  );
};

export default DatabaseInterface;