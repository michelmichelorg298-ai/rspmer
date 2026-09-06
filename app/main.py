from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import auth, products, fournitures, ventes, commandes_retour, users, kpi
from .database import Base, SessionLocal, engine
from .services.user_service import ensure_default_users


def create_app() -> FastAPI:
    app = FastAPI(title="Gestion Poissonnerie", version="3.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(kpi.router)
    app.include_router(products.router)
    app.include_router(fournitures.router)
    app.include_router(ventes.router)
    app.include_router(commandes_retour.router)

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            ensure_default_users(db)
        finally:
            db.close()

    @app.get("/")
    def read_root():
        return {"status": "API is running"}

    return app


app = create_app()
