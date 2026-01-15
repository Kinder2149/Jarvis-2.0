from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.agent_registry import get_base_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(req: ChatRequest):
    try:
        agent = get_base_agent()
        response = agent.handle(
            [{"role": "user", "content": req.message}]
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))