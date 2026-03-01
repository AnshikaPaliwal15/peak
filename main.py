import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# -------------------------------
# Optional Spark (Fabric Only)
# -------------------------------
spark = None
try:
    from pyspark.sql import SparkSession, Row

    spark = SparkSession.builder \
        .appName("EnergyCalculation") \
        .getOrCreate()

    print("Spark initialized successfully.")
except Exception as e:
    print(f"Spark not available: {str(e)}")
    spark = None


# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(title="Energy Calculation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Request Model
# -------------------------------
class EnergyInput(BaseModel):
    generated_energy: float = Field(..., ge=0)
    total_discharge: float = Field(..., ge=0)
    total_excess: float = Field(..., ge=0)


# -------------------------------
# Calculation Endpoint
# -------------------------------
@app.post("/calculate")
async def calculate_energy(data: EnergyInput):

    if (data.total_discharge + data.total_excess) > data.generated_energy:
        raise HTTPException(
            status_code=400,
            detail="Discharge + Excess cannot exceed Generated Energy."
        )

    loss_kwh = data.generated_energy - data.total_discharge - data.total_excess

    generated_mwh = data.generated_energy / 1000
    discharge_mwh = data.total_discharge / 1000
    excess_mwh = data.total_excess / 1000
    loss_mwh = loss_kwh / 1000

    timestamp = datetime.utcnow()

    result = {
        "Generated_Energy_kWh": data.generated_energy,
        "Total_Discharge_kWh": data.total_discharge,
        "Total_Excess_kWh": data.total_excess,
        "Loss_And_Curtailed_kWh": loss_kwh,
        "Generated_Energy_MWh": generated_mwh,
        "Total_Discharge_MWh": discharge_mwh,
        "Total_Excess_MWh": excess_mwh,
        "Loss_And_Curtailed_MWh": loss_mwh,
        "Timestamp": str(timestamp)
    }

    # Save to Lakehouse (only if running inside Fabric Spark)
    if spark:
        try:
            row = Row(**result)
            df = spark.createDataFrame([row])
            df.write.mode("append").saveAsTable("energy_summary")
            print("Saved to Lakehouse")
        except Exception as e:
            print(f"Lakehouse write error: {str(e)}")

    return result


# -------------------------------
# Serve Frontend
# -------------------------------
@app.get("/")
async def serve_home():
    return FileResponse("index.html")


app.mount("/static", StaticFiles(directory="."), name="static")
