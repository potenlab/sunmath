from pydantic import BaseModel


class OCRResponse(BaseModel):
    text: str
    confidence: float
    model_used: str = "baseline"
