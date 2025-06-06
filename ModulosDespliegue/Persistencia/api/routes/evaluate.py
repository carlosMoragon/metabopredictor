from fastapi import APIRouter, HTTPException
from models import RequestResponseModel, EvaluateCacheModel
from db import evaluates
from pymongo import DESCENDING
from utils import with_clean_mongo_id

router = APIRouter()

# Ruta para consultar la caché
@router.post("/cache")
@with_clean_mongo_id(remove_id=True) 
async def evaluate_cache(data: EvaluateCacheModel):
    # Convertir usando alias para que el JSON coincida con el guardado
    request_query = data.dict(by_alias=True, exclude_unset=True)

    cached = await evaluates.find_one(
        {"request": request_query}, sort=[("respond.Score", DESCENDING)]
    )

    if cached:
        cached['cacheHits'] = cached.get('cacheHits', 0) + 1
        await evaluates.replace_one({"_id": cached["_id"]}, cached)
        return {"cached": True, "result": cached}
    else:
        return {"cached": False, "result": None}

# Ruta para guardar un resultado en la caché
@router.post("/save")
async def evaluate_save(data: RequestResponseModel):
    try:
        await evaluates.insert_one(data.dict(by_alias=True))
        return {"stored": True, "message": "Result successfully stored in cache."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving result: {e}")
