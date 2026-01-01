from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import codes, agents

app = FastAPI(title="DefenderC2-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(codes.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
