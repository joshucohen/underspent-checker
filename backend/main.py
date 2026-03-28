from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
        filename = file.filename.lower()

        # ✅ Enforce Excel only
        if not filename.endswith(".xlsx"):
            raise HTTPException(
                status_code=400,
                detail="Only Excel (.xlsx) files are supported. File must contain 3 sheets (one per year)."
            )

        contents = await file.read()
        excel_file = io.BytesIO(contents)

        # Convert percentage → decimal
        threshold_decimal = threshold / 100

        result = analyze_funds(
            excel_file,
            threshold=threshold_decimal,
            include_revenue=include_revenue
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )