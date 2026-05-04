from fastapi import APIRouter, HTTPException, Query
from models import ObituaryResponse, PaginatedObituaries
from database import collection
from bson import ObjectId

router = APIRouter()

def serialize_mongo_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("/api/obituaries", response_model=PaginatedObituaries)
async def get_obituaries(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50)):
    skip = (page - 1) * size
    
    cursor = collection.find().sort("created_at", -1).skip(skip).limit(size)
    docs = await cursor.to_list(length=size)
    
    total = await collection.count_documents({})
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "data": [serialize_mongo_doc(doc) for doc in docs]
    }

@router.get("/api/obituaries/{id}", response_model=ObituaryResponse)
async def get_obituary(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
        
    doc = await collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Obituary not found")
        
    return serialize_mongo_doc(doc)

@router.get("/api/search", response_model=PaginatedObituaries)
async def search_obituaries(q: str = Query(..., min_length=2), page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=50)):
    skip = (page - 1) * size
    
    query = {"$or": [
        {"name": {"$regex": q, "$options": "i"}},
        {"content": {"$regex": q, "$options": "i"}},
        {"location": {"$regex": q, "$options": "i"}}
    ]}
    
    cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(size)
    docs = await cursor.to_list(length=size)
    
    total = await collection.count_documents(query)
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "data": [serialize_mongo_doc(doc) for doc in docs]
    }

@router.get("/api/trending")
async def get_trending_keywords():
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$limit": 50},
        {"$group": {"_id": "$name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    docs = await collection.aggregate(pipeline).to_list(length=10)
    keywords = [doc["_id"] for doc in docs if doc["_id"]]
    return {"trending": keywords}
