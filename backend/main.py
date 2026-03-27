from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

from analyzer import analyze_funds

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    threshold: float = Form(...),
    include_revenue: bool = Form(False)
):
    try:
        contents = await file.read()
        filename = file.filename.lower()

        # ✅ Handle file type
        if filename.endswith(".xlsx"):
            data_file = io.BytesIO(contents)
            df = pd.read_excel(data_file)

        elif filename.endswith(".csv"):
            data_file = io.StringIO(contents.decode("utf-8"))
            df = pd.read_csv(data_file)

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload .csv or .xlsx"
            )

        # Convert percentage → decimal
        threshold_decimal = threshold / 100

        result = analyze_funds(
            df,
            threshold=threshold_decimal,
            include_revenue=include_revenue
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )