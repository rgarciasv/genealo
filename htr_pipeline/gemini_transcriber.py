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

from .config import (
    DEFAULT_MODEL,
    DEFAULT_RESOLUTION,
    DEFAULT_TEMPERATURE,
    DEFAULT_THINKING_LEVEL,
    SYSTEM_PROMPT,
)

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


class PartidaLineItem(BaseModel):
    """Transcripción de una línea numerada dentro de un bloque contextual de partida."""

    numero: int = Field(description="Número entero 1..N exactamente como aparece en la etiqueta de la imagen anotada.")
    texto: str = Field(
        description=(
            "Transcripción paleográfica literal estricta de esa línea exacta. "
            "Cadena vacía '' si es totalmente ilegible. Prohibido usar '?' o '[?]'."
        )
    )
    duda: bool = Field(
        description="True si existe cualquier tramo dudoso o tinta pálida en esta línea."
    )
    motivo: str = Field(
        default="",
        description="Motivo breve si duda=true; cadena vacía si no hay duda.",
    )


class PartidaTranscriptionResult(BaseModel):
    """Salida estructurada para todas las líneas numeradas [01]..[N] de una partida completa."""

    lineas: list[PartidaLineItem] = Field(
        description="Lista completa con exactamente una entrada por cada número de línea [01]..[N] presente en la imagen anotada."
    )


class GeminiLineTranscriber:
    """Orquesta llamadas multimodales síncronas con salida estructurada por línea."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        resolution: str = DEFAULT_RESOLUTION,
        thinking_level: Optional[str] = DEFAULT_THINKING_LEVEL,
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
        self.resolution = resolution
        self.thinking_level = (thinking_level or "").strip().lower() or None
        self.max_retries = max_retries
        self.base_backoff_sec = base_backoff_sec

    @staticmethod
    def _encode_bgr_to_png_base64(crop_bgr: np.ndarray) -> str:
        ok, buf = cv2.imencode(".png", crop_bgr)
        if not ok:
            raise RuntimeError("No se pudo codificar el recorte PNG en memoria.")
        return base64.b64encode(buf.tobytes()).decode("utf-8")

    def _build_generation_config(self) -> Optional[dict[str, object]]:
        # Gemini 4 (hydrogen/neon/argon/carbon) y 3.8 Flash omiten temperature y usan thinking_level.
        lower_model = self.model.lower()
        if lower_model.startswith("gemini-4") or "3.8" in lower_model:
            if self.thinking_level and self.thinking_level != "none":
                return {"thinking_level": self.thinking_level}
            return None
        return {"temperature": self.temperature}

    @staticmethod
    def _sanitize_result(result: LineTranscriptionResult) -> LineTranscriptionResult:
        """Asegura inventario Unicode cerrado y elimina marcadores prohibidos ('?' o '[?]')."""
        texto = result.texto.strip()
        duda = result.duda
        motivo = result.motivo.strip()

        # Reemplazos implícitos deterministas ([L-39] / Aletheia implicit_character_replacements)
        texto = (
            texto.replace("\u00b0", "\u00ba")  # ° -> º
            .replace("\u1d52", "\u00ba")  # ᵒ -> º
            .replace("\u1d43", "\u00aa")  # ᵃ -> ª
            .replace("\u017f", "s")  # ſ -> s (TRIDIS)
            .replace("\ufb01", "fi")
            .replace("\ufb02", "fl")
        )

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
                    "resolution": self.resolution,
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

    def transcribe_partida(
        self,
        clean_crop_bgr: np.ndarray,
        annotated_crop_bgr: np.ndarray,
        partida_id: str,
        side: str,
        index_to_line_id: dict[int, str],
    ) -> dict[str, LineTranscriptionResult]:
        """Transcribe una partida completa en 1 sola llamada enviando:
        - Imagen 1 (ultra_high / self.resolution): recorte limpio sin marcas sobre la tinta.
        - Imagen 2 (high): mismo recorte con etiquetas numeradas [01]..[N] para asignar cada línea.
        """
        clean_b64 = self._encode_bgr_to_png_base64(clean_crop_bgr)
        annotated_b64 = self._encode_bgr_to_png_base64(annotated_crop_bgr)

        n_lines = len(index_to_line_id)
        idx_list_str = ", ".join(f"{i:02d}" for i in sorted(index_to_line_id))
        user_prompt = (
            f"Transcribirás una partida o bloque manuscrito completo ({partida_id}, plana: {side}) "
            f"compuesto por exactamente {n_lines} líneas numeradas: [{idx_list_str}].\n"
            "Se adjuntan DOS imágenes del mismo bloque:\n"
            "1) PRIMERA IMAGEN (LIMPIA): tinta original intacta para lectura paleográfica de máxima precisión.\n"
            "2) SEGUNDA IMAGEN (ANOTADA): exactamente el mismo recorte con pastillas numeradas [01]..[N] "
            "y bandas translúcidas que delimitan el alcance exacto de cada línea.\n\n"
            "INSTRUCCIONES CRÍTICAS:\n"
            "- Usa el contexto completo de la partida (incluyendo el cruce entre cuerpo y notas marginales) "
            "para desambiguar nombres y palabras cortadas entre renglones, SIN inventar ni modernizar la ortografía.\n"
            "- Devuelve EXACTAMENTE el texto contenido dentro del polígono de cada número [01]..[N], sin mover "
            "palabras de una línea a otra y sin omitir ningún número.\n"
            "- Aplica estrictamente el inventario Unicode cerrado de 16 caracteres especiales (prohibido '?' o '[?]')."
        )

        # Si el usuario pidió ultra_high lo usamos para la imagen limpia; si pidió high, también funciona genial.
        clean_res = self.resolution
        annot_res = "high" if clean_res == "ultra_high" else clean_res

        request_kwargs: dict[str, object] = {
            "model": self.model,
            "system_instruction": SYSTEM_PROMPT,
            "input": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image",
                    "data": clean_b64,
                    "mime_type": "image/png",
                    "resolution": clean_res,
                },
                {
                    "type": "image",
                    "data": annotated_b64,
                    "mime_type": "image/png",
                    "resolution": annot_res,
                },
            ],
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": PartidaTranscriptionResult.model_json_schema(),
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
                    raise ValueError(f"Respuesta vacía de Gemini para {partida_id}")
                parsed = PartidaTranscriptionResult.model_validate_json(raw_json)

                out: dict[str, LineTranscriptionResult] = {}
                for item in parsed.lineas:
                    lid = index_to_line_id.get(item.numero)
                    if lid is None:
                        continue
                    out[lid] = self._sanitize_result(
                        LineTranscriptionResult(
                            texto=item.texto,
                            duda=item.duda,
                            motivo=item.motivo,
                        )
                    )
                # Rellenar cualquier línea faltante con duda=True para no perder trazabilidad
                for num, lid in index_to_line_id.items():
                    if lid not in out:
                        out[lid] = LineTranscriptionResult(
                            texto="",
                            duda=True,
                            motivo=f"Línea [{num:02d}] omitida en respuesta de partida {partida_id}.",
                        )
                return out
            except Exception as exc:
                last_exc = exc
                wait_sec = self.base_backoff_sec * (2 ** (attempt - 1))
                logger.warning(
                    "Error transcribiendo partida %s (intento %d/%d): %s. Reintentando en %.1fs...",
                    partida_id,
                    attempt,
                    self.max_retries,
                    exc,
                    wait_sec,
                )
                if attempt < self.max_retries:
                    time.sleep(wait_sec)

        logger.error("Fallo definitivo en partida %s tras %d intentos: %s", partida_id, self.max_retries, last_exc)
        return {
            lid: LineTranscriptionResult(
                texto="",
                duda=True,
                motivo=f"Error de API en partida {partida_id}: {last_exc}",
            )
            for lid in index_to_line_id.values()
        }
