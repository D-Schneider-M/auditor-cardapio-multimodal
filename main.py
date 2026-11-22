"""API FastAPI e servidor web do Auditor Multimodal de Cardápio."""
from __future__ import annotations

import mimetypes
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from auditor_ia import auditar_item_cardapio
from gerar_exemplos import garantir_exemplos

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    garantir_exemplos()
    yield


app = FastAPI(
    title="Auditor Multimodal de Cardápio & Conversão",
    description="API de Visão Computacional + Structured Outputs (Gemini Vision + Pydantic) para catálogo de delivery.",
    version="1.0.0",
    lifespan=lifespan,
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def pagina_inicial() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "servico": "auditor-cardapio-multimodal"}


@app.get("/api/exemplos")
def listar_exemplos() -> list[dict[str, Any]]:
    exemplos = garantir_exemplos()
    return [
        {
            "id": item["id"],
            "nome_botao": item["nome_botao"],
            "imagem_url": item["imagem_url"],
            "titulo": item["titulo"],
            "descricao": item["descricao"],
            "preco": item["preco"],
            "categoria": item["categoria"],
        }
        for item in exemplos
    ]


@app.post("/api/auditar")
async def endpoint_auditar(
    titulo: str = Form(...),
    descricao: str = Form(""),
    preco: float = Form(0.0),
    categoria: str = Form("Geral"),
    exemplo_id: str = Form(""),
    imagem: UploadFile | None = File(None),
) -> dict[str, Any]:
    imagem_bytes: bytes = b""
    mime_type = "image/jpeg"

    if imagem is not None and imagem.filename:
        imagem_bytes = await imagem.read()
        mime_type = imagem.content_type or mimetypes.guess_type(imagem.filename)[0] or "image/jpeg"
        if not mime_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="O arquivo enviado precisa ser uma imagem (JPG, PNG ou WEBP).")
    elif exemplo_id.strip():
        exemplos = {e["id"]: e for e in garantir_exemplos()}
        escolhido = exemplos.get(exemplo_id.strip())
        if not escolhido:
            raise HTTPException(status_code=404, detail="Exemplo não encontrado.")
        caminho = Path(escolhido["caminho_local"])
        imagem_bytes = caminho.read_bytes()
        mime_type = "image/jpeg"
    else:
        raise HTTPException(status_code=400, detail="Envie uma imagem do prato ou selecione um cenário de exemplo.")

    try:
        return auditar_item_cardapio(
            imagem_bytes=imagem_bytes,
            mime_type=mime_type,
            titulo=titulo,
            descricao=descricao,
            preco=preco,
            categoria=categoria,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao processar auditoria multimodal: {exc}") from exc