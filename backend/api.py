from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.agent_registry import get_base_agent
from backend.agents.base_agent import InvalidRuntimeMessageError
from backend.ia.mistral_client import MistralResponseFormatError, MistralUpstreamError

router = APIRouter()

# In-memory session store (process-local)
SESSIONS: dict[str, list[dict]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@router.post("/chat")
def chat(req: ChatRequest):
    try:
        import uuid

        session_id = req.session_id or str(uuid.uuid4())
        history = SESSIONS.get(session_id, [])

        # Append user message to history
        history.append({"role": "user", "content": req.message})

        agent = get_base_agent()
        response_text = agent.handle(history)

        # Append assistant response to history and persist
        history.append({"role": "assistant", "content": response_text})
        SESSIONS[session_id] = history

        return {"response": response_text, "session_id": session_id}
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