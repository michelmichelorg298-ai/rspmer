from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Product
from ..schemas.product import ProductCreate, ProductUpdate


def list_products(db: Session, only_low_stock: bool = False) -> List[Product]:
    q = db.query(Product)
    if only_low_stock:
        q = q.filter(Product.stock_kg <= Product.seuil_alerte_kg)
    return q.order_by(Product.nom.asc()).all()


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_nom(db: Session, nom: str) -> Optional[Product]:
    if not nom or not nom.strip():
        return None
    return db.query(Product).filter(Product.nom.ilike(nom.strip())).first()


def get_or_create_product_by_name(
    db: Session,
    nom: str,
    initial_stock: float = 0.0,
    prix_achat_ref: Optional[float] = None,
) -> Product:
    existing = get_product_by_nom(db, nom)
    if existing:
        return existing
    new_prod = Product(
        nom=nom.strip(),
        categorie="Poisson",
        stock_kg=initial_stock,
        prix_achat_ref=prix_achat_ref,
        seuil_alerte_kg=5.0,
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod


def create_product(db: Session, data: ProductCreate) -> Product:
    obj = Product(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Optional[Product]:
    obj = get_product(db, product_id)
    if obj is None:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_product(db: Session, product_id: int) -> bool:
    obj = get_product(db, product_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True


def adjust_stock(db: Session, product_id: int, delta_kg: float) -> Optional[Product]:
    """Ajoute delta_kg au stock (négatif = sortie)."""
    obj = get_product(db, product_id)
    if obj is None:
        return None
    obj.stock_kg = round(float(obj.stock_kg or 0.0) + float(delta_kg), 3)
    db.add(obj)
    return obj
