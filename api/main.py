from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(
    title="Obituary Content API",
    description="API for fetching automated, SEO-optimized obituary content.",
    version="1.0.0"
)

# Allow CORS for plugin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Obituary Content API"}

# To run locally: uvicorn main:app --reload
