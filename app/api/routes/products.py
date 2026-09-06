from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...api.deps import require_role
from ...database import get_db
from ...models import User
from ...schemas.product import ProductCreate, ProductResponse, ProductUpdate
from ...services.product_service import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
def read_products(
    only_low_stock: bool = False,
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    return list_products(db, only_low_stock=only_low_stock)


@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int,
    current_user: User = Depends(require_role("read")),
    db: Session = Depends(get_db),
):
    obj = get_product(db, product_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return obj


@router.post("", response_model=ProductResponse)
def create_product_route(
    data: ProductCreate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    return create_product(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_route(
    product_id: int,
    data: ProductUpdate,
    current_user: User = Depends(require_role("read_write")),
    db: Session = Depends(get_db),
):
    obj = update_product(db, product_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return obj


@router.delete("/{product_id}")
def delete_product_route(
    product_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if not delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return {"detail": "Produit supprimé"}
