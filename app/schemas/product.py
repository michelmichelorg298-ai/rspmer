from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    nom: str
    categorie: str = "Autre"
    prix_achat_ref: Optional[float] = None
    stock_kg: float = 0.0
    seuil_alerte_kg: float = 0.0
    notes: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
