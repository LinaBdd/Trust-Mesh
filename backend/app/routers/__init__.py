from app.routers.auth import router as auth_router
from app.routers.demo import router as demo_router
from app.routers.trust import router as trust_router

__all__ = ["auth_router", "demo_router", "trust_router"]