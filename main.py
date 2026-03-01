import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os

# Try to import and initialize Spark (standard in Microsoft Fabric Spark environments)
spark = None
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import Row
    # In Fabric, spark session is usually pre-initialized. 
    # If not, let's create a builder for local/environment context.
    spark = SparkSession.builder \
        .appName("EnergyCalculation") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    print("Spark initialized successfully.")
except Exception as e:
    # On local Windows machines without proper Hadoop/Java setup, this often fails.
    # We catch all exceptions here to ensure the API still runs for the UI.
    print(f"Warning: Spark could not be initialized ({str(e)}). Result persistence to Lakehouse will be skipped in this environment.")
    spark = None

app = FastAPI(title="Energy Calculation API")

# Add CORS middleware to prevent browser blocking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for incoming request
class EnergyInput(BaseModel):
    generated_energy: float = Field(..., ge=0)
    total_discharge: float = Field(..., ge=0)
    total_excess: float = Field(..., ge=0)

# POST endpoint for calculation
@app.post("/calculate")
async def calculate_energy(data: EnergyInput):
    # Validation: discharge + excess > generated
    if (data.total_discharge + data.total_excess) > data.generated_energy:
        raise HTTPException(
            status_code=400, 
            detail="Total discharge and total excess cannot exceed generated energy."
        )

    # 1. Perform kWh calculations
    loss_and_curtailed_kwh = data.generated_energy - data.total_discharge - data.total_excess
    
    # 2. Perform MWh calculations (Value / 1000)
    generated_mwh = data.generated_energy / 1000.0
    discharge_mwh = data.total_discharge / 1000.0
    excess_mwh = data.total_excess / 1000.0
    loss_mwh = loss_and_curtailed_kwh / 1000.0
    
    timestamp = datetime.now()

    # Result dictionary
    result = {
        "Generated_Energy_kWh": data.generated_energy,
        "Total_Discharge_kWh": data.total_discharge,
        "Total_Excess_kWh": data.total_excess,
        "Loss_And_Curtailed_kWh": loss_and_curtailed_kwh,
        "Generated_Energy_MWh": generated_mwh,
        "Total_Discharge_MWh": discharge_mwh,
        "Total_Excess_MWh": excess_mwh,
        "Loss_And_Curtailed_MWh": loss_mwh,
        "Timestamp": str(timestamp)
    }

    # 3. Store in Microsoft Fabric Lakehouse Table
    if spark:
        try:
            row = Row(
                Generated_Energy_kWh=float(data.generated_energy),
                Total_Discharge_kWh=float(data.total_discharge),
                Total_Excess_kWh=float(data.total_excess),
                Loss_And_Curtailed_kWh=float(loss_and_curtailed_kwh),
                Generated_Energy_MWh=float(generated_mwh),
                Total_Discharge_MWh=float(discharge_mwh),
                Total_Excess_MWh=float(excess_mwh),
                Loss_And_Curtailed_MWh=float(loss_mwh),
                Timestamp=timestamp
            )
            df = spark.createDataFrame([row])
            df.write.mode("append").saveAsTable("energy_summary")
            print("Successfully saved to Lakehouse table: energy_summary")
        except Exception as e:
            print(f"Error saving to Lakehouse: {str(e)}")
    else:
        print("Data persistence skipped (Spark not available).")

    return result

# Serve Frontend
@app.get("/")
async def read_index():
    return FileResponse("index.html")

# Mount everything in the current directory as static files (from the root)
# Put this AFTER other routes so it doesn't mask /calculate or /
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    # Ensure port 8000 is used
    uvicorn.run(app, host="0.0.0.0", port=8000)
