import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class EnergyInput(BaseModel):
    generated_energy: float = Field(..., ge=0)
    total_discharge: float = Field(..., ge=0)
    total_excess: float = Field(..., ge=0)

@app.post("/calculate")
async def calculate_energy(data: EnergyInput):
    loss_kwh = data.generated_energy - data.total_discharge - data.total_excess
    return {
        "Generated_Energy_kWh": data.generated_energy,
        "Total_Discharge_kWh": data.total_discharge,
        "Total_Excess_kWh": data.total_excess,
        "Loss_And_Curtailed_kWh": loss_kwh,
        "Generated_Energy_MWh": data.generated_energy / 1000.0,
        "Total_Discharge_MWh": data.total_discharge / 1000.0,
        "Total_Excess_MWh": data.total_excess / 1000.0,
        "Loss_And_Curtailed_MWh": loss_kwh / 1000.0,
    }

# Explicit routes for static assets to avoid path issues on Azure
@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/style.css")
async def read_css():
    return FileResponse("style.css", media_type="text/css")

@app.get("/script.js")
async def read_js():
    return FileResponse("script.js", media_type="application/javascript")

# Fallback for other files
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
