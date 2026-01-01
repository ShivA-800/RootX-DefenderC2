from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.agent_service import agent_service
from app.services.code_service import code_service

router = APIRouter()

class RegisterRequest(BaseModel):
    centralized_code: str = Field(..., min_length=12, max_length=12)
    hostname: str
    platform: str
    username: str
    agent_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class RegisterResponse(BaseModel):
    status: str
    agent_id: str
    token: str

class ConnectRequest(BaseModel):
    agent_id: str
    token: str

class ConnectResponse(BaseModel):
    status: str
    agent_id: str
    last_seen: str

@router.post("/register", response_model=RegisterResponse)
async def register_agent(request: RegisterRequest):
    """
    Register a new agent with a valid centralized code.
    """
    code_validation = code_service.validate_code(request.centralized_code)
    
    if not code_validation:
        raise HTTPException(status_code=400, detail="Invalid or expired centralized code")
    
    result = agent_service.register_agent(
        centralized_code=request.centralized_code,
        hostname=request.hostname,
        platform=request.platform,
        username=request.username,
        meta=request.meta,
        agent_id=request.agent_id
    )
    
    return result

@router.post("/connect", response_model=ConnectResponse)
async def connect_agent(request: ConnectRequest):
    """
    Reconnect an existing agent using agent_id and token.
    """
    result = agent_service.connect_agent(
        agent_id=request.agent_id,
        token=request.token
    )
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid agent_id or token")
    
    return result
