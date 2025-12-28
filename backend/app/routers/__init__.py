"""
Routers - API endpoint organization
"""
from .auth import router as auth_router
from .employees import router as employees_router
from .tasks import router as tasks_router
from .documents import router as documents_router
from .training import router as training_router
from .performance import router as performance_router
from .dashboard import router as dashboard_router
from .onboarding import router as onboarding_router
from .assistants import router as assistants_router

__all__ = [
    "auth_router",
    "employees_router",
    "tasks_router",
    "documents_router",
    "training_router",
    "performance_router",
    "dashboard_router",
    "onboarding_router",
    "assistants_router",
]
