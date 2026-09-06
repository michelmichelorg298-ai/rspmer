from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...api.deps import require_role
from ...database import get_db
from ...models import User
from ...schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from ...services.expense_service import (
    create_expense,
    delete_expense,
    get_expense,
    list_expenses,
    update_expense,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=List[ExpenseResponse])
def read_expenses(
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    return list_expenses(db)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def read_expense(
    expense_id: int,
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    obj = get_expense(db, expense_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    return obj


@router.post("", response_model=ExpenseResponse)
def create_expense_route(
    data: ExpenseCreate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    return create_expense(db, data)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense_route(
    expense_id: int,
    data: ExpenseUpdate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    obj = update_expense(db, expense_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    return obj


@router.delete("/{expense_id}")
def delete_expense_route(
    expense_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if not delete_expense(db, expense_id):
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    return {"detail": "Dépense supprimée"}
