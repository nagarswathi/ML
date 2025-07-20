from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_and_sum_food(csv_bytes):
    # Read file into DataFrame
    content = io.StringIO(csv_bytes.decode("utf-8", errors="ignore"))
    df = pd.read_csv(content)

    # Clean column names (remove spaces, unify case)
    df.columns = df.columns.str.strip().str.lower()

    # Find likely column names
    category_col = next((col for col in df.columns if "category" in col), None)
    amount_col = next((col for col in df.columns if "amount" in col or "expense" in col or "spent" in col), None)

    if not category_col or not amount_col:
        return None

    # Strip and lowercase categories
    df[category_col] = df[category_col].astype(str).str.strip().str.lower()

    # Clean amount column (remove commas, convert to float)
    df[amount_col] = (
        df[amount_col]
        .astype(str)
        .str.replace(",", "")
        .str.extract(r"([\d.]+)")
        .astype(float)
    )

    # Filter for "food"
    total_food = df[df[category_col] == "food"][amount_col].sum()

    return round(float(total_food), 2)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    result = clean_and_sum_food(content)
    if result is None:
        return JSONResponse(status_code=400, content={"error": "Could not find required columns."})
    
    return {
        "answer": result,
        "email": "21f1000509@ds.study.iitm.ac.in",
        "exam": "tds-2025-05-roe"
    }
