from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from environment import SmartHomeEnergyEnv
from models import Action

app = FastAPI(title="Smart Home Energy Optimizer")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active environments (in production, use proper state management)
environments = {}

class ResetRequest(BaseModel):
    difficulty: str = "easy"

class StepRequest(BaseModel):
    action: dict

@app.get("/")
async def root():
    return {
        "name": "Smart Home Energy Optimizer",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/reset")
async def reset(request: Optional[ResetRequest] = None):
    """Reset the environment"""
    difficulty = request.difficulty if request else "easy"
    
    env = SmartHomeEnergyEnv(difficulty=difficulty)
    observation = await env.reset()
    
    # Store environment (use session ID in production)
    env_id = "default"
    environments[env_id] = env
    
    return {
        "observation": observation.dict(),
        "info": {"difficulty": difficulty}
    }

@app.post("/step")
async def step(request: StepRequest):
    """Take a step in the environment"""
    env_id = "default"
    
    if env_id not in environments:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first")
    
    env = environments[env_id]
    
    try:
        # Parse action
        action = Action(**request.action)
        
        # Take step
        observation, reward, done, info = await env.step(action)
        
        return {
            "observation": observation.dict(),
            "reward": reward.dict(),
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def get_state():
    """Get current environment state"""
    env_id = "default"
    
    if env_id not in environments:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first")
    
    env = environments[env_id]
    state = await env.state()
    
    return state

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)