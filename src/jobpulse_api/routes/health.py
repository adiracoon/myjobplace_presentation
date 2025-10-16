from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["health"])
@router.get("")
def healthz():
    return {"status": "ok"}
router_ready = APIRouter(prefix="/readyz", tags=["health"])
@router_ready.get("")
def readyz():
    return {"ready": True}
