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
        # 🔴 Validate file presence
        if not file or not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded. Please upload a valid Excel (.xlsx) file."
            )

        filename = file.filename.lower()

        # 🔴 Enforce Excel only
        if not filename.endswith(".xlsx"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only Excel (.xlsx) files are supported."
            )

        # 🔴 Validate threshold
        if threshold < 0 or threshold > 100:
            raise HTTPException(
                status_code=400,
                detail="Threshold must be between 0 and 100."
            )

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        excel_file = io.BytesIO(contents)

        # Convert percentage → decimal
        threshold_decimal = threshold / 100

        result = analyze_funds(
            excel_file,
            threshold=threshold_decimal,
            include_revenue=include_revenue
        )

        return result

    except HTTPException:
        # 🔁 Pass through clean errors
        raise

    except ValueError as e:
        # 🔴 Expected validation errors from analyzer
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:
        # 🔴 Catch-all (don’t expose internals)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please check your file format and try again."
        )