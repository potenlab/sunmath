import logging

import google.auth
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from sqlalchemy.ext.asyncio import AsyncSession

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


def _load_baseline_model() -> GenerativeModel | None:
    """Load the active baseline model endpoint, if available."""
    # Config override takes priority
    if settings.baseline_model_endpoint:
        return GenerativeModel(settings.baseline_model_endpoint)
    return None


class OCRService:
    def __init__(self, db: AsyncSession | None = None):
        _ensure_init()
        self.raw_model = GenerativeModel(MODEL_NAME)
        self.baseline_model = _load_baseline_model()
        self.db = db

    async def _try_load_baseline_from_db(self) -> GenerativeModel | None:
        """Lazily load baseline model from DB if not set via config."""
        if self.baseline_model is not None:
            return self.baseline_model
        if not self.db:
            return None
        try:
            from sqlalchemy import text

            # Check if the baseline_models table exists before querying
            result = await self.db.execute(
                text(
                    "SELECT EXISTS ("
                    "  SELECT FROM information_schema.tables"
                    "  WHERE table_name = 'baseline_models'"
                    ")"
                )
            )
            table_exists = result.scalar()
            if not table_exists:
                return None

            from app.services.baseline_training import get_active_baseline_model

            active = await get_active_baseline_model(self.db)
            if active and active.model_endpoint:
                self.baseline_model = GenerativeModel(active.model_endpoint)
                logger.info("Loaded baseline model: %s", active.model_endpoint)
                return self.baseline_model
        except Exception as e:
            logger.warning("Failed to load baseline model from DB: %s", e)
        return None

    async def recognize(
        self, image_bytes: bytes, content_type: str, student_id: int | None = None
    ) -> dict:
        """Run OCR on image bytes and return extracted text.

        Fallback chain: LoRA -> baseline-tuned -> baseline-raw (raw Gemini).
        Returns dict with 'text', 'confidence', and 'model_used' keys.
        """
        model_used = "baseline-raw"
        model = self.raw_model

        # Try to load baseline-tuned model
        baseline = await self._try_load_baseline_from_db()
        if baseline:
            model = baseline
            model_used = "baseline-tuned"

        # Try to use student's LoRA-tuned model if available (highest priority)
        if student_id and self.db:
            try:
                from app.services.lora_training import get_active_lora_model

                lora_model = await get_active_lora_model(self.db, student_id)
                if lora_model and lora_model.model_endpoint:
                    model = GenerativeModel(lora_model.model_endpoint)
                    model_used = "lora"
                    logger.info(
                        "Using LoRA model %s for student %d",
                        lora_model.model_endpoint,
                        student_id,
                    )
            except Exception as e:
                logger.warning(
                    "Failed to load LoRA model for student %d, using %s: %s",
                    student_id,
                    model_used,
                    e,
                )

        image_part = Part.from_data(data=image_bytes, mime_type=content_type)

        try:
            response = await model.generate_content_async(
                [OCR_PROMPT, image_part]
            )
            text = response.text.strip()
            return {"text": text, "confidence": 1.0, "model_used": model_used}
        except Exception as e:
            # Fallback chain: lora -> baseline-tuned -> baseline-raw
            fallback_chain = []
            if model_used == "lora":
                if baseline:
                    fallback_chain.append(("baseline-tuned", baseline))
                fallback_chain.append(("baseline-raw", self.raw_model))
            elif model_used == "baseline-tuned":
                fallback_chain.append(("baseline-raw", self.raw_model))

            for fallback_label, fallback_model in fallback_chain:
                logger.warning(
                    "%s model failed, falling back to %s: %s",
                    model_used,
                    fallback_label,
                    e,
                )
                try:
                    response = await fallback_model.generate_content_async(
                        [OCR_PROMPT, image_part]
                    )
                    text = response.text.strip()
                    return {"text": text, "confidence": 1.0, "model_used": fallback_label}
                except Exception as fallback_err:
                    e = fallback_err

            if "429" in str(e):
                logger.warning("Gemini rate limit hit during OCR")
                raise RuntimeError("OCR service rate limited. Please try again shortly.") from e
            logger.error("OCR failed: %s", e)
            raise RuntimeError(f"OCR processing failed: {e}") from e
