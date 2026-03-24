"""
Professors API
RESTful API for querying professor data from RateMyProfessors
Supports: De Anza College, UC San Diego
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import json
import os
import time

@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_data()
    yield

app = FastAPI(
    title="College Professors API",
    description="API for querying professor ratings and reviews from De Anza College and UC San Diego",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Data files per school
DATA_FILES = {
    "deanza": "rmp_deanza_all_professors.json",
    "ucsd":   "rmp_ucsd_all_professors.json",
}

# In-memory store: each entry has a "School" field added
professors_data: List[dict] = []


def load_data():
    """Load professor data from all school JSON files."""
    global professors_data
    professors_data = []

    for school_key, filename in DATA_FILES.items():
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                rows = json.load(f)
            for row in rows:
                row["School"] = school_key   # tag each record with its school
            professors_data.extend(rows)
            print(f"Loaded {len(rows)} professors from {filename} (school={school_key})")
        else:
            print(f"Warning: {filename} not found — skipping.")

    print(f"Total professors loaded: {len(professors_data)}")


@app.post("/reload")
async def reload_data():
    """Reload professor data from all JSON files."""
    try:
        load_data()
        return {
            "status": "success",
            "message": f"Data reloaded. {len(professors_data)} professors loaded.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading data: {str(e)}")


@app.get("/")
async def root():
    """Serve the web interface."""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {
        "message": "College Professors API",
        "version": "2.0.0",
        "schools": list(DATA_FILES.keys()),
        "endpoints": {
            "web_interface": "/",
            "api_docs": "/docs",
            "professors": "/professors",
            "professor_by_name": "/professors/name/{name}",
            "professor_by_department": "/professors/department/{department}",
            "search": "/search",
            "stats": "/stats",
            "departments": "/departments",
        }
    }


@app.get("/professors")
async def get_professors(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    school: Optional[str] = Query(None, description="Filter by school: 'deanza' or 'ucsd'"),
    department: Optional[str] = Query(None, description="Filter by department"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum average rating"),
    max_difficulty: Optional[float] = Query(None, ge=0, le=5, description="Maximum average difficulty"),
    format: Optional[str] = Query(None, description="Response format: 'json' or 'html'")
):
    """Get all professors with optional filtering and pagination."""
    if format != "json" and os.path.exists("static/professors.html"):
        return FileResponse("static/professors.html")

    filtered = professors_data.copy()

    if school:
        filtered = [p for p in filtered if p.get("School", "").lower() == school.lower()]

    if department:
        filtered = [p for p in filtered if p.get("Department", "").lower() == department.lower()]

    if min_rating is not None:
        filtered = [
            p for p in filtered
            if (r := _get_float(p.get("Average_Rating"))) is not None and r >= min_rating
        ]

    if max_difficulty is not None:
        filtered = [
            p for p in filtered
            if (d := _get_float(p.get("Average_Difficulty"))) is not None and d <= max_difficulty
        ]

    total = len(filtered)
    start = (page - 1) * limit
    paginated = filtered[start:start + limit]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "data": paginated
    }


@app.get("/professors/name/{name}")
async def get_professor_by_name(
    name: str,
    school: Optional[str] = Query(None, description="Filter by school: 'deanza' or 'ucsd'"),
    format: Optional[str] = Query(None, description="Response format: 'json' or 'html'")
):
    """Get professor(s) by name (case-insensitive partial match)."""
    if format != "json" and os.path.exists("static/professors.html"):
        return FileResponse("static/professors.html")

    pool = professors_data
    if school:
        pool = [p for p in pool if p.get("School", "").lower() == school.lower()]

    name_lower = name.lower()
    matches = [p for p in pool if name_lower in p.get("Full_Name", "").lower()]

    if not matches:
        raise HTTPException(status_code=404, detail=f"Professor(s) with name '{name}' not found")

    return {"count": len(matches), "data": matches}


@app.get("/professors/department/{department}")
async def get_professors_by_department(
    department: str,
    school: Optional[str] = Query(None, description="Filter by school: 'deanza' or 'ucsd'"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    format: Optional[str] = Query(None, description="Response format: 'json' or 'html'")
):
    """Get professors by department."""
    if format != "json" and os.path.exists("static/professors.html"):
        return FileResponse("static/professors.html")

    pool = professors_data
    if school:
        pool = [p for p in pool if p.get("School", "").lower() == school.lower()]

    matches = [p for p in pool if department.lower() == p.get("Department", "").lower()]

    if not matches:
        raise HTTPException(status_code=404, detail=f"No professors found in department '{department}'")

    total = len(matches)
    start = (page - 1) * limit
    paginated = matches[start:start + limit]

    return {
        "department": department,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "data": paginated
    }


@app.get("/search")
async def search_professors(
    q: str = Query(..., description="Search query (searches in name and department)"),
    school: Optional[str] = Query(None, description="Filter by school: 'deanza' or 'ucsd'"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    format: Optional[str] = Query(None, description="Response format: 'json' or 'html'")
):
    """Search professors by name or department."""
    if format != "json" and os.path.exists("static/professors.html"):
        return FileResponse("static/professors.html")

    pool = professors_data
    if school:
        pool = [p for p in pool if p.get("School", "").lower() == school.lower()]

    query_lower = q.lower()
    matches = [
        p for p in pool
        if query_lower in p.get("Full_Name", "").lower()
        or query_lower in p.get("Department", "").lower()
    ]

    total = len(matches)
    start = (page - 1) * limit
    paginated = matches[start:start + limit]

    return {
        "query": q,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "data": paginated
    }


@app.get("/stats")
async def get_stats(
    school: Optional[str] = Query(None, description="Filter by school: 'deanza' or 'ucsd'"),
    format: Optional[str] = Query(None, description="Response format: 'json' or 'html'")
):
    """Get statistics about the professor database."""
    if format != "json" and os.path.exists("static/stats.html"):
        return FileResponse("static/stats.html")

    pool = professors_data
    if school:
        pool = [p for p in pool if p.get("School", "").lower() == school.lower()]

    if not pool:
        return {"message": "No data available"}

    departments = {}
    total_reviews = 0
    ratings = []
    difficulties = []

    for prof in pool:
        dept = prof.get("Department")
        if dept:
            departments[dept] = departments.get(dept, 0) + 1

        num_ratings = prof.get("Num_Ratings", 0)
        if isinstance(num_ratings, (int, float)):
            total_reviews += num_ratings

        rating = _get_float(prof.get("Average_Rating"))
        if rating is not None:
            ratings.append(rating)

        difficulty = _get_float(prof.get("Average_Difficulty"))
        if difficulty is not None:
            difficulties.append(difficulty)

    return {
        "total_professors": len(pool),
        "total_reviews": total_reviews,
        "departments": {
            "count": len(departments),
            "list": sorted(departments.keys())
        },
        "ratings": {
            "average": sum(ratings) / len(ratings) if ratings else 0,
            "min": min(ratings) if ratings else 0,
            "max": max(ratings) if ratings else 0
        },
        "difficulty": {
            "average": sum(difficulties) / len(difficulties) if difficulties else 0,
            "min": min(difficulties) if difficulties else 0,
            "max": max(difficulties) if difficulties else 0
        },
        "top_departments": sorted(
            departments.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    }


@app.get("/departments")
async def get_departments(
    school: Optional[str] = Query(None, description="Filter by school: 'deanza' or 'ucsd'"),
    format: Optional[str] = Query(None, description="Response format: 'json' or 'html'")
):
    """Get list of all departments."""
    if format != "json" and os.path.exists("static/departments.html"):
        return FileResponse("static/departments.html")

    pool = professors_data
    if school:
        pool = [p for p in pool if p.get("School", "").lower() == school.lower()]

    departments = sorted({p.get("Department") for p in pool if p.get("Department")})

    return {"count": len(departments), "departments": departments}


@app.get("/schools")
async def get_schools():
    """List available schools and their professor counts."""
    result = {}
    for school_key in DATA_FILES:
        count = sum(1 for p in professors_data if p.get("School") == school_key)
        result[school_key] = count
    return {"schools": result}


def _get_float(value):
    """Convert value to float, return None if conversion fails."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
