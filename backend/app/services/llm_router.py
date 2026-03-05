"""LLM router for dispatching grading requests to appropriate LLM providers."""

import json
import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GRADING_SYSTEM_PROMPT = """\
You are a math grading assistant. Grade the student's answer to the given question.

Rules:
- For algebraic/numeric problems, check mathematical equivalence and required form.
- For proof/descriptive problems, evaluate logical correctness and completeness.
- Use the provided grading hints and evaluation concepts when available.

Respond with JSON only, no additional text:
{"is_correct": true/false, "reasoning": "brief explanation"}"""

CONCEPT_EXTRACTION_SYSTEM_PROMPT = """\
You are a math curriculum analyst. Given a math problem, extract the concepts it tests.

Respond with JSON only, no additional text:
{
  "evaluation_concepts": ["concept_name", ...],
  "required_concepts": ["concept_name", ...],
  "expected_form": "factored|expanded|simplified|numeric|proof",
  "grading_hints": "string or null"
}

Definitions:
- evaluation_concepts: the concepts this problem directly tests/evaluates.
- required_concepts: prerequisite concepts the student needs to solve this problem.
- expected_form: the form the answer should be in.
- grading_hints: any specific grading instructions (null if none)."""


class LLMRouter:
    """Routes grading requests to configured LLM or falls back to heuristic grading."""

    _client: httpx.AsyncClient | None = None

    @classmethod
    def _get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(timeout=settings.llm_timeout)
        return cls._client

    async def grade_answer(
        self,
        question_content: str,
        correct_answer: str,
        submitted_answer: str,
        grading_hints: str | None = None,
        evaluation_concepts: list[dict] | None = None,
    ) -> dict:
        """Grade an answer via LLM or heuristic fallback.

        Returns:
            dict with keys: is_correct (bool), reasoning (str)
        """
        if settings.llm_api_key:
            return await self._call_llm(
                question_content,
                correct_answer,
                submitted_answer,
                grading_hints,
                evaluation_concepts,
            )
        return self._fallback_grade(correct_answer, submitted_answer)

    async def _call_llm(
        self,
        question_content: str,
        correct_answer: str,
        submitted_answer: str,
        grading_hints: str | None,
        evaluation_concepts: list[dict] | None,
    ) -> dict:
        """Call OpenRouter API for grading."""
        user_message = self._build_grading_prompt(
            question_content, correct_answer, submitted_answer,
            grading_hints, evaluation_concepts,
        )
        try:
            client = self._get_client()
            response = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": [
                        {"role": "system", "content": GRADING_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 300,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_grading_response(content)
        except (httpx.HTTPStatusError, httpx.TimeoutException) as exc:
            logger.warning("LLM API error, falling back to heuristic: %s", exc)
            return self._fallback_grade(correct_answer, submitted_answer)
        except Exception as exc:
            logger.warning("LLM response parse error, falling back to heuristic: %s", exc)
            return self._fallback_grade(correct_answer, submitted_answer)

    async def extract_concepts(self, problem_content: str) -> dict | None:
        """Extract evaluation/required concepts from problem text via LLM.

        Returns dict with keys: evaluation_concepts, required_concepts,
        expected_form, grading_hints. Returns None on any failure.
        """
        if not settings.llm_api_key:
            return None

        user_message = f"Problem:\n{problem_content}"
        try:
            client = self._get_client()
            response = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": [
                        {"role": "system", "content": CONCEPT_EXTRACTION_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_json_response(content)
        except (httpx.HTTPStatusError, httpx.TimeoutException) as exc:
            logger.warning("LLM concept extraction API error: %s", exc)
            return None
        except Exception as exc:
            logger.warning("LLM concept extraction parse error: %s", exc)
            return None

    @staticmethod
    def _build_grading_prompt(
        question_content: str,
        correct_answer: str,
        submitted_answer: str,
        grading_hints: str | None,
        evaluation_concepts: list[dict] | None,
    ) -> str:
        parts = [
            f"Question: {question_content}",
            f"Expected answer: {correct_answer}",
            f"Student's answer: {submitted_answer}",
        ]
        if grading_hints:
            parts.append(f"Grading hints: {grading_hints}")
        if evaluation_concepts:
            concept_names = ", ".join(c["name"] for c in evaluation_concepts if "name" in c)
            if concept_names:
                parts.append(f"Evaluation concepts: {concept_names}")
        return "\n".join(parts)

    @staticmethod
    def _parse_grading_response(content: str) -> dict:
        """Parse LLM grading JSON response, handling optional markdown fences."""
        parsed = LLMRouter._parse_json_response(content)
        if parsed and "is_correct" in parsed:
            return {
                "is_correct": bool(parsed["is_correct"]),
                "reasoning": str(parsed.get("reasoning", "")),
            }
        raise ValueError(f"Invalid grading response structure: {content[:200]}")

    @staticmethod
    def _parse_json_response(content: str) -> dict | None:
        """Parse JSON from LLM response, stripping markdown fences if present."""
        text = content.strip()
        # Strip markdown code fences
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM response: %s", text[:200])
            return None

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for comparison: strip, lowercase, remove LaTeX commands."""
        s = text.strip().lower()
        # Remove LaTeX commands
        s = re.sub(r"\\[a-zA-Z]+", "", s)
        # Remove braces
        s = s.replace("{", "").replace("}", "")
        # Remove dollar signs
        s = s.replace("$", "")
        # Collapse whitespace
        s = re.sub(r"\s+", " ", s).strip()
        return s

    @staticmethod
    def _fallback_grade(correct_answer: str, submitted_answer: str) -> dict:
        """Heuristic fallback grading using string normalization comparison."""
        norm_correct = LLMRouter._normalize(correct_answer)
        norm_submitted = LLMRouter._normalize(submitted_answer)

        is_correct = norm_correct == norm_submitted
        if is_correct:
            reasoning = "Answer matches expected answer (normalized comparison)"
        else:
            reasoning = (
                f"Answer does not match. "
                f"Expected: '{correct_answer}', "
                f"Submitted: '{submitted_answer}'"
            )
        return {"is_correct": is_correct, "reasoning": reasoning}
