from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
import base64
import requests


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="NFT Marketplace API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class NFTStatus(str, Enum):
    LISTED = "listed"
    SOLD = "sold"
    UNLISTED = "unlisted"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

# Models
class NFTTrait(BaseModel):
    trait_type: str
    value: str
    rarity: Optional[float] = None

class NFT(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    image: str  # base64 encoded image
    price: float
    owner: str
    creator: str
    collection: str
    traits: List[NFTTrait] = []
    token_id: int
    contract_address: str = Field(default_factory=lambda: f"0x{uuid.uuid4().hex[:40]}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: NFTStatus = NFTStatus.LISTED
    likes: int = 0
    views: int = 0

class NFTCreate(BaseModel):
    name: str
    description: str
    image_url: str
    price: float
    collection: str
    traits: List[NFTTrait] = []

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    wallet_address: str = Field(default_factory=lambda: f"0x{uuid.uuid4().hex[:40]}")
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False

class UserCreate(BaseModel):
    username: str
    email: str
    bio: Optional[str] = None

class Collection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    creator: str
    banner_image: Optional[str] = None
    floor_price: float = 0.0
    volume: float = 0.0
    items_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CollectionCreate(BaseModel):
    name: str
    description: str
    banner_image_url: Optional[str] = None

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nft_id: str
    buyer: str
    seller: str
    price: float
    transaction_hash: str = Field(default_factory=lambda: f"0x{uuid.uuid4().hex}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: TransactionStatus = TransactionStatus.PENDING

class TransactionCreate(BaseModel):
    nft_id: str
    buyer: str
    seller: str
    price: float

# Utility functions
async def download_and_encode_image(image_url: str) -> str:
    """Download image from URL and encode to base64"""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return ""

# Routes
@api_router.get("/")
async def root():
    return {"message": "NFT Marketplace API"}

# NFT Routes
@api_router.get("/nfts", response_model=List[NFT])
async def get_nfts(
    skip: int = 0,
    limit: int = 20,
    collection: Optional[str] = None,
    status: Optional[NFTStatus] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "desc"
):
    query = {}
    if collection:
        query["collection"] = collection
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"collection": {"$regex": search, "$options": "i"}}
        ]
    
    sort_order = -1 if order == "desc" else 1
    
    nfts = await db.nfts.find(query).sort(sort_by, sort_order).skip(skip).limit(limit).to_list(length=limit)
    return [NFT(**nft) for nft in nfts]

@api_router.get("/nfts/{nft_id}", response_model=NFT)
async def get_nft(nft_id: str):
    nft = await db.nfts.find_one({"id": nft_id})
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    
    # Increment views
    await db.nfts.update_one({"id": nft_id}, {"$inc": {"views": 1}})
    nft["views"] = nft.get("views", 0) + 1
    
    return NFT(**nft)

@api_router.post("/nfts", response_model=NFT)
async def create_nft(nft_data: NFTCreate):
    # Download and encode image
    image_base64 = await download_and_encode_image(nft_data.image_url)
    
    nft = NFT(
        name=nft_data.name,
        description=nft_data.description,
        image=image_base64,
        price=nft_data.price,
        owner="0x" + uuid.uuid4().hex[:40],  # Mock owner
        creator="0x" + uuid.uuid4().hex[:40],  # Mock creator
        collection=nft_data.collection,
        traits=nft_data.traits,
        token_id=await get_next_token_id()
    )
    
    await db.nfts.insert_one(nft.dict())
    
    # Update collection stats
    await update_collection_stats(nft.collection)
    
    return nft

@api_router.post("/nfts/{nft_id}/like")
async def like_nft(nft_id: str):
    result = await db.nfts.update_one(
        {"id": nft_id},
        {"$inc": {"likes": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="NFT not found")
    return {"message": "NFT liked successfully"}

# User Routes
@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    user = User(
        username=user_data.username,
        email=user_data.email,
        bio=user_data.bio
    )
    await db.users.insert_one(user.dict())
    return user

@api_router.get("/users/{user_id}/nfts", response_model=List[NFT])
async def get_user_nfts(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    nfts = await db.nfts.find({"owner": user["wallet_address"]}).to_list(1000)
    return [NFT(**nft) for nft in nfts]

# Collection Routes
@api_router.get("/collections", response_model=List[Collection])
async def get_collections():
    collections = await db.collections.find().to_list(1000)
    return [Collection(**collection) for collection in collections]

@api_router.get("/collections/{collection_id}", response_model=Collection)
async def get_collection(collection_id: str):
    collection = await db.collections.find_one({"id": collection_id})
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return Collection(**collection)

@api_router.post("/collections", response_model=Collection)
async def create_collection(collection_data: CollectionCreate):
    banner_image = ""
    if collection_data.banner_image_url:
        banner_image = await download_and_encode_image(collection_data.banner_image_url)
    
    collection = Collection(
        name=collection_data.name,
        description=collection_data.description,
        creator="0x" + uuid.uuid4().hex[:40],  # Mock creator
        banner_image=banner_image
    )
    await db.collections.insert_one(collection.dict())
    return collection

@api_router.get("/collections/{collection_id}/nfts", response_model=List[NFT])
async def get_collection_nfts(collection_id: str):
    collection = await db.collections.find_one({"id": collection_id})
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    nfts = await db.nfts.find({"collection": collection["name"]}).to_list(1000)
    return [NFT(**nft) for nft in nfts]

# Transaction Routes
@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions():
    transactions = await db.transactions.find().sort("timestamp", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate):
    # Simulate blockchain transaction
    transaction = Transaction(
        nft_id=transaction_data.nft_id,
        buyer=transaction_data.buyer,
        seller=transaction_data.seller,
        price=transaction_data.price,
        status=TransactionStatus.PENDING
    )
    
    await db.transactions.insert_one(transaction.dict())
    
    # Update NFT ownership and status
    await db.nfts.update_one(
        {"id": transaction_data.nft_id},
        {
            "$set": {
                "owner": transaction_data.buyer,
                "status": NFTStatus.SOLD
            }
        }
    )
    
    # Simulate transaction completion after a delay
    await complete_transaction(transaction.id)
    
    return transaction

@api_router.get("/stats")
async def get_marketplace_stats():
    total_nfts = await db.nfts.count_documents({})
    total_users = await db.users.count_documents({})
    total_collections = await db.collections.count_documents({})
    
    # Calculate total volume
    transactions = await db.transactions.find({"status": TransactionStatus.COMPLETED}).to_list(1000)
    total_volume = sum(transaction.get("price", 0) for transaction in transactions)
    
    return {
        "total_nfts": total_nfts,
        "total_users": total_users,
        "total_collections": total_collections,
        "total_volume": total_volume,
        "active_listings": await db.nfts.count_documents({"status": NFTStatus.LISTED})
    }

# Utility functions
async def get_next_token_id():
    """Get the next token ID for NFT minting"""
    count = await db.nfts.count_documents({})
    return count + 1

async def update_collection_stats(collection_name: str):
    """Update collection statistics"""
    nfts = await db.nfts.find({"collection": collection_name}).to_list(1000)
    if not nfts:
        return
    
    # Calculate floor price
    listed_nfts = [nft for nft in nfts if nft.get("status") == NFTStatus.LISTED]
    floor_price = min(nft.get("price", 0) for nft in listed_nfts) if listed_nfts else 0
    
    # Calculate volume
    transactions = await db.transactions.find({"status": TransactionStatus.COMPLETED}).to_list(1000)
    collection_transactions = [t for t in transactions if any(nft.get("id") == t.get("nft_id") for nft in nfts)]
    volume = sum(transaction.get("price", 0) for transaction in collection_transactions)
    
    # Update collection
    await db.collections.update_one(
        {"name": collection_name},
        {
            "$set": {
                "floor_price": floor_price,
                "volume": volume,
                "items_count": len(nfts)
            }
        }
    )

async def complete_transaction(transaction_id: str):
    """Complete a pending transaction"""
    await db.transactions.update_one(
        {"id": transaction_id},
        {"$set": {"status": TransactionStatus.COMPLETED}}
    )

# Initialize sample data
@api_router.post("/init-sample-data")
async def init_sample_data():
    """Initialize the marketplace with sample NFTs and collections"""
    
    # Sample NFT images (from vision expert)
    sample_images = [
        "https://images.unsplash.com/photo-1635377090186-036bca445c6b",
        "https://images.pexels.com/photos/1670977/pexels-photo-1670977.jpeg",
        "https://images.pexels.com/photos/5011647/pexels-photo-5011647.jpeg", 
        "https://images.pexels.com/photos/1081685/pexels-photo-1081685.jpeg",
        "https://images.unsplash.com/photo-1693920105404-c2208c22cfe4",
        "https://images.unsplash.com/photo-1634320714682-ae8b9c9cee60",
        "https://images.pexels.com/photos/32796044/pexels-photo-32796044.jpeg",
        "https://images.pexels.com/photos/8347501/pexels-photo-8347501.jpeg"
    ]
    
    # Create sample collections
    collections = [
        {"name": "CryptoArt", "description": "Exclusive digital art collection"},
        {"name": "PixelPunks", "description": "Retro pixel art avatars"},
        {"name": "Abstract3D", "description": "3D rendered abstract artwork"},
        {"name": "DigitalPortraits", "description": "AI-generated portrait collection"}
    ]
    
    for coll in collections:
        collection = Collection(
            name=coll["name"],
            description=coll["description"],
            creator="0x" + uuid.uuid4().hex[:40]
        )
        await db.collections.insert_one(collection.dict())
    
    # Create sample NFTs
    nft_data = [
        {"name": "Colorful Abstraction", "description": "A vibrant abstract digital artwork", "price": 2.5, "collection": "CryptoArt"},
        {"name": "Space Invader", "description": "Classic retro pixel art", "price": 1.2, "collection": "PixelPunks"},
        {"name": "Cubic Dreams", "description": "3D rendered minimalist cube", "price": 3.0, "collection": "Abstract3D"},
        {"name": "Digital Portrait", "description": "AI-enhanced digital portrait", "price": 1.8, "collection": "DigitalPortraits"},
        {"name": "Purple Waves", "description": "Abstract 3D rendered waves", "price": 4.2, "collection": "Abstract3D"},
        {"name": "Pixel Mona Lisa", "description": "Classic art in pixel form", "price": 5.0, "collection": "PixelPunks"},
        {"name": "Flowing Colors", "description": "Vibrant flowing abstract shapes", "price": 2.8, "collection": "CryptoArt"},
        {"name": "Neon Portal", "description": "3D rendered portal with neon effects", "price": 3.5, "collection": "Abstract3D"}
    ]
    
    for i, nft in enumerate(nft_data):
        image_base64 = await download_and_encode_image(sample_images[i])
        
        nft_obj = NFT(
            name=nft["name"],
            description=nft["description"],
            image=image_base64,
            price=nft["price"],
            owner="0x" + uuid.uuid4().hex[:40],
            creator="0x" + uuid.uuid4().hex[:40],
            collection=nft["collection"],
            token_id=i + 1,
            traits=[
                NFTTrait(trait_type="Rarity", value="Common" if i % 3 == 0 else "Rare"),
                NFTTrait(trait_type="Style", value=nft["collection"])
            ]
        )
        
        await db.nfts.insert_one(nft_obj.dict())
    
    # Update collection stats
    for coll in collections:
        await update_collection_stats(coll["name"])
    
    return {"message": "Sample data initialized successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()