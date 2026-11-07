from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from app.git_service import GitRepositoryAnalyzer
from app.ai_historian import AIHistorianEngine

app = FastAPI(title="Spatial-Temporal AI Code Historian API")

# React Frontend connect garna CORS enable garne
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_engine = AIHistorianEngine()

class RepoRequest(BaseModel):
    repo_path: str

class CommitNarrativeRequest(BaseModel):
    commit_data: dict

@app.post("/api/parse-repo")
def parse_repository(req: RepoRequest):
    if not os.path.exists(req.repo_path):
        raise HTTPException(status_code=400, detail="Repository path does not exist")
    try:
        analyzer = GitRepositoryAnalyzer(req.repo_path)
        data = analyzer.generate_3d_spatial_nodes()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-narrative")
async def get_ai_narrative(req: CommitNarrativeRequest):
    try:
        narrative = await ai_engine.analyze_commit_narrative(req.commit_data)
        return {"narrative": narrative}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)