# FruitMer - Système de Gestion de Poissonnerie

## 📋 Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Structure du projet](#structure-du-projet)
5. [Modules principaux](#modules-principaux)
6. [Base de données](#base-de-données)
7. [API REST](#api-rest)
8. [Interface utilisateur](#interface-utilisateur)
9. [Authentification et Autorisation](#authentification-et-autorisation)
10. [Guide d'utilisation](#guide-dutilisation)
11. [Améliorations planifiées](#améliorations-planifiées)

---

## Vue d'ensemble

**FruitMer** est une application web moderne de gestion complète pour une poissonnerie. Elle permet de gérer les produits, les fournitures, les ventes, les commandes de retour et les dépenses avec un système d'authentification et d'autorisation basé sur les rôles.

### Caractéristiques principales
- ✅ Gestion des produits (création, modification, suppression)
- ✅ Suivi des fournitures avec dates et fournisseurs
- ✅ Enregistrement des ventes et clients
- ✅ Gestion des commandes de retour et retours de marchandise
- ✅ Tableaux de bord KPI pour l'analyse des performances
- ✅ Authentification utilisateur sécurisée
- ✅ Contrôle d'accès basé sur les rôles (RBAC)
- ✅ API REST complète

---

## Architecture

### Stack technologique
- **Backend**: FastAPI (Python 3.8+)
- **Serveur d'application**: Uvicorn
- **Base de données**: SQLAlchemy ORM (SQLite / PostgreSQL)
- **Interface principale**: Streamlit
- **Frontend alternatif**: React (Vite)
- **Authentification**: JWT (python-jose)
- **Hachage des mots de passe**: Passlib

### Architecture en couches

```
┌─────────────────────────────────────┐
│       Interfaces utilisateur         │
│  (Streamlit UI + React Frontend)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        API REST FastAPI             │
│    (Endpoints et Routes)            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Services métier (Business Logic)│
│  (kpi_service, product_service...)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Schémas Pydantic (Validation)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Modèles SQLAlchemy (ORM)           │
│  (User, Product, Fourniture...)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Base de données                │
│  (SQLite ou PostgreSQL)             │
└─────────────────────────────────────┘
```

---

## Installation

### Prérequis
- Python 3.8 ou supérieur
- PostgreSQL ou SQLite
- Node.js 16+ (pour le frontend React optionnel)

### Étapes d'installation

1. **Cloner le repository et installer les dépendances Python**
```bash
cd /home/michel/code_python/fruitmer/projet
pip install -r requirements.txt
```

2. **Configurer les variables d'environnement**
```bash
export DATABASE_URL="postgresql://user:password@localhost/fruitmer"
# ou pour SQLite (défaut):
# export DATABASE_URL="sqlite:///./app.db"
export SECRET_KEY="your-secret-key-here"
export API_URL="http://127.0.0.1:8000"
```

3. **Initialiser la base de données**
```bash
# Les migrations Alembic sont disponibles
alembic upgrade head
```

4. **Démarrer l'API**
```bash
bash scripts/run_api.sh
# ou manuellement:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Démarrer l'interface Streamlit**
```bash
bash scripts/run_ui.sh
# ou manuellement:
streamlit run streamlit_app.py
```

6. **Installation du frontend React (optionnel)**
```bash
cd frontend
npm install
npm run dev
```

---

## Structure du projet

```
projet/
├── alembic/                          # Migrations de base de données
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                    # Fichiers de migration
├── app/                             # Application principale
│   ├── __init__.py
│   ├── config.py                    # Configuration de l'application
│   ├── database.py                  # Configuration SQLAlchemy
│   ├── main.py                      # Point d'entrée FastAPI
│   ├── models.py                    # Modèles SQLAlchemy
│   ├── api/                         # API REST endpoints
│   │   ├── deps.py                  # Dépendances injectées
│   │   ├── routes/                  # Routes organisées par entité
│   │   │   ├── auth.py              # Authentification
│   │   │   ├── products.py
│   │   │   ├── fournitures.py
│   │   │   ├── ventes.py
│   │   │   ├── commandes_retour.py
│   │   │   ├── users.py
│   │   │   ├── customers.py
│   │   │   ├── expenses.py
│   │   │   └── kpi.py
│   ├── schemas/                     # Schémas Pydantic (validation)
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── fourniture.py
│   │   ├── vente.py
│   │   ├── commande_retour.py
│   │   └── user.py
│   ├── services/                    # Logique métier
│   │   ├── product_service.py
│   │   ├── fourniture_service.py
│   │   ├── vente_service.py
│   │   ├── commande_retour_service.py
│   │   ├── kpi_service.py
│   │   └── user_service.py
│   └── core/
│       └── security.py              # Fonctions de sécurité
├── frontend/                        # Frontend React (optionnel)
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── contexts/
│   │   └── api/
│   └── ...
├── ui/                             # Interface Streamlit
│   ├── api_client.py               # Client API Streamlit
│   ├── session.py
│   ├── helpers.py
│   └── components/                 # Composants réutilisables
├── scripts/                        # Scripts utilitaires
│   ├── run_api.sh
│   ├── run_ui.sh
│   └── reset_db.py
├── streamlit_app.py               # Point d'entrée Streamlit
├── alembic.ini                    # Configuration Alembic
└── requirements.txt               # Dépendances Python
```

---

## Modules principaux

### 1. **Authentification (auth)**
- LOGIN / LOGOUT
- Génération de JWT tokens
- Validation des credentials
- Gestion des sessions

**Rôles disponibles:**
- `admin`: Accès complet
- `directeur`: Accès lectures + création KPI
- `read`: Accès lecture seule
- `write`: Accès lecture/écriture

### 2. **Gestion des Produits**
Gère le catalogue de produits avec:
- Nom, catégorie, prix d'achat de référence
- Stock en kg et seuil d'alerte
- Historique de création/modification
- Relations avec fournitures et ventes

### 3. **Fournitures (Supply Chain)**
Enregistrement des arrivages de marchandise:
- Produit associé, date d'arrivée
- Fournisseur, origine, quantité (kg)
- Prix unitaire (€/kg)
- Historique complet

### 4. **Ventes**
Documentation des ventes:
- Produit vendu, date de livraison
- Client/Restaurant, quantité et prix
- Lieu de livraison et contact
- Traçabilité de la fourniture utilisée

### 5. **Commandes de Retour**
Gestion des retours et invendus:
- Produit retourné, quantité
- Raison du retour
- Impacte sur les KPI (bénéfice net)

### 6. **Tableaux de Bord (KPI)**
Analyses et rapports:
- Total kg vendus par produit
- Durée de rotation des stocks
- Kg restant après vente
- Bénéfice global et net (après retours)
- Filtrage par produit et date d'arrivée

---

## Base de données

### Schéma des tables

#### **users**
```sql
id (PK) | email (UNIQUE) | full_name | hashed_password | role | disabled | created_at
```

#### **products**
```sql
id (PK) | nom (UNIQUE) | categorie | prix_achat_ref | stock_kg | 
seuil_alerte_kg | notes | created_at | updated_at
```

#### **fournitures**
```sql
id (PK) | product_id (FK) | nom_produit_texte | date_obtenu | 
origine | nom_fournisseur | kilo_produit | prix_par_kg | created_at
```

#### **ventes**
```sql
id (PK) | product_id (FK) | fourniture_id (FK) | nom_produit_texte | 
date_obtenu_fourniture | date_livraison | nom_ou_restaurant | 
kilo | prix | lieu | numero_telephone | created_at
```

#### **commandes_retour**
```sql
id (PK) | product_id (FK) | fourniture_id (FK) | kilo_retourne | 
raison | montant_remboursement | created_at
```

### Migrations Alembic
Les migrations sont versionnées et stockées dans `alembic/versions/`:
- `491f357c0d69_add_updated_at_column_to_products.py`
- `79b2ab93ebd5_description.py`
- `97914c9f4370_add_products_suppliers_customers_sales_.py`
- `aaaa6a45d4e0_remove_unique_constraints_depences.py`
- `b1c2d3e4f5a6_add_fournitures_ventes_commandes_retour.py`

---

## API REST

### URL de base
```
http://localhost:8000
```

### Endpoints principaux

#### **Authentication**
```
POST   /auth/login            - Connexion utilisateur
POST   /auth/logout           - Déconnexion
POST   /auth/refresh          - Renouvellement token
```

#### **Users**
```
GET    /users/me              - Récupérer profil utilisateur
POST   /users/                - Créer utilisateur (admin)
GET    /users/                - Lister utilisateurs (admin)
PUT    /users/{id}            - Modifier utilisateur
DELETE /users/{id}            - Supprimer utilisateur (admin)
POST   /users/{id}/change-password - Changer mot de passe
```

#### **Products**
```
GET    /products/             - Lister tous les produits
POST   /products/             - Créer produit
GET    /products/{id}         - Récupérer détails produit
PUT    /products/{id}         - Modifier produit
DELETE /products/{id}         - Supprimer produit
```

#### **Fournitures (Supply)**
```
GET    /fournitures/          - Lister fournitures
POST   /fournitures/          - Enregistrer arrivage
GET    /fournitures/{id}      - Détails fourniture
PUT    /fournitures/{id}      - Modifier fourniture
DELETE /fournitures/{id}      - Supprimer fourniture
```

#### **Ventes (Sales)**
```
GET    /ventes/               - Lister ventes
POST   /ventes/               - Créer vente
GET    /ventes/{id}           - Détails vente
PUT    /ventes/{id}           - Modifier vente
DELETE /ventes/{id}           - Supprimer vente
```

#### **Commandes Retour (Returns)**
```
GET    /commandes-retour/     - Lister retours
POST   /commandes-retour/     - Enregistrer retour
GET    /commandes-retour/{id} - Détails retour
PUT    /commandes-retour/{id} - Modifier retour
DELETE /commandes-retour/{id} - Supprimer retour
```

#### **KPI Dashboard**
```
GET    /kpi/summary           - Résumé KPI global
GET    /kpi/by-product        - KPI par produit
GET    /kpi/by-date           - KPI par date d'arrivée
GET    /kpi/filter            - KPI avec filtres (produit, date)
```

### Documentation interactive
```
GET    /docs                  - Swagger UI
GET    /redoc                 - ReDoc
```

---

## Interface utilisateur

### Streamlit (streamlit_app.py)

**Pages disponibles:**
1. **Produits** - CRUD complet des produits
2. **Fournitures** - Enregistrement des arrivages
3. **Ventes** - Saisie des ventes et clients
4. **Commandes Retour** - Gestion des retours
5. **Dashboard KPI** - Analyses et rapports

**Composants:**
- Barre latérale d'authentification
- Formulaires de saisie avec validation
- Tableaux affichant les données
- Graphiques d'analyse

### React Frontend (optionnel)

**Structure:**
- `App.jsx` - Composant racine
- `components/` - Composants réutilisables
  - Navbar.jsx
  - Sidebar.jsx
  - Modal.jsx
  - ProtectedRoute.jsx
  - ErrorBoundary.jsx
  - etc.
- `pages/` - Pages principales
- `contexts/` - Context API pour état global
- `api/client.js` - Client HTTP pour API

---

## Authentification et Autorisation

### Flux d'authentification

1. **Login**: Utilisateur envoie email + password
2. **Validation**: Vérification en BD, validation password
3. **JWT Token**: Génération d'un token JWT signé
4. **Stockage**: Client stocke le token
5. **Requêtes**: Token envoyé en header `Authorization: Bearer <token>`
6. **Validation**: Vérification token à chaque requête

### Rôles et permissions

| Rôle | Produits | Fournitures | Ventes | Retours | Users | KPI |
|------|----------|-------------|--------|---------|-------|-----|
| admin | ✅ C/R/U/D | ✅ C/R/U/D | ✅ C/R/U/D | ✅ C/R/U/D | ✅ C/R/U/D | ✅ R |
| directeur | ✅ R | ✅ R | ✅ R | ✅ R | ❌ | ✅ R |
| read | ✅ R | ✅ R | ✅ R | ✅ R | ❌ | ✅ R |
| write | ✅ C/R/U | ✅ C/R/U | ✅ C/R/U | ✅ R | ❌ | ❌ |

**Légende**: C=Créer, R=Lire, U=Modifier, D=Supprimer

### Utilisateurs par défaut
L'application crée automatiquement:
- `admin@fruitmer.com` (role: admin)
- `directeur@fruitmer.com` (role: directeur)

---

## Guide d'utilisation

### Pour l'administrateur
1. **Gestion des utilisateurs**: Créer, modifier ou supprimer les comptes
2. **Configuration des produits**: Ajouter/modifier produits et catégories
3. **Suivi des fournitures**: Vérifier toutes les entrées de marchandise
4. **Consultation KPI**: Accès à tous les tableaux de bord

### Pour le directeur
1. **Analyse KPI**: Consulter les performances par produit
2. **Filtrer par produit et date**: Analyser en détail les arrivages
3. **Suivi des retours**: Comprendre l'impact sur les marges
4. **Export de rapports**: Extraire les données pour analyse

### Pour les opérateurs (role: write)
1. **Saisie fournitures**: Enregistrer les arrivages quotidiens
2. **Saisie ventes**: Documenter chaque vente/livraison
3. **Retours**: Signaler les retours de marchandise
4. **Consultation**: Voir l'historique et les stocks

---

## Améliorations planifiées

### Phase 1: Features utilisateurs
- [x] Gestion des utilisateurs sur le backend
- [x] Changement de mot de passe utilisateur
- [x] Ajout/suppression utilisateurs par admin
- [ ] **Nouveau**: Reset de mot de passe oublié
- [ ] **Nouveau**: Historique d'accès utilisateur

### Phase 2: Restructuration pages
- [ ] **PRIORITÉ**: Transformer Dashboard en page de saisie de données
  - Page de saisie dédiée aux fournitures
  - Page de saisie dédiée aux ventes
  - Page de saisie dédiée aux retours
  - Affichage du nombre de saisies par jour
  - Aperçu des dernières saisies de la journée
- [ ] KPI Dashboard pour directeur/admin uniquement
  - Sélection de produit et date d'arrivée
  - Affichage des KPI spécifiques au produit
  - Calcul: total kg vendus, jours de rotation, kg restant, bénéfice net

### Phase 3: Améliorations UI
- [ ] Redesign Streamlit avec meilleure ergonomie
- [ ] Tableaux de bord interactifs (React)
- [ ] Graphiques d'analyse avancés
- [ ] Export PDF/Excel des rapports
- [ ] Mode sombre/clair

### Phase 4: Performance et données
- [ ] Caching des KPI pour performance
- [ ] Archivage des données anciennes
- [ ] Backup automatique de la BD
- [ ] Import/Export de données (CSV)

### Phase 5: Intégrations
- [ ] Intégration email (reminders, rapports)
- [ ] SMS notifications pour retours
- [ ] Sync avec système comptable
- [ ] API mobile (iOS/Android)

---

## Dépannage

### Erreurs courantes

**1. Connexion à la base de données**
```bash
# Vérifier les variables d'environnement
echo $DATABASE_URL

# Réinitialiser la BD
python scripts/reset_db.py
```

**2. Token JWT expiré**
- Recharger la page
- Se reconnecter
- Vérifier l'heure du serveur

**3. CORS erreurs**
- L'API accepte les origins: `["*"]`
- Vérifier `Access-Control-Allow-*` headers

**4. Migrations Alembic**
```bash
# Voir l'état des migrations
alembic current

# Appliquer les migrations
alembic upgrade head

# Annuler dernière migration (danger!)
alembic downgrade -1
```

---

## Contacts et support

- **Responsable projet**: Michel
- **Email**: michel@fruitmer.local
- **Documentation**: Ce fichier
- **Issues**: À reporter dans le système de suivi projet

---

**Dernière mise à jour**: Septembre 2026
**Version**: 3.1.0