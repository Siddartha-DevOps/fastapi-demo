from scipy.optimize import minimize  # make sure this is imported
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib  # for loading ML model
from typing import Optional
from scipy.optimize import minimize


class MixConstraints(BaseModel):
    min_fine_agg_kg: Optional[float] = None
    max_coarse_agg_kg: Optional[float] = None


class OptimizeRequest(BaseModel):
    target_strength_mpa: float
    max_cement_kg: float
    max_water_cement_ratio: float
    max_admixture_kg: float
    constraints: Optional[MixConstraints] = None


@app.post("/optimize_mix/")
async def optimize_mix(data: OptimizeRequest):
    # Include your optimization logic here as explained earlier
    def predict_strength(x):

        cement, water, fine_agg, coarse_agg, admixture = x
        wcr = water / cement if cement != 0 else 0
        strength = 100 - (wcr * 50) + (admixture * 0.5)
        return strength

    def cost_function(x):

        cement, water, fine_agg, coarse_agg, admixture = x
        return cement * 0.1 + water * 0.05 + fine_agg * \
            0.02 + coarse_agg * 0.015 + admixture * 0.2

    def strength_constraint(x):

        return predict_strength(x) - data.target_strength_mpa

    bounds = [
        (0, data.max_cement_kg),
        (0, data.max_cement_kg * data.max_water_cement_ratio),
        (0, 1000),
        (0, 1500),
        (0, data.max_admixture_kg)
    ]

x0 = [
    data.max_cement_kg *
    0.8,
    data.max_cement_kg *
    0.4,
    500,
    1000,
    data.max_admixture_kg *
    0.5]
cons = {'type': 'ineq', 'fun': strength_constraint}

if data.constraints:
    if data.constraints.min_fine_agg_kg is not None:
        cons = [cons, {'type': 'ineq', 'fun': lambda x: x[2] -
                       data.constraints.min_fine_agg_kg}]
    if data.constraints.max_coarse_agg_kg is not None:
        cons = [
            cons, {
                'type': 'ineq', 'fun': lambda x: data.constraints.max_coarse_agg_kg - x[3]}]


result = minimize(
    cost_function,
    x0,
    bounds=bounds,
    constraints=cons,
    method='SLSQP')

if not result.success:
    raise HTTPException(
        status_code=400,
        detail="Optimization failed: " +
        result.message)

cement, water, fine_agg, coarse_agg, admixture = result.x
optimized_mix = {
    "cement_kg": round(cement, 2),
    "water_kg": round(water, 2),
    "fine_agg_kg": round(fine_agg, 2),
    "coarse_agg_kg": round(coarse_agg, 2),
    "admixture_kg": round(admixture, 2)
}

predicted_strength = predict_strength(result.x)
estimated_cost = cost_function(result.x)
# missing indentation here
  return {
        "optimized_mix": optimized_mix,
        "predicted_strength_mpa": round(predicted_strength, 2),
        "estimated_cost": round(estimated_cost, 2),
        "message": "Optimization successful"
  }


app = FastAPI(title="Concrete Mix Optimization API")
# Allow CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for concrete mix input


class MixInput(BaseModel):
    cement_kg: float
    water_kg: float
    fine_agg_kg: float
    coarse_agg_kg: float
    admixture_kg: float
    age_days: int


# Load your pre-trained AI model
# Use correct path or dummy model for testing
try:
    model = joblib.load("models/rf_concrete_strength_model.pkl")
except FileNotFoundError:
    class DummyModel:
        def predict(self, X):
            return [30.0]  # dummy strength
    model = DummyModel()

# Root endpoint


@app.get("/")
async def read_root():
    return {"message": "Welcome to Concrete Mix Optimization API"}

# Predict concrete strength endpoint


@app.post("/predict_strength/")
async def predict_strength(mix: MixInput):
    water_cement_ratio = mix.water_kg / mix.cement_kg
    features = [[
        water_cement_ratio,
        mix.water_kg,
        mix.fine_agg_kg,
        mix.coarse_agg_kg,
        mix.admixture_kg,
        mix.age_days
    ]]
    prediction = model.predict(features)[0]
    return {"predicted_strength_mpa": round(prediction, 2)}


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
