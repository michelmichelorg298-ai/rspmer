from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VenteBase(BaseModel):
    product_id: Optional[int] = None
    nom_produit_texte: str
    fourniture_id: Optional[int] = None
    date_obtenu_fourniture: Optional[date] = None
    date_livraison: date
    nom_ou_restaurant: str
    kilo: float
    prix: float
    lieu: Optional[str] = None
    numero_telephone: Optional[str] = None


class VenteCreate(VenteBase):
    pass


class VenteUpdate(BaseModel):
    product_id: Optional[int] = None
    nom_produit_texte: Optional[str] = None
    fourniture_id: Optional[int] = None
    date_obtenu_fourniture: Optional[date] = None
    date_livraison: Optional[date] = None
    nom_ou_restaurant: Optional[str] = None
    kilo: Optional[float] = None
    prix: Optional[float] = None
    lieu: Optional[str] = None
    numero_telephone: Optional[str] = None


class VenteResponse(VenteBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
