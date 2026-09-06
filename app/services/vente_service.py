from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Fourniture, Vente
from ..schemas.vente import VenteCreate, VenteUpdate
from .product_service import adjust_stock, get_or_create_product_by_name


def list_ventes(db: Session) -> List[Vente]:
    return db.query(Vente).order_by(Vente.date_livraison.desc(), Vente.id.desc()).all()


def get_vente(db: Session, vente_id: int) -> Optional[Vente]:
    return db.query(Vente).filter(Vente.id == vente_id).first()


def create_vente(db: Session, data: VenteCreate) -> Vente:
    payload = data.model_dump()
    nom_texte = payload.get("nom_produit_texte") or ""
    product_id = payload.get("product_id")
    fourniture_id = payload.get("fourniture_id")

    if not product_id and nom_texte:
        prod = get_or_create_product_by_name(db, nom_texte)
        payload["product_id"] = prod.id
        product_id = prod.id

    # If fourniture_id is not specified, auto-link to the most recent lot for this product
    if not fourniture_id and product_id:
        latest_fourn = (
            db.query(Fourniture)
            .filter(Fourniture.product_id == product_id)
            .order_by(Fourniture.date_obtenu.desc(), Fourniture.id.desc())
            .first()
        )
        if latest_fourn:
            payload["fourniture_id"] = latest_fourn.id
            if not payload.get("date_obtenu_fourniture"):
                payload["date_obtenu_fourniture"] = latest_fourn.date_obtenu

    obj = Vente(**payload)
    db.add(obj)
    if obj.product_id and obj.kilo:
        adjust_stock(db, obj.product_id, -float(obj.kilo))
    db.commit()
    db.refresh(obj)
    return obj


def update_vente(
    db: Session, vente_id: int, data: VenteUpdate
) -> Optional[Vente]:
    existing = get_vente(db, vente_id)
    if existing is None:
        return None
    old_product_id = existing.product_id
    old_kilo = existing.kilo or 0.0
    new_data = data.model_dump(exclude_unset=True)
    new_product_id = new_data.get("product_id", old_product_id)
    new_kilo = new_data.get("kilo", old_kilo)
    if old_product_id and old_kilo:
        adjust_stock(db, old_product_id, +float(old_kilo))
    if new_product_id and new_kilo:
        adjust_stock(db, new_product_id, -float(new_kilo))
    for k, v in new_data.items():
        setattr(existing, k, v)
    db.commit()
    db.refresh(existing)
    return existing


def delete_vente(db: Session, vente_id: int) -> bool:
    existing = get_vente(db, vente_id)
    if existing is None:
        return False
    if existing.product_id and existing.kilo:
        adjust_stock(db, existing.product_id, +float(existing.kilo))
    db.delete(existing)
    db.commit()
    return True
