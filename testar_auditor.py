"""Testes de geração de cenários e Evals multimodais (Gemini Vision + Pydantic)."""
from __future__ import annotations

import sys
from pathlib import Path

from auditor_ia import auditar_item_cardapio
from gerar_exemplos import garantir_exemplos


def testar_estrutura_offline() -> None:
    exemplos = garantir_exemplos()
    assert len(exemplos) == 3
    for ex in exemplos:
        caminho = Path(ex["caminho_local"])
        assert caminho.exists() and caminho.stat().st_size > 1000
    print("[OK] 3 cenários e imagens sintéticas validados localmente.")


def rodar_evals_multimodais() -> None:
    exemplos = {e["id"]: e for e in garantir_exemplos()}

    # Caso 1: Foto com hambúrguer + batata + refri, mas texto só menciona X-Burger -> deve detectar inconsistência
    c1 = exemplos["combo_incompleto"]
    res1 = auditar_item_cardapio(
        imagem_bytes=Path(c1["caminho_local"]).read_bytes(),
        mime_type="image/jpeg",
        titulo=c1["titulo"],
        descricao=c1["descricao"],
        preco=c1["preco"],
        categoria=c1["categoria"],
    )
    aud1 = res1["auditoria"]
    ok1 = aud1["possui_inconsistencia"] is True and len(aud1["elementos_identificados_foto"]) >= 2
    print(
        f"[{'PASSOU' if ok1 else 'FALHOU'}] Caso Combo Incompleto | Inconsistência={aud1['possui_inconsistencia']} | "
        f"Itens={aud1['elementos_identificados_foto']} | Latência={res1['telemetria']['latencia_seg']}s"
    )

    # Caso 2: Foto escura e mal enquadrada -> deve receber nota geral baixa/moderada (< 65)
    c2 = exemplos["foto_escura"]
    res2 = auditar_item_cardapio(
        imagem_bytes=Path(c2["caminho_local"]).read_bytes(),
        mime_type="image/jpeg",
        titulo=c2["titulo"],
        descricao=c2["descricao"],
        preco=c2["preco"],
        categoria=c2["categoria"],
    )
    aud2 = res2["auditoria"]
    ok2 = aud2["nota_iluminacao_nitidez"] < 65
    print(
        f"[{'PASSOU' if ok2 else 'FALHOU'}] Caso Foto Escura | Nota Iluminação={aud2['nota_iluminacao_nitidez']}/100 | "
        f"Latência={res2['telemetria']['latencia_seg']}s"
    )

    acertos = int(ok1) + int(ok2)
    print(f"\nResumo Evals Multimodais: {acertos}/2 ({100 * acertos / 2:.0f}% de acerto)")


if __name__ == "__main__":
    testar_estrutura_offline()
    if "--completo" in sys.argv:
        rodar_evals_multimodais()
    else:
        print("\nDica: rode `python testar_auditor.py --completo` para testar a visão multimodal na API Gemini.")