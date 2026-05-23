from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx
from app.config import settings
from app.services.ai.retry import RetryPolicy, run_with_retry


class GeminiError(Exception):
    pass


class GeminiTransientError(GeminiError):
    pass


class GeminiResponseFormatError(GeminiError):
    pass


@dataclass(frozen=True)
class GeminiUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class GeminiGenerationResult:
    raw_output: str
    parsed_output: dict[str, Any]
    usage: GeminiUsage
    retries_used: int = 0


class GeminiClient:
    """Backend-only Gemini wrapper with schema-constrained JSON output."""

    _TRANSIENT_CODES = {408, 409, 429, 500, 502, 503, 504}

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        api_base_url: str,
        timeout_seconds: float = 30.0,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiClient.")

        self.api_key = api_key
        normalized_model_name = model_name.strip().removeprefix("models/").strip()
        if not normalized_model_name:
            raise ValueError("GEMINI_MODEL_NAME must be set.")
        self.model_name = normalized_model_name
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retry_policy = retry_policy or RetryPolicy()

    @classmethod
    def from_settings(cls) -> "GeminiClient":
        return cls(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_MODEL_NAME,
            api_base_url=settings.GEMINI_API_BASE_URL,
            timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
            retry_policy=RetryPolicy(
                max_attempts=max(settings.AI_MAX_RETRIES, 1),
                base_delay_seconds=max(settings.AI_RETRY_BASE_DELAY_SECONDS, 0.1),
            ),
        )

    async def generate_structured(
        self,
        *,
        prompt: str,
        response_json_schema: dict[str, Any],
        temperature: float = 0.2,
    ) -> GeminiGenerationResult:
        async def _task() -> GeminiGenerationResult:
            return await self._generate_once(
                prompt=prompt,
                response_json_schema=response_json_schema,
                temperature=temperature,
            )

        result, retries_used = await run_with_retry(
            _task,
            should_retry=self._should_retry,
            policy=self.retry_policy,
        )
        return GeminiGenerationResult(
            raw_output=result.raw_output,
            parsed_output=result.parsed_output,
            usage=result.usage,
            retries_used=retries_used,
        )

    async def _generate_once(
        self,
        *,
        prompt: str,
        response_json_schema: dict[str, Any],
        temperature: float,
    ) -> GeminiGenerationResult:
        is_openai_compatible = "openrouter" in self.api_base_url.lower() or "openai" in self.api_base_url.lower()

        if is_openai_compatible:
            url = f"{self.api_base_url}/chat/completions"
            
            # Use OpenAI formatted payload
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            # Add json schema enforcement if response_json_schema is provided.
            # OpenRouter / OpenAI supports tools or json_schema in response_format,
            # but for maximum compatibility with free models, a system hint and response_format={"type": "json_object"}
            # is best, or passing the schema directly for models that support it.
            if response_json_schema:
                # Some models on OpenRouter/OpenAI don't support response_format={"type": "json_object"}
                # and throw a 400. We'll rely on the system prompt and then use our robust extraction helper.
                payload["messages"].insert(0, {
                    "role": "system",
                    "content": f"You must respond with valid JSON matching this schema: {json.dumps(response_json_schema)}. Do not include any other text."
                })
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8080",
                "X-Title": "EduFlow"
            }
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(url, headers=headers, json=payload)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                raise GeminiTransientError(f"Transport error while calling AI provider: {exc}") from exc
                
        else:
            url = f"{self.api_base_url}/v1beta/models/{self.model_name}:generateContent"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "responseMimeType": "application/json",
                    "responseSchema": response_json_schema,
                },
            }
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(url, params={"key": self.api_key}, json=payload)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                raise GeminiTransientError(f"Transport error while calling Gemini: {exc}") from exc

        if response.status_code in self._TRANSIENT_CODES:
            raise GeminiTransientError(
                f"Transient AI error {response.status_code}: {response.text[:300]}"
            )
        if response.status_code == 404:
            raise GeminiError(
                f"AI model not found. "
                f"Configured Model='{self.model_name}'. "
                f"Raw: {response.text[:500]}"
            )
        if response.status_code >= 400:
            raise GeminiError(f"AI error {response.status_code}: {response.text[:600]}")

        data = response.json()
        
        is_openai_compatible = "openrouter" in self.api_base_url.lower() or "openai" in self.api_base_url.lower()
        raw_output = self._extract_response_text(data, is_openai=is_openai_compatible)
        
        if not raw_output:
            raise GeminiResponseFormatError("AI response did not contain JSON text content.")

        # Robust JSON extraction: try to find a JSON block if not directly parsable
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            # Try to extract from markdown block ```json ... ```
            import re
            match = re.search(r"```json\s*(.*?)\s*```", raw_output, re.DOTALL)
            if not match:
                match = re.search(r"```\s*(.*?)\s*```", raw_output, re.DOTALL)
            
            if match:
                try:
                    parsed = json.loads(match.group(1))
                except json.JSONDecodeError as exc:
                    raise GeminiResponseFormatError("Found JSON block but it was not valid JSON.") from exc
            else:
                raise GeminiResponseFormatError("AI response was not valid JSON and no markdown code block was found.")

        if not isinstance(parsed, dict):
            raise GeminiResponseFormatError("AI structured response must be a JSON object.")

        usage_data = data.get("usage", {}) if is_openai_compatible else data.get("usageMetadata", {})
        if not usage_data:
            usage_data = {}
            
        usage = GeminiUsage(
            input_tokens=usage_data.get("prompt_tokens") if is_openai_compatible else usage_data.get("promptTokenCount"),
            output_tokens=usage_data.get("completion_tokens") if is_openai_compatible else usage_data.get("candidatesTokenCount"),
            total_tokens=usage_data.get("total_tokens") if is_openai_compatible else usage_data.get("totalTokenCount"),
        )
        return GeminiGenerationResult(raw_output=raw_output, parsed_output=parsed, usage=usage)

    async def generate_simple(
        self,
        *,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Mimics the simple, direct API call style of ai_content_generator.py.
        Returns ONLY the raw text/JSON content from the AI.
        """
        is_openai_compatible = "openrouter" in self.api_base_url.lower() or "openai" in self.api_base_url.lower()
        
        if is_openai_compatible:
            url = f"{self.api_base_url}/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8080",
                "X-Title": "EduFlow"
            }
        else:
            url = f"{self.api_base_url}/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temperature},
            }
            headers = {}

        # Simple retry loop mirroring the reference implementation
        max_retries = 3
        last_exc = None
        
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract text using the direct paths
                    raw_text = ""
                    if is_openai_compatible:
                        choices = data.get("choices", [])
                        if choices:
                            raw_text = choices[0].get("message", {}).get("content", "")
                    else:
                        candidates = data.get("candidates", [])
                        if candidates:
                            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    
                    if not raw_text:
                        raise Exception("AI returned empty content")
                        
                    return raw_text.strip()
                    
                except Exception as e:
                    last_exc = e
                    if attempt < max_retries - 1:
                        import asyncio
                        await asyncio.sleep(0.5 * (2**attempt))
                    continue
        
        raise last_exc or Exception("Failed to generate content after retries")

    @staticmethod
    def _extract_response_text(response_json: dict[str, Any], is_openai: bool = False) -> str:
        if is_openai:
            choices = response_json.get("choices") or []
            if not choices:
                return ""
            return str((choices[0] or {}).get("message", {}).get("content") or "").strip()
            
        candidates = response_json.get("candidates") or []
        if not candidates:
            return ""
        parts = (((candidates[0] or {}).get("content") or {}).get("parts")) or []
        if not parts:
            return ""
        return str((parts[0] or {}).get("text") or "").strip()

    @staticmethod
    def _should_retry(exc: Exception) -> bool:
        return isinstance(exc, GeminiTransientError)
