from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Concrete Mix Optimization API")

origins = ["*"]  # Allows all origins, for local dev only. For production, specify explicit URLs.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # List of allowed origins or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"]               # Allow all request headers
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to concrete Mix Optimization API"}

# Pydantic model for concrete mix input
class MixInput(BaseModel):
    cement_kg: float
    water_kg: float
    fine_agg_kg: float
    coarse_agg_kg: float
    admixture_kg: float
    age_days: int

# Predict concrete strength (dummy logic for now)
@app.post("/predict_strength/")
async def predict_strength(mix: MixInput):
    # Dummy formula for testing
    predicted_strength = (mix.cement_kg * 0.5) + (mix.water_kg * 0.3)
    return {"predicted_strength_mpa": predicted_strength}

# Optional: Add future endpoints like mix optimization
# class OptimizeInput(BaseModel):
#     target_strength: float
#     age_days: int
#
# @app.post("/optimize_mix/")
# async def optimize_mix(opt: OptimizeInput):
#     # Replace with AI/ML model logic
#     optimized_mix = {"cement_kg": 300, "water_kg": 150}  # example
#     return {"optimized_mix": optimized_mix}
