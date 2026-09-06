from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...api.deps import require_role
from ...database import get_db
from ...models import User
from ...services.kpi_service import get_lot_kpi_analytics, list_lots

router = APIRouter(prefix="/kpis", tags=["kpi"])


@router.get("/lots")
def read_lots_route(
    product_id: Optional[int] = None,
    current_user: User = Depends(require_role("directeur")),
    db: Session = Depends(get_db),
):
    return list_lots(db, product_id=product_id)


@router.get("/analytics/{fourniture_id}")
def read_lot_analytics_route(
    fourniture_id: int,
    current_user: User = Depends(require_role("directeur")),
    db: Session = Depends(get_db),
):
    analytics = get_lot_kpi_analytics(db, fourniture_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Lot de fourniture introuvable")
    return analytics
