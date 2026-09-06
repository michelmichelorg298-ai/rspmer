from typing import Dict, List, Optional
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..models import CommandeRetour, Fourniture, Product, Vente


def list_lots(db: Session, product_id: Optional[int] = None) -> List[Dict]:
    query = db.query(Fourniture)
    if product_id:
        query = query.filter(Fourniture.product_id == product_id)
    fournitures = query.order_by(Fourniture.date_obtenu.desc(), Fourniture.id.desc()).all()
    
    results = []
    for f in fournitures:
        results.append({
            "id": f.id,
            "product_id": f.product_id,
            "nom_produit_texte": f.nom_produit_texte,
            "date_obtenu": f.date_obtenu,
            "nom_fournisseur": f.nom_fournisseur,
            "origine": f.origine,
            "kilo_produit": f.kilo_produit,
            "prix_par_kg": f.prix_par_kg,
        })
    return results


def get_lot_kpi_analytics(db: Session, fourniture_id: int) -> Optional[Dict]:
    fourniture = db.query(Fourniture).filter(Fourniture.id == fourniture_id).first()
    if not fourniture:
        return None

    # Fetch sales for this fourniture
    sales_conditions = [Vente.fourniture_id == fourniture.id]
    if fourniture.product_id:
        sales_conditions.append(
            and_(
                Vente.fourniture_id.is_(None),
                Vente.product_id == fourniture.product_id,
                Vente.date_obtenu_fourniture == fourniture.date_obtenu
            )
        )
    sales = db.query(Vente).filter(or_(*sales_conditions)).all()

    # Fetch returns for this fourniture
    returns_conditions = [CommandeRetour.fourniture_id == fourniture.id]
    if fourniture.product_id:
        returns_conditions.append(
            and_(
                CommandeRetour.fourniture_id.is_(None),
                CommandeRetour.product_id == fourniture.product_id,
                CommandeRetour.origine == fourniture.origine
            )
        )
    returns = db.query(CommandeRetour).filter(or_(*returns_conditions)).all()

    total_kg_vendus = sum(v.kilo for v in sales)
    total_kg_retours = sum(r.kilo for r in returns)
    chiffre_affaires = sum(v.kilo * v.prix for v in sales)
    cout_total_achat = fourniture.kilo_produit * fourniture.prix_par_kg
    benefice_net = chiffre_affaires - cout_total_achat
    marge_pct = round(((chiffre_affaires - cout_total_achat) / cout_total_achat) * 100, 1) if cout_total_achat > 0 else 0.0

    est_tout_vendu = total_kg_vendus >= fourniture.kilo_produit
    kilo_restant = max(0.0, fourniture.kilo_produit - total_kg_vendus)

    jours_pour_tout_vendre = None
    if est_tout_vendu and sales:
        dates_livraison = [v.date_livraison for v in sales if v.date_livraison]
        if dates_livraison:
            max_date = max(dates_livraison)
            delta = (max_date - fourniture.date_obtenu).days
            jours_pour_tout_vendre = max(1, delta)

    retours_liste = []
    for r in returns:
        retours_liste.append({
            "id": r.id,
            "kilo": r.kilo,
            "cause": r.cause,
            "origine": r.origine,
            "date": r.created_at.strftime("%Y-%m-%d") if r.created_at else None
        })

    return {
        "fourniture": {
            "id": fourniture.id,
            "product_id": fourniture.product_id,
            "nom_produit_texte": fourniture.nom_produit_texte,
            "date_obtenu": fourniture.date_obtenu,
            "nom_fournisseur": fourniture.nom_fournisseur,
            "origine": fourniture.origine,
            "kilo_produit": fourniture.kilo_produit,
            "prix_par_kg": fourniture.prix_par_kg,
            "cout_total_achat": cout_total_achat,
        },
        "kpis": {
            "total_kg_vendus": round(total_kg_vendus, 2),
            "total_kg_retours": round(total_kg_retours, 2),
            "est_tout_vendu": est_tout_vendu,
            "kilo_restant": round(kilo_restant, 2),
            "jours_pour_tout_vendre": jours_pour_tout_vendre,
            "chiffre_affaires": round(chiffre_affaires, 2),
            "benefice_net": round(benefice_net, 2),
            "marge_pct": marge_pct,
            "commandes_retournees": retours_liste,
            "nb_ventes": len(sales),
            "nb_retours": len(returns),
        }
    }
