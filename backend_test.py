#!/usr/bin/env python3
import requests
import json
import time
import unittest
import sys
from enum import Enum
from typing import Dict, List, Optional, Any

# Base URL for API requests
BASE_URL = "https://3eea92df-47f3-42d9-8b38-34dd6ad2d8bd.preview.emergentagent.com/api"

class NFTStatus(str, Enum):
    LISTED = "listed"
    SOLD = "sold"
    UNLISTED = "unlisted"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class NFTMarketplaceTests(unittest.TestCase):
    """Test suite for NFT Marketplace API"""
    
    test_nft = None
    
    @classmethod
    def setUpClass(cls):
        """Initialize test data"""
        print("\n=== Setting up test data ===")
        # Initialize sample data
        response = requests.post(f"{BASE_URL}/init-sample-data")
        cls.assertTrue = unittest.TestCase.assertTrue
        cls.assertEqual = unittest.TestCase.assertEqual
        cls.assertIn = unittest.TestCase.assertIn
        cls.assertIsNotNone = unittest.TestCase.assertIsNotNone
        
        if response.status_code == 200:
            print("✅ Sample data initialized successfully")
        else:
            print(f"❌ Failed to initialize sample data: {response.status_code} - {response.text}")
            sys.exit(1)
        
        # Get initial NFTs for later tests
        cls.nfts = requests.get(f"{BASE_URL}/nfts").json()
        cls.collections = requests.get(f"{BASE_URL}/collections").json()
        
        # Create a test user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "bio": "Test user for API testing"
        }
        cls.test_user = requests.post(f"{BASE_URL}/users", json=user_data).json()
        print(f"Created test user: {cls.test_user['username']} (ID: {cls.test_user['id']})")
        
        # Create a test NFT for later tests
        if cls.collections:
            nft_data = {
                "name": "Test NFT",
                "description": "Created during API testing",
                "image_url": "https://images.unsplash.com/photo-1635377090186-036bca445c6b",
                "price": 1.5,
                "collection": cls.collections[0]["name"],
                "traits": [
                    {"trait_type": "Test", "value": "API Testing"}
                ]
            }
            
            response = requests.post(f"{BASE_URL}/nfts", json=nft_data)
            if response.status_code == 200:
                cls.test_nft = response.json()
                print(f"Created test NFT: {cls.test_nft['name']} (ID: {cls.test_nft['id']})")
            else:
                print(f"❌ Failed to create test NFT: {response.status_code} - {response.text}")
    
    def test_01_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n=== Testing Root Endpoint ===")
        response = requests.get(f"{BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "NFT Marketplace API"})
        print("✅ Root endpoint working correctly")
    
    def test_02_get_nfts(self):
        """Test getting all NFTs"""
        print("\n=== Testing GET /nfts ===")
        response = requests.get(f"{BASE_URL}/nfts")
        self.assertEqual(response.status_code, 200)
        nfts = response.json()
        self.assertTrue(len(nfts) > 0)
        print(f"✅ Retrieved {len(nfts)} NFTs successfully")
        
        # Verify NFT structure
        nft = nfts[0]
        required_fields = ["id", "name", "description", "image", "price", "owner", 
                          "creator", "collection", "token_id", "status"]
        for field in required_fields:
            self.assertIn(field, nft)
        print("✅ NFT data structure is correct")
    
    def test_03_get_nft_by_id(self):
        """Test getting a specific NFT by ID"""
        print("\n=== Testing GET /nfts/{nft_id} ===")
        if not self.nfts:
            self.fail("No NFTs available for testing")
        
        nft_id = self.nfts[0]["id"]
        response = requests.get(f"{BASE_URL}/nfts/{nft_id}")
        self.assertEqual(response.status_code, 200)
        nft = response.json()
        self.assertEqual(nft["id"], nft_id)
        print(f"✅ Retrieved NFT by ID: {nft['name']} (ID: {nft_id})")
        
        # Test non-existent NFT
        response = requests.get(f"{BASE_URL}/nfts/nonexistent-id")
        self.assertEqual(response.status_code, 404)
        print("✅ 404 response for non-existent NFT")
    
    def test_04_create_nft(self):
        """Test creating a new NFT"""
        print("\n=== Testing POST /nfts ===")
        nft_data = {
            "name": "Test NFT",
            "description": "Created during API testing",
            "image_url": "https://images.unsplash.com/photo-1635377090186-036bca445c6b",
            "price": 1.5,
            "collection": self.collections[0]["name"],
            "traits": [
                {"trait_type": "Test", "value": "API Testing"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/nfts", json=nft_data)
        self.assertEqual(response.status_code, 200)
        new_nft = response.json()
        self.assertEqual(new_nft["name"], nft_data["name"])
        self.assertEqual(new_nft["description"], nft_data["description"])
        self.assertEqual(new_nft["price"], nft_data["price"])
        self.assertEqual(new_nft["collection"], nft_data["collection"])
        self.assertIsNotNone(new_nft["image"])
        print(f"✅ Created new NFT: {new_nft['name']} (ID: {new_nft['id']})")
        
        # Save for later tests
        self.test_nft = new_nft
    
    def test_05_like_nft(self):
        """Test liking an NFT"""
        print("\n=== Testing POST /nfts/{nft_id}/like ===")
        if not hasattr(self, 'test_nft'):
            self.fail("No test NFT available")
        
        nft_id = self.test_nft["id"]
        initial_likes = self.test_nft["likes"]
        
        response = requests.post(f"{BASE_URL}/nfts/{nft_id}/like")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "NFT liked successfully"})
        
        # Verify likes increased
        response = requests.get(f"{BASE_URL}/nfts/{nft_id}")
        updated_nft = response.json()
        self.assertEqual(updated_nft["likes"], initial_likes + 1)
        print(f"✅ Liked NFT: {updated_nft['name']} (Likes: {updated_nft['likes']})")
    
    def test_06_search_and_filter_nfts(self):
        """Test searching and filtering NFTs"""
        print("\n=== Testing NFT Search and Filtering ===")
        
        # Test search
        search_term = "abstract"
        response = requests.get(f"{BASE_URL}/nfts?search={search_term}")
        self.assertEqual(response.status_code, 200)
        search_results = response.json()
        print(f"✅ Search for '{search_term}' returned {len(search_results)} results")
        
        # Test filtering by collection
        if self.collections:
            collection_name = self.collections[0]["name"]
            response = requests.get(f"{BASE_URL}/nfts?collection={collection_name}")
            self.assertEqual(response.status_code, 200)
            collection_results = response.json()
            print(f"✅ Filter by collection '{collection_name}' returned {len(collection_results)} results")
            
            # Verify all NFTs belong to the specified collection
            for nft in collection_results:
                self.assertEqual(nft["collection"], collection_name)
        
        # Test filtering by status
        response = requests.get(f"{BASE_URL}/nfts?status={NFTStatus.LISTED}")
        self.assertEqual(response.status_code, 200)
        status_results = response.json()
        print(f"✅ Filter by status '{NFTStatus.LISTED}' returned {len(status_results)} results")
        
        # Verify all NFTs have the specified status
        for nft in status_results:
            self.assertEqual(nft["status"], NFTStatus.LISTED)
        
        # Test sorting
        response = requests.get(f"{BASE_URL}/nfts?sort_by=price&order=asc")
        self.assertEqual(response.status_code, 200)
        sorted_results = response.json()
        print(f"✅ Sorting by price (ascending) returned {len(sorted_results)} results")
        
        # Verify sorting
        if len(sorted_results) > 1:
            for i in range(len(sorted_results) - 1):
                self.assertTrue(sorted_results[i]["price"] <= sorted_results[i+1]["price"])
    
    def test_07_get_users(self):
        """Test getting all users"""
        print("\n=== Testing GET /users ===")
        response = requests.get(f"{BASE_URL}/users")
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertTrue(len(users) > 0)
        print(f"✅ Retrieved {len(users)} users successfully")
    
    def test_08_get_user_by_id(self):
        """Test getting a specific user by ID"""
        print("\n=== Testing GET /users/{user_id} ===")
        user_id = self.test_user["id"]
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.assertEqual(user["id"], user_id)
        print(f"✅ Retrieved user by ID: {user['username']} (ID: {user_id})")
        
        # Test non-existent user
        response = requests.get(f"{BASE_URL}/users/nonexistent-id")
        self.assertEqual(response.status_code, 404)
        print("✅ 404 response for non-existent user")
    
    def test_09_get_collections(self):
        """Test getting all collections"""
        print("\n=== Testing GET /collections ===")
        response = requests.get(f"{BASE_URL}/collections")
        self.assertEqual(response.status_code, 200)
        collections = response.json()
        self.assertTrue(len(collections) > 0)
        print(f"✅ Retrieved {len(collections)} collections successfully")
        
        # Verify collection structure
        collection = collections[0]
        required_fields = ["id", "name", "description", "creator", "floor_price", "volume", "items_count"]
        for field in required_fields:
            self.assertIn(field, collection)
        print("✅ Collection data structure is correct")
    
    def test_10_get_collection_by_id(self):
        """Test getting a specific collection by ID"""
        print("\n=== Testing GET /collections/{collection_id} ===")
        if not self.collections:
            self.fail("No collections available for testing")
        
        collection_id = self.collections[0]["id"]
        response = requests.get(f"{BASE_URL}/collections/{collection_id}")
        self.assertEqual(response.status_code, 200)
        collection = response.json()
        self.assertEqual(collection["id"], collection_id)
        print(f"✅ Retrieved collection by ID: {collection['name']} (ID: {collection_id})")
    
    def test_11_create_collection(self):
        """Test creating a new collection"""
        print("\n=== Testing POST /collections ===")
        collection_data = {
            "name": "Test Collection",
            "description": "Created during API testing",
            "banner_image_url": "https://images.unsplash.com/photo-1635377090186-036bca445c6b"
        }
        
        response = requests.post(f"{BASE_URL}/collections", json=collection_data)
        self.assertEqual(response.status_code, 200)
        new_collection = response.json()
        self.assertEqual(new_collection["name"], collection_data["name"])
        self.assertEqual(new_collection["description"], collection_data["description"])
        print(f"✅ Created new collection: {new_collection['name']} (ID: {new_collection['id']})")
    
    def test_12_get_collection_nfts(self):
        """Test getting NFTs from a specific collection"""
        print("\n=== Testing GET /collections/{collection_id}/nfts ===")
        if not self.collections:
            self.fail("No collections available for testing")
        
        collection_id = self.collections[0]["id"]
        collection_name = self.collections[0]["name"]
        response = requests.get(f"{BASE_URL}/collections/{collection_id}/nfts")
        self.assertEqual(response.status_code, 200)
        nfts = response.json()
        print(f"✅ Retrieved {len(nfts)} NFTs from collection '{collection_name}'")
        
        # Verify all NFTs belong to the collection
        for nft in nfts:
            self.assertEqual(nft["collection"], collection_name)
    
    def test_13_get_transactions(self):
        """Test getting all transactions"""
        print("\n=== Testing GET /transactions ===")
        response = requests.get(f"{BASE_URL}/transactions")
        self.assertEqual(response.status_code, 200)
        transactions = response.json()
        print(f"✅ Retrieved {len(transactions)} transactions successfully")
    
    def test_14_create_transaction(self):
        """Test creating a new transaction"""
        print("\n=== Testing POST /transactions ===")
        if not hasattr(self, 'test_nft'):
            self.fail("No test NFT available")
        
        transaction_data = {
            "nft_id": self.test_nft["id"],
            "buyer": "0x" + "1" * 40,  # Mock buyer address
            "seller": self.test_nft["owner"],
            "price": self.test_nft["price"]
        }
        
        response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
        self.assertEqual(response.status_code, 200)
        new_transaction = response.json()
        self.assertEqual(new_transaction["nft_id"], transaction_data["nft_id"])
        self.assertEqual(new_transaction["buyer"], transaction_data["buyer"])
        self.assertEqual(new_transaction["seller"], transaction_data["seller"])
        self.assertEqual(new_transaction["price"], transaction_data["price"])
        print(f"✅ Created new transaction for NFT: {self.test_nft['name']} (ID: {self.test_nft['id']})")
        
        # Verify NFT ownership and status updated
        time.sleep(1)  # Wait for transaction to complete
        response = requests.get(f"{BASE_URL}/nfts/{self.test_nft['id']}")
        updated_nft = response.json()
        self.assertEqual(updated_nft["owner"], transaction_data["buyer"])
        self.assertEqual(updated_nft["status"], NFTStatus.SOLD)
        print(f"✅ NFT ownership and status updated correctly")
    
    def test_15_get_marketplace_stats(self):
        """Test getting marketplace statistics"""
        print("\n=== Testing GET /stats ===")
        response = requests.get(f"{BASE_URL}/stats")
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        
        required_fields = ["total_nfts", "total_users", "total_collections", "total_volume", "active_listings"]
        for field in required_fields:
            self.assertIn(field, stats)
        
        # Verify stats are reasonable
        self.assertTrue(stats["total_nfts"] > 0)
        self.assertTrue(stats["total_users"] > 0)
        self.assertTrue(stats["total_collections"] > 0)
        print(f"✅ Marketplace stats retrieved successfully:")
        print(f"   - Total NFTs: {stats['total_nfts']}")
        print(f"   - Total Users: {stats['total_users']}")
        print(f"   - Total Collections: {stats['total_collections']}")
        print(f"   - Total Volume: {stats['total_volume']}")
        print(f"   - Active Listings: {stats['active_listings']}")
    
    def test_16_image_processing(self):
        """Test image processing and base64 encoding"""
        print("\n=== Testing Image Processing ===")
        if not hasattr(self, 'test_nft'):
            self.fail("No test NFT available")
        
        # Verify image is base64 encoded
        self.assertTrue(len(self.test_nft["image"]) > 0)
        
        # Try to decode the base64 image
        try:
            import base64
            image_data = base64.b64decode(self.test_nft["image"])
            self.assertTrue(len(image_data) > 0)
            print(f"✅ Image is properly base64 encoded ({len(image_data)} bytes)")
        except Exception as e:
            self.fail(f"Failed to decode base64 image: {e}")

def run_tests():
    """Run all tests"""
    print("\n========================================")
    print("🧪 NFT MARKETPLACE API TESTS")
    print("========================================")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(NFTMarketplaceTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n========================================")
    print(f"🧪 TEST SUMMARY")
    print("========================================")
    print(f"Total tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    # Return success/failure
    return len(result.failures) + len(result.errors) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)