import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const Header = ({ onSearch, searchTerm, setSearchTerm }) => (
  <header className="bg-gray-900 border-b border-gray-800">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-16">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-white">NFTMarket</h1>
        </div>
        <div className="flex-1 max-w-lg mx-8">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && onSearch()}
              placeholder="Search NFTs, collections, and users"
              className="block w-full pl-10 pr-3 py-2 border border-gray-600 rounded-md leading-5 bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">
            Connect Wallet
          </button>
        </div>
      </div>
    </div>
  </header>
);

const Hero = ({ featuredNFTs }) => (
  <section className="bg-gradient-to-r from-purple-900 via-blue-900 to-indigo-900 py-20">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
          Discover, Create, and Sell NFTs
        </h1>
        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          The world's first and largest digital marketplace for crypto collectibles and non-fungible tokens
        </p>
        <div className="flex justify-center space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-md text-lg font-semibold transition-colors">
            Explore
          </button>
          <button className="border border-white text-white hover:bg-white hover:text-gray-900 px-8 py-3 rounded-md text-lg font-semibold transition-colors">
            Create
          </button>
        </div>
      </div>
      
      {featuredNFTs.length > 0 && (
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          {featuredNFTs.slice(0, 3).map((nft) => (
            <div key={nft.id} className="bg-gray-800 rounded-xl overflow-hidden shadow-xl hover:shadow-2xl transition-shadow">
              <img
                src={`data:image/jpeg;base64,${nft.image}`}
                alt={nft.name}
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-2">{nft.name}</h3>
                <p className="text-gray-400 mb-4">{nft.collection}</p>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-blue-400">{nft.price} ETH</span>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">
                    Buy Now
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </section>
);

const NFTCard = ({ nft, onLike, onView }) => (
  <div className="bg-gray-800 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
    <div className="relative">
      <img
        src={`data:image/jpeg;base64,${nft.image}`}
        alt={nft.name}
        className="w-full h-64 object-cover cursor-pointer"
        onClick={() => onView(nft)}
      />
      <div className="absolute top-2 right-2 flex space-x-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onLike(nft.id);
          }}
          className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
      <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
        {nft.status}
      </div>
    </div>
    <div className="p-4">
      <h3 className="text-lg font-bold text-white mb-1">{nft.name}</h3>
      <p className="text-gray-400 text-sm mb-2">{nft.collection}</p>
      <p className="text-gray-300 text-sm mb-4 line-clamp-2">{nft.description}</p>
      <div className="flex justify-between items-center">
        <div>
          <span className="text-xs text-gray-400">Price</span>
          <p className="text-xl font-bold text-blue-400">{nft.price} ETH</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">
          Buy Now
        </button>
      </div>
      <div className="flex justify-between items-center mt-4 text-sm text-gray-400">
        <span>❤️ {nft.likes}</span>
        <span>👁️ {nft.views}</span>
      </div>
    </div>
  </div>
);

const NFTGrid = ({ nfts, onLike, onView, loading }) => (
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h2 className="text-3xl font-bold text-white mb-8">Explore NFTs</h2>
    
    {loading ? (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="bg-gray-800 rounded-xl overflow-hidden animate-pulse">
            <div className="w-full h-64 bg-gray-700"></div>
            <div className="p-4">
              <div className="h-4 bg-gray-700 rounded mb-2"></div>
              <div className="h-3 bg-gray-700 rounded mb-4"></div>
              <div className="h-8 bg-gray-700 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {nfts.map((nft) => (
          <NFTCard
            key={nft.id}
            nft={nft}
            onLike={onLike}
            onView={onView}
          />
        ))}
      </div>
    )}
  </div>
);

const NFTModal = ({ nft, onClose, onBuy }) => {
  if (!nft) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-gray-800 rounded-xl max-w-4xl w-full mx-4 max-h-90vh overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-6 border-b border-gray-700">
          <h2 className="text-2xl font-bold text-white">{nft.name}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-6">
          <div>
            <img
              src={`data:image/jpeg;base64,${nft.image}`}
              alt={nft.name}
              className="w-full rounded-lg"
            />
          </div>
          
          <div>
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-2">Collection</h3>
              <p className="text-blue-400">{nft.collection}</p>
            </div>
            
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-2">Description</h3>
              <p className="text-gray-300">{nft.description}</p>
            </div>
            
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-2">Details</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Token ID:</span>
                  <p className="text-white">{nft.token_id}</p>
                </div>
                <div>
                  <span className="text-gray-400">Status:</span>
                  <p className="text-white">{nft.status}</p>
                </div>
                <div>
                  <span className="text-gray-400">Owner:</span>
                  <p className="text-white">{nft.owner.substring(0, 10)}...</p>
                </div>
                <div>
                  <span className="text-gray-400">Created:</span>
                  <p className="text-white">{new Date(nft.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
            
            {nft.traits && nft.traits.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-2">Traits</h3>
                <div className="grid grid-cols-2 gap-2">
                  {nft.traits.map((trait, index) => (
                    <div key={index} className="bg-gray-700 rounded-lg p-3 text-center">
                      <p className="text-blue-400 text-sm">{trait.trait_type}</p>
                      <p className="text-white font-semibold">{trait.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="border-t border-gray-700 pt-6">
              <div className="flex justify-between items-center mb-4">
                <span className="text-gray-400">Current Price</span>
                <span className="text-3xl font-bold text-blue-400">{nft.price} ETH</span>
              </div>
              <button
                onClick={() => onBuy(nft)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-md font-semibold transition-colors"
              >
                Buy Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Stats = ({ stats }) => (
  <section className="bg-gray-900 py-16">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h2 className="text-3xl font-bold text-white text-center mb-12">Marketplace Stats</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <div className="text-center">
          <div className="text-4xl font-bold text-blue-400 mb-2">{stats.total_nfts}</div>
          <div className="text-gray-400">Total NFTs</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-green-400 mb-2">{stats.total_users}</div>
          <div className="text-gray-400">Total Users</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-purple-400 mb-2">{stats.total_collections}</div>
          <div className="text-gray-400">Collections</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-yellow-400 mb-2">{stats.total_volume?.toFixed(1)} ETH</div>
          <div className="text-gray-400">Total Volume</div>
        </div>
      </div>
    </div>
  </section>
);

const FilterBar = ({ onFilterChange, loading }) => (
  <div className="bg-gray-800 border-b border-gray-700">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <select
            onChange={(e) => onFilterChange('status', e.target.value)}
            className="bg-gray-700 text-white rounded-md px-3 py-2 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          >
            <option value="">All Status</option>
            <option value="listed">Listed</option>
            <option value="sold">Sold</option>
            <option value="unlisted">Unlisted</option>
          </select>
          
          <select
            onChange={(e) => onFilterChange('sort', e.target.value)}
            className="bg-gray-700 text-white rounded-md px-3 py-2 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          >
            <option value="created_at">Recently Created</option>
            <option value="price">Price</option>
            <option value="likes">Most Liked</option>
            <option value="views">Most Viewed</option>
          </select>
        </div>
        
        <div className="text-sm text-gray-400">
          {loading ? 'Loading...' : 'Showing all NFTs'}
        </div>
      </div>
    </div>
  </div>
);

function App() {
  const [nfts, setNfts] = useState([]);
  const [featuredNFTs, setFeaturedNFTs] = useState([]);
  const [selectedNft, setSelectedNft] = useState(null);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({ status: '', sort: 'created_at' });

  const initializeData = async () => {
    try {
      await axios.post(`${API}/init-sample-data`);
      console.log('Sample data initialized');
    } catch (error) {
      console.error('Error initializing sample data:', error);
    }
  };

  const fetchNFTs = async (search = '', filterStatus = '', sortBy = 'created_at') => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: '20',
        sort_by: sortBy,
        order: 'desc'
      });
      
      if (search) params.append('search', search);
      if (filterStatus) params.append('status', filterStatus);
      
      const response = await axios.get(`${API}/nfts?${params}`);
      setNfts(response.data);
      setFeaturedNFTs(response.data.slice(0, 3));
    } catch (error) {
      console.error('Error fetching NFTs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleLike = async (nftId) => {
    try {
      await axios.post(`${API}/nfts/${nftId}/like`);
      setNfts(nfts.map(nft => 
        nft.id === nftId 
          ? { ...nft, likes: nft.likes + 1 }
          : nft
      ));
    } catch (error) {
      console.error('Error liking NFT:', error);
    }
  };

  const handleView = (nft) => {
    setSelectedNft(nft);
  };

  const handleBuy = async (nft) => {
    try {
      const transaction = {
        nft_id: nft.id,
        buyer: '0x' + Math.random().toString(16).substr(2, 40),
        seller: nft.owner,
        price: nft.price
      };
      
      await axios.post(`${API}/transactions`, transaction);
      alert('Purchase successful! Transaction is being processed.');
      setSelectedNft(null);
      fetchNFTs(searchTerm, filters.status, filters.sort);
      fetchStats();
    } catch (error) {
      console.error('Error buying NFT:', error);
      alert('Purchase failed. Please try again.');
    }
  };

  const handleSearch = () => {
    fetchNFTs(searchTerm, filters.status, filters.sort);
  };

  const handleFilterChange = (filterType, value) => {
    const newFilters = { ...filters, [filterType]: value };
    setFilters(newFilters);
    fetchNFTs(searchTerm, newFilters.status, newFilters.sort);
  };

  useEffect(() => {
    const initialize = async () => {
      await initializeData();
      await Promise.all([fetchNFTs(), fetchStats()]);
    };
    initialize();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900">
      <Header 
        onSearch={handleSearch}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
      />
      
      <Hero featuredNFTs={featuredNFTs} />
      
      <Stats stats={stats} />
      
      <FilterBar 
        onFilterChange={handleFilterChange}
        loading={loading}
      />
      
      <NFTGrid 
        nfts={nfts}
        onLike={handleLike}
        onView={handleView}
        loading={loading}
      />
      
      {selectedNft && (
        <NFTModal
          nft={selectedNft}
          onClose={() => setSelectedNft(null)}
          onBuy={handleBuy}
        />
      )}
    </div>
  );
}

export default App;