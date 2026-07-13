from app.api.action_logs import (
    router as action_logs_router,
)
from app.api.club_settings import (
    router as club_settings_router,
)
from app.api.debts import router as debts_router
from app.api.employees import router as employees_router
from app.api.inventory_balances import (
    router as inventory_balances_router,
)
from app.api.lightshell_imports import (
    router as lightshell_imports_router,
)
from app.api.prizes import router as prizes_router
from app.api.products import router as products_router

__all__ = [
    "action_logs_router",
    "club_settings_router",
    "debts_router",
    "employees_router",
    "inventory_balances_router",
    "lightshell_imports_router",
    "prizes_router",
    "products_router",
]