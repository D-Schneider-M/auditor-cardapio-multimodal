"""Motor de Auditoria Multimodal de Cardápio (Gemini Vision + Pydantic Structured Outputs)."""
from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-3.5-flash-lite"]

CUSTO_POR_MILHAO_TOKENS = {
    "entrada": 0.15,
    "saida": 0.60,
}

SYSTEM_INSTRUCTION = """
Você é um Especialista Sênior em Conversão de Marketplace, Fotografia Gastronômica e Qualidade de Catálogo de Delivery.
Sua missão é auditar simultaneamente a FOTO e o TEXTO (título, descrição, preço e categoria) de um item de cardápio.

Critérios obrigatórios de avaliação:
1. Qualidade Visual: avalie iluminação, nitidez, contraste, enquadramento e apetite appeal da imagem.
2. Coerência Foto vs. Texto (Anti-Reclamação): compare tudo que está visível na imagem com o que está escrito.
   - Se a foto mostrar acompanhamentos, bebidas ou itens que NÃO estão na descrição (ex.: batata frita ou refrigerante na foto, mas texto fala só do lanche), marque `possui_inconsistencia = true` e alerte sobre o risco de o cliente achar que o combo está incluso e abrir reclamação.
   - Se o texto prometer itens que não aparecem na foto, também aponte a divergência.
3. Copywriting para Conversão: reescreva o título (curto, claro, sem caixa alta abusiva) e a descrição (apetitosos, transparentes sobre gramatura/acompanhamentos e alinhados à foto real).
4. Responda sempre em português do Brasil, de forma objetiva e acionável para o dono do restaurante.
"""


class ResultadoAuditoria(BaseModel):
    nota_geral: int = Field(..., description="Nota geral de 0 a 100 considerando qualidade visual, aderência e conversão.")
    nota_iluminacao_nitidez: int = Field(..., description="Nota de 0 a 100 para iluminação, foco, contraste e nitidez.")
    nota_enquadramento: int = Field(..., description="Nota de 0 a 100 para enquadramento, centralização e apresentação do prato.")
    nota_aderencia_texto: int = Field(..., description="Nota de 0 a 100 para coerência exata entre imagem e descrição.")
    nota_atratividade_copy: int = Field(..., description="Nota de 0 a 100 para poder de venda do título e descrição atuais.")
    possui_inconsistencia: bool = Field(..., description="True se houver divergência relevante entre foto e texto.")
    alerta_inconsistencia: str = Field(..., description="Explicação objetiva da divergência, ou 'Nenhuma divergência detectada.'")
    elementos_identificados_foto: list[str] = Field(..., description="Lista de alimentos, bebidas e itens visíveis na imagem.")
    titulo_otimizado: str = Field(..., description="Novo título otimizado para busca e conversão no app.")
    descricao_otimizada: str = Field(..., description="Nova descrição apetitosa, transparente e fiel à imagem.")
    sugestoes_melhoria: list[str] = Field(..., description="Lista de 3 a 4 recomendações práticas para o restaurante.")
    impacto_estimado_conversao: str = Field(..., description="Potencial de melhoria ('Alto', 'Médio' ou 'Baixo') com justificativa curta.")


def _obter_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY não configurada. Adicione no arquivo .env local ou nas variáveis de ambiente do servidor."
        )
    return api_key


def _chamar_gemini_multimodal(
    client: genai.Client,
    partes: list[types.Part],
) -> tuple[Any, str]:
    modelos_unicos = list(dict.fromkeys(FALLBACK_MODELS))
    ultimo_erro: Exception | None = None

    for modelo in modelos_unicos:
        for tentativa in range(1, 3):
            try:
                resposta = client.models.generate_content(
                    model=modelo,
                    contents=partes,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_schema=ResultadoAuditoria,
                        temperature=0.2,
                    ),
                )
                return resposta, modelo
            except Exception as exc:
                ultimo_erro = exc
                msg = str(exc).lower()
                transitorio = any(
                    cod in msg
                    for cod in ("503", "429", "404", "not_found", "unavailable", "resource_exhausted", "deadline")
                )
                if not transitorio:
                    raise
                time.sleep(1.0 * tentativa)

    raise RuntimeError(f"Falha ao consultar modelos Gemini Vision: {ultimo_erro}")


def auditar_item_cardapio(
    imagem_bytes: bytes,
    mime_type: str,
    titulo: str,
    descricao: str,
    preco: float = 0.0,
    categoria: str = "Geral",
) -> dict[str, Any]:
    """Executa a auditoria multimodal (imagem + texto) e retorna JSON validado + telemetria."""
    api_key = _obter_api_key()
    if not imagem_bytes:
        raise ValueError("Nenhuma imagem válida foi enviada para auditoria.")
    if not titulo or not titulo.strip():
        raise ValueError("Informe o título atual do prato para realizar a auditoria.")

    inicio = time.perf_counter()
    client = genai.Client(api_key=api_key)

    prompt_texto = (
        f"Audite este item de cardápio:\n"
        f"- Categoria: {categoria.strip() or 'Geral'}\n"
        f"- Preço anunciado: R$ {preco:.2f}\n"
        f"- Título atual: {titulo.strip()}\n"
        f"- Descrição atual: {descricao.strip() or '(Sem descrição cadastrada)'}\n"
    )

    partes = [
        types.Part.from_bytes(data=imagem_bytes, mime_type=mime_type or "image/jpeg"),
        types.Part.from_text(text=prompt_texto),
    ]

    resposta, modelo_usado = _chamar_gemini_multimodal(client, partes)
    duracao = round(time.perf_counter() - inicio, 2)

    texto_json = (resposta.text or "").strip()
    if texto_json.startswith("```"):
        texto_json = texto_json.strip("`").removeprefix("json").strip()

    auditoria_validada = ResultadoAuditoria.model_validate_json(texto_json)

    uso = getattr(resposta, "usage_metadata", None)
    tokens_in = getattr(uso, "prompt_token_count", 0) or 0 if uso else 0
    tokens_out = getattr(uso, "candidates_token_count", 0) or 0 if uso else 0
    custo_usd = round(
        (tokens_in / 1_000_000) * CUSTO_POR_MILHAO_TOKENS["entrada"]
        + (tokens_out / 1_000_000) * CUSTO_POR_MILHAO_TOKENS["saida"],
        6,
    )

    return {
        "entrada": {
            "titulo": titulo.strip(),
            "descricao": descricao.strip(),
            "preco": round(float(preco), 2),
            "categoria": categoria.strip() or "Geral",
        },
        "auditoria": auditoria_validada.model_dump(),
        "modelo": modelo_usado,
        "telemetria": {
            "latencia_seg": duracao,
            "tokens_entrada": tokens_in,
            "tokens_saida": tokens_out,
            "tokens_total": tokens_in + tokens_out,
            "custo_estimado_usd": custo_usd,
        },
    }