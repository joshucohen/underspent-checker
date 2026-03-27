from fastapi import FastAPI, UploadFile, File, Form
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
    threshold: float = Form(...),   # user sends percentage (e.g., 50)
    include_revenue: bool = Form(False)
):
    contents = await file.read()

    # Convert Excel file
    excel_file = io.BytesIO(contents)

    # Convert percentage → decimal
    threshold_decimal = threshold / 100

    result = analyze_funds(
        excel_file,
        threshold=threshold_decimal,
        include_revenue=include_revenue
    )

    return result