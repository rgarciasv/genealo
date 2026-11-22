"""Cliente de transcripción paleográfica sobre recortes de línea usando Google GenAI SDK."""

from __future__ import annotations

import base64
import logging
import os
import time
from typing import Optional

import cv2
import numpy as np
from google import genai
from pydantic import BaseModel, Field

from .config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LineTranscriptionResult(BaseModel):
    """Esquema JSON estricto exigido a Gemini por cada línea manuscrita."""

    texto: str = Field(
        description=(
            "Transcripción paleográfica literal estricta de la línea. "
            "Cadena vacía '' si es totalmente ilegible. Prohibido usar '?' o '[?]'."
        )
    )
    duda: bool = Field(
        description=(
            "True si existe cualquier tramo dudoso, tinta muy pálida, mancha o "
            "incertidumbre paleográfica que requiera revisión humana."
        )
    )
    motivo: str = Field(
        default="",
        description="Descripción breve de la duda si duda=true; cadena vacía si no hay duda.",
    )


class GeminiLineTranscriber:
    """Orquesta llamadas multimodales síncronas con salida estructurada por línea."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_retries: int = 4,
        base_backoff_sec: float = 2.0,
    ) -> None:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "No se encontró GEMINI_API_KEY en las variables de entorno. "
                "Define $env:GEMINI_API_KEY='tu_clave' en PowerShell antes de ejecutar."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.base_backoff_sec = base_backoff_sec

    @staticmethod
    def _encode_bgr_to_png_base64(crop_bgr: np.ndarray) -> str:
        ok, buf = cv2.imencode(".png", crop_bgr)
        if not ok:
            raise RuntimeError("No se pudo codificar el recorte PNG en memoria.")
        return base64.b64encode(buf.tobytes()).decode("utf-8")

    def _build_generation_config(self) -> Optional[dict[str, object]]:
        # Gemini 4 Carbon/Argon y 3.8 Flash recomiendan omitir temperature;
        # modelos 3.1 como gemini-3.1-pro-preview usan temperature=0.1 según especificación.
        lower_model = self.model.lower()
        if lower_model.startswith("gemini-4") or "3.8" in lower_model:
            return None
        return {"temperature": self.temperature}

    @staticmethod
    def _sanitize_result(result: LineTranscriptionResult) -> LineTranscriptionResult:
        """Asegura que nunca se inyecten marcadores prohibidos ('?' o '[?]') en el XML."""
        texto = result.texto.strip()
        duda = result.duda
        motivo = result.motivo.strip()

        if "[?]" in texto or "?" in texto:
            logger.warning("Detectado marcador '?' o '[?]' en respuesta; limpiando y marcando duda=True.")
            texto = texto.replace("[?]", "").replace("?", "").strip()
            duda = True
            note = "Marcador '?' sanitizado automáticamente."
            motivo = f"{motivo} | {note}".strip(" |") if motivo else note

        return LineTranscriptionResult(texto=texto, duda=duda, motivo=motivo)

    def transcribe_line(
        self,
        crop_bgr: np.ndarray,
        line_id: str,
        side: str = "unknown",
    ) -> LineTranscriptionResult:
        """Envía el recorte poligonal enmascarado a Gemini y valida la salida Pydantic."""
        image_b64 = self._encode_bgr_to_png_base64(crop_bgr)
        user_prompt = (
            f"Transcribe literalmente esta única línea manuscrita "
            f"(ID: {line_id}, plana: {side}). "
            "Aplica estrictamente todas las reglas paleográficas, abreviaturas e inventario Unicode cerrado."
        )

        request_kwargs: dict[str, object] = {
            "model": self.model,
            "system_instruction": SYSTEM_PROMPT,
            "input": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image",
                    "data": image_b64,
                    "mime_type": "image/png",
                    "resolution": "high",
                },
            ],
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": LineTranscriptionResult.model_json_schema(),
            },
            "store": False,
        }

        gen_cfg = self._build_generation_config()
        if gen_cfg is not None:
            request_kwargs["generation_config"] = gen_cfg

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                interaction = self.client.interactions.create(**request_kwargs)
                raw_json = interaction.output_text
                if not raw_json:
                    raise ValueError(f"Respuesta vacía de Gemini para línea {line_id}")
                parsed = LineTranscriptionResult.model_validate_json(raw_json)
                return self._sanitize_result(parsed)
            except Exception as exc:
                last_exc = exc
                wait_sec = self.base_backoff_sec * (2 ** (attempt - 1))
                logger.warning(
                    "Error transcribiendo %s (intento %d/%d): %s. Reintentando en %.1fs...",
                    line_id,
                    attempt,
                    self.max_retries,
                    exc,
                    wait_sec,
                )
                if attempt < self.max_retries:
                    time.sleep(wait_sec)

        logger.error("Fallo definitivo en línea %s tras %d intentos: %s", line_id, self.max_retries, last_exc)
        return LineTranscriptionResult(
            texto="",
            duda=True,
            motivo=f"Error de API tras {self.max_retries} reintentos: {last_exc}",
        )
