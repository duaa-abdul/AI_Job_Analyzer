from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from graph import analyze_job

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="A1 Job Description Analyzer")

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


class AnalyzeRequest(BaseModel):
    job_description: str = Field(
        min_length=1,
        max_length=20000,
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.post("/api/analyze")
async def analyze(request_data: AnalyzeRequest):
    description = request_data.job_description.strip()

    if len(description) < 30:
        raise HTTPException(
            status_code=400,
            detail="Please enter at least 30 characters.",
        )

    try:
        report = analyze_job(description)
        return {"success": True, "report": report}

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"Job analysis error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis failed. Check your Groq API key, "
                "model availability, and server terminal."
            ),
        ) from exc
