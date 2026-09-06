from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, index=True, nullable=False)
    full_name = Column(String(256), nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String(50), nullable=False, default="read")
    disabled = Column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    categorie: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Autre"
    )
    prix_achat_ref: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    stock_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    seuil_alerte_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    supply_items: Mapped[List["Fourniture"]] = relationship(back_populates="product")
    direct_sale_items: Mapped[List["Vente"]] = relationship(back_populates="product")
    return_items: Mapped[List["CommandeRetour"]] = relationship(back_populates="product")


class Fourniture(Base):
    __tablename__ = "fournitures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    nom_produit_texte: Mapped[str] = mapped_column(String(150), nullable=False)
    date_obtenu: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    origine: Mapped[str] = mapped_column(String(200), nullable=False)
    nom_fournisseur: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    kilo_produit: Mapped[float] = mapped_column(Float, nullable=False)
    prix_par_kg: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped[Optional[Product]] = relationship(back_populates="supply_items")
    vente_items: Mapped[List["Vente"]] = relationship(back_populates="fourniture")
    retour_items: Mapped[List["CommandeRetour"]] = relationship(back_populates="fourniture")


class Vente(Base):
    __tablename__ = "ventes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    nom_produit_texte: Mapped[str] = mapped_column(String(150), nullable=False)
    fourniture_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("fournitures.id", ondelete="SET NULL"), nullable=True, index=True
    )
    date_obtenu_fourniture: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    date_livraison: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    nom_ou_restaurant: Mapped[str] = mapped_column(String(250), nullable=False, index=True)
    kilo: Mapped[float] = mapped_column(Float, nullable=False)
    prix: Mapped[float] = mapped_column(Float, nullable=False)
    lieu: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    numero_telephone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped[Optional[Product]] = relationship(back_populates="direct_sale_items")
    fourniture: Mapped[Optional[Fourniture]] = relationship(back_populates="vente_items")


class CommandeRetour(Base):
    __tablename__ = "commandes_retour"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    nom_produit_texte: Mapped[str] = mapped_column(String(150), nullable=False)
    fourniture_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("fournitures.id", ondelete="SET NULL"), nullable=True, index=True
    )
    origine: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    kilo: Mapped[float] = mapped_column(Float, nullable=False)
    cause: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped[Optional[Product]] = relationship(back_populates="return_items")
    fourniture: Mapped[Optional[Fourniture]] = relationship(back_populates="retour_items")
