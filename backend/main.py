from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import orders, market_data, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Trading Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)
app.include_router(market_data.router)
app.include_router(admin.router)

@app.get("/health")
def health():
    return {"status": "ok"}