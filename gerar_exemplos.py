"""Gerador de cenários e imagens sintéticas para demonstração multimodal com 1 clique."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter

DIR_EXEMPLOS = Path(__file__).parent / "static" / "exemplos"

CATALOGO_EXEMPLOS: list[dict[str, Any]] = [
    {
        "id": "combo_incompleto",
        "nome_botao": "Caso 1: Foto com Combo vs. Texto Incompleto",
        "arquivo": "combo_incompleto.jpg",
        "titulo": "X-Burger Artesanal",
        "descricao": "Hambúrguer bovino 160g no pão brioche com queijo prato.",
        "preco": 34.90,
        "categoria": "Lanches & Burgers",
    },
    {
        "id": "foto_escura",
        "nome_botao": "Caso 2: Foto Escura / Mal Enquadrada",
        "arquivo": "foto_escura.jpg",
        "titulo": "Prato Executivo",
        "descricao": "Arroz, feijão, carne e salada.",
        "preco": 26.50,
        "categoria": "Pratos Executivos",
    },
    {
        "id": "padrao_ouro",
        "nome_botao": "Caso 3: Anúncio Bem Estruturado (Padrão Ouro)",
        "arquivo": "padrao_ouro.jpg",
        "titulo": "Smash Duplo Bacon Cheddar + Fritas Rústicas",
        "descricao": (
            "Dois blends bovinos 90g prensados na chapa, queijo cheddar cremoso, "
            "tiras de bacon crocante e molho especial no pão brioche selado. "
            "Acompanha porção individual de batatas fritas crocantes."
        ),
        "preco": 42.90,
        "categoria": "Lanches & Burgers",
    },
]


def _desenhar_burger(draw: ImageDraw.ImageDraw, cx: int, cy: int, escala: float = 1.0) -> None:
    """Desenha um hambúrguer em camadas bem definidas para reconhecimento visual."""
    w = int(150 * escala)
    # Pão inferior
    draw.rounded_rectangle([cx - w, cy + int(35 * escala), cx + w, cy + int(70 * escala)], radius=18, fill=(212, 148, 74))
    # Carne
    draw.rounded_rectangle([cx - w - 8, cy + int(5 * escala), cx + w + 8, cy + int(40 * escala)], radius=14, fill=(92, 46, 28))
    # Queijo cheddar derretido
    draw.polygon(
        [
            (cx - w, cy + int(5 * escala)),
            (cx + w, cy + int(5 * escala)),
            (cx + int(w * 0.7), cy + int(28 * escala)),
            (cx, cy + int(12 * escala)),
            (cx - int(w * 0.6), cy + int(26 * escala)),
        ],
        fill=(255, 196, 28),
    )
    # Alface e tomate
    draw.rounded_rectangle([cx - w - 4, cy - int(10 * escala), cx + w + 4, cy + int(6 * escala)], radius=8, fill=(58, 166, 68))
    draw.rounded_rectangle([cx - int(w * 0.85), cy - int(22 * escala), cx + int(w * 0.85), cy - int(8 * escala)], radius=6, fill=(220, 48, 42))
    # Pão superior
    draw.chord([cx - w, cy - int(85 * escala), cx + w, cy + int(15 * escala)], start=180, end=360, fill=(224, 156, 76))


def _criar_combo_incompleto(destino: Path) -> None:
    img = Image.new("RGB", (800, 520), (245, 238, 226))
    draw = ImageDraw.Draw(img)
    # Mesa e prato branco
    draw.rectangle([0, 340, 800, 520], fill=(198, 168, 134))
    draw.ellipse([110, 210, 690, 470], fill=(255, 255, 255), outline=(220, 220, 220), width=4)

    # Hambúrguer central
    _desenhar_burger(draw, cx=340, cy=310, escala=0.95)

    # Porção de batatas fritas à direita
    draw.polygon([(495, 360), (585, 360), (570, 270), (510, 270)], fill=(214, 40, 40))
    for offset in range(-28, 32, 11):
        draw.rectangle([540 + offset, 215, 547 + offset, 278], fill=(252, 205, 42), outline=(224, 170, 20))

    # Copo de refrigerante com canudo à esquerda
    draw.polygon([(165, 355), (235, 355), (245, 210), (155, 210)], fill=(45, 45, 52))
    draw.rectangle([152, 200, 248, 214], fill=(240, 240, 240))
    draw.line([(205, 200), (225, 135)], fill=(230, 57, 70), width=7)

    img.save(destino, format="JPEG", quality=92)


def _criar_foto_escura(destino: Path) -> None:
    img = Image.new("RGB", (800, 520), (28, 26, 24))
    draw = ImageDraw.Draw(img)
    # Prato mal enquadrado no canto inferior direito e com pouca luz
    draw.ellipse([430, 290, 860, 560], fill=(72, 70, 68))
    # Arroz, feijão e carne apagados
    draw.ellipse([490, 340, 630, 440], fill=(118, 115, 108))
    draw.ellipse([610, 360, 740, 460], fill=(64, 44, 34))
    draw.rounded_rectangle([540, 410, 700, 485], radius=16, fill=(78, 48, 38))
    img = img.filter(ImageFilter.GaussianBlur(radius=2.2))
    img.save(destino, format="JPEG", quality=68)


def _criar_padrao_ouro(destino: Path) -> None:
    img = Image.new("RGB", (800, 520), (252, 246, 236))
    draw = ImageDraw.Draw(img)
    # Fundo estúdio suave + tábua de madeira clara
    draw.rectangle([0, 310, 800, 520], fill=(182, 132, 86))
    draw.rounded_rectangle([130, 260, 670, 460], radius=28, fill=(148, 98, 56))

    # Hambúrguer duplo destaque bem iluminado
    _desenhar_burger(draw, cx=330, cy=305, escala=1.05)

    # Cesta metálica com fritas rústicas
    draw.rounded_rectangle([490, 245, 625, 365], radius=12, fill=(68, 72, 78))
    for offset in range(-45, 50, 13):
        draw.rectangle([555 + offset, 200, 564 + offset, 268], fill=(248, 198, 38), outline=(212, 152, 24))

    img.save(destino, format="JPEG", quality=95)


def garantir_exemplos() -> list[dict[str, Any]]:
    """Garante que todas as imagens de exemplo existam e retorna seus metadados."""
    DIR_EXEMPLOS.mkdir(parents=True, exist_ok=True)
    geradores = {
        "combo_incompleto.jpg": _criar_combo_incompleto,
        "foto_escura.jpg": _criar_foto_escura,
        "padrao_ouro.jpg": _criar_padrao_ouro,
    }
    for arquivo, fn in geradores.items():
        caminho = DIR_EXEMPLOS / arquivo
        if not caminho.exists():
            fn(caminho)

    saida = []
    for item in CATALOGO_EXEMPLOS:
        registro = dict(item)
        registro["imagem_url"] = f"/static/exemplos/{item['arquivo']}"
        registro["caminho_local"] = str(DIR_EXEMPLOS / item["arquivo"])
        saida.append(registro)
    return saida


if __name__ == "__main__":
    itens = garantir_exemplos()
    print(f"[OK] {len(itens)} cenários de exemplo gerados em {DIR_EXEMPLOS}")