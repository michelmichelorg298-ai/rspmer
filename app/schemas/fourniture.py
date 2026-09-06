from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FournitureBase(BaseModel):
    product_id: Optional[int] = None
    nom_produit_texte: str
    date_obtenu: date
    origine: str
    nom_fournisseur: str
    kilo_produit: float
    prix_par_kg: float


class FournitureCreate(FournitureBase):
    pass


class FournitureUpdate(BaseModel):
    product_id: Optional[int] = None
    nom_produit_texte: Optional[str] = None
    date_obtenu: Optional[date] = None
    origine: Optional[str] = None
    nom_fournisseur: Optional[str] = None
    kilo_produit: Optional[float] = None
    prix_par_kg: Optional[float] = None


class FournitureResponse(FournitureBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
