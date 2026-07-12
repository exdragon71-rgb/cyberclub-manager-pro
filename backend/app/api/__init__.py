from app.api.debts import router as debts_router
from app.api.employees import router as employees_router
from app.api.inventory_balances import (
    router as inventory_balances_router,
)
from app.api.lightshell_imports import (
    router as lightshell_imports_router,
)
from app.api.products import router as products_router

__all__ = [
    "debts_router",
    "employees_router",
    "inventory_balances_router",
    "lightshell_imports_router",
    "products_router",
]