from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CommandeRetourBase(BaseModel):
    product_id: Optional[int] = None
    nom_produit_texte: str
    fourniture_id: Optional[int] = None
    origine: str
    kilo: float
    cause: str


class CommandeRetourCreate(CommandeRetourBase):
    pass


class CommandeRetourUpdate(BaseModel):
    product_id: Optional[int] = None
    nom_produit_texte: Optional[str] = None
    fourniture_id: Optional[int] = None
    origine: Optional[str] = None
    kilo: Optional[float] = None
    cause: Optional[str] = None


class CommandeRetourResponse(CommandeRetourBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
