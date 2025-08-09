from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pydantic import ReaderCreate, ReaderResponse
from app.services.reader_service import ReaderService
from app.dependencies import get_reader_service

router = APIRouter(prefix="/readers", tags=["readers"])

@router.post("/", response_model=ReaderResponse)
async def register_reader(reader_data: ReaderCreate, service: ReaderService = Depends(get_reader_service)):
    try:
        return await service.register_reader(reader_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{reader_id}", response_model=ReaderResponse)
async def get_reader(reader_id: str, service: ReaderService = Depends(get_reader_service)):
    reader = await service.get_by_id(reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader

@router.put("/{reader_id}", response_model=ReaderResponse)
async def update_reader(reader_id: str, reader_data: ReaderCreate, service: ReaderService = Depends(get_reader_service)):
    try:
        return await service.update_reader(reader_id, reader_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{reader_id}")
async def freeze_reader(reader_id: str, service: ReaderService = Depends(get_reader_service)):
    try:
        await service.freeze_reader(reader_id)
        return {"message": "Reader frozen successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))