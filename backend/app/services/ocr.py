import logging

import google.auth
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part

from app.config import settings

logger = logging.getLogger(__name__)

OCR_PROMPT = r"""You are a math OCR system. Look at this handwritten math formula image and output ONLY the LaTeX representation.

Rules:
- Output ONLY the LaTeX code, nothing else
- Do NOT wrap in $ signs or \[ \] delimiters
- Use standard LaTeX commands: \frac, \sqrt, \int, \sum, \lim, \begin{pmatrix}, etc.
- For nth roots use \sqrt[n]{...}
- For definite integrals use \int_a^b
- For matrices use \begin{pmatrix}...\end{pmatrix} or \begin{vmatrix}...\end{vmatrix}
- Preserve the exact mathematical meaning
- If unsure about a symbol, make your best guess

Output the LaTeX now:"""

MODEL_NAME = "gemini-2.0-flash"

_initialized = False


def _ensure_init():
    global _initialized
    if not _initialized:
        credentials = None
        if settings.google_application_credentials:
            credentials = service_account.Credentials.from_service_account_file(
                settings.google_application_credentials,
            )
        vertexai.init(
            project=settings.gcp_project_id,
            location=settings.gcp_location,
            credentials=credentials,
        )
        _initialized = True


class OCRService:
    def __init__(self):
        _ensure_init()
        self.model = GenerativeModel(MODEL_NAME)

    async def recognize(self, image_bytes: bytes, content_type: str) -> dict:
        """Run OCR on image bytes and return extracted text.

        Returns dict with 'text' and 'confidence' keys.
        """
        image_part = Part.from_data(data=image_bytes, mime_type=content_type)

        try:
            response = await self.model.generate_content_async(
                [OCR_PROMPT, image_part]
            )
            text = response.text.strip()
            return {"text": text, "confidence": 1.0}
        except Exception as e:
            if "429" in str(e):
                logger.warning("Gemini rate limit hit during OCR")
                raise RuntimeError("OCR service rate limited. Please try again shortly.") from e
            logger.error("OCR failed: %s", e)
            raise RuntimeError(f"OCR processing failed: {e}") from e
