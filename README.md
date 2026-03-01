# Energy Calculation Dashboard

A professional dashboard for calculating energy performance metrics and storing them in Microsoft Fabric Lakehouse.

## Features
- **Professional UI**: Minimalist corporate design with a soft blue/teal theme.
- **Real-time Validation**: Prevents negative values and logical errors (Discharge + Excess > Generated).
- **FastAPI Backend**: Efficient calculation and API handling.
- **Fabric Lakehouse Storage**: Automatically saves results to the `energy_summary` Lakehouse table using Spark DataFrames.
- **Metric Conversion**: Automatically converts all kWh values to MWh.

## Project Structure
- `index.html`: Dashboard layout and input forms.
- `style.css`: Modern, responsive corporate styling.
- `script.js`: Frontend logic, UI updates, and backend API integration.
- `main.py`: FastAPI server and Microsoft Fabric storage logic.
- `requirements.txt`: Python package dependencies.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.9+ and Spark (if running locally) installed.
*Note: In the Microsoft Fabric environment, Spark is already configured.*

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python main.py
```
The server will start at `http://localhost:8000`.

## Calculation Formula
The application calculates "Loss and Curtailed Energy" using the following formula:
`Loss_And_Curtailed_kWh = Generated_Energy_kWh - Total_Discharge_kWh - Total_Excess_kWh`
All values are converted to MWh by dividing the kWh value by 1000.

## Microsoft Fabric Integration
The system uses the `pyspark` library to write to Lakehouse. It appends a new record to the `energy_summary` table with the following columns:
- `Generated_Energy_kWh`: Energy generated in kWh.
- `Total_Discharge_kWh`: Energy discharged from storage in kWh.
- `Total_Excess_kWh`: Excess energy generated in kWh.
- `Loss_And_Curtailed_kWh`: Difference (the "loss").
- `Generated_Energy_MWh` etc.: Same values converted to MWh.
- `Timestamp`: Datetime record of the calculation.
