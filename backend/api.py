from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.agent_registry import get_base_agent
from backend.agents.base_agent import InvalidRuntimeMessageError
from backend.ia.mistral_client import MistralResponseFormatError, MistralUpstreamError

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
    except InvalidRuntimeMessageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MistralResponseFormatError:
        raise HTTPException(
            status_code=502,
            detail="Invalid response format from upstream AI provider",
        )
    except MistralUpstreamError:
        raise HTTPException(
            status_code=503,
            detail="Upstream AI provider unavailable",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))