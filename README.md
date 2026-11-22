# 🍽️ Auditor Multimodal de Cardápio & Conversão (Gemini Vision + FastAPI)

[![Aplicação ao Vivo](https://img.shields.io/badge/App_ao_Vivo-Acessar_Sistema-e11d48?style=for-the-badge)](https://SEU-LINK-AQUI.onrender.com)
[![API Docs](https://img.shields.io/badge/FastAPI-Swagger_Docs-10b981?style=for-the-badge)](https://SEU-LINK-AQUI.onrender.com/docs)

* **🌐 Aplicação Web ao Vivo:** `https://SEU-LINK-AQUI.onrender.com` *(em deploy)*
* **⚡ Documentação Interativa da API (Swagger):** `https://SEU-LINK-AQUI.onrender.com/docs`

Sistema full-stack de auditoria automatizada para catálogos de delivery e marketplaces. Combina **Visão Computacional (`Gemini Vision`)**, **validação estrita de contrato JSON (`Pydantic Structured Outputs`)** e **API REST (`FastAPI`)** com interface web responsiva para diagnosticar qualidade fotográfica, detectar divergências entre foto e texto e reescrever anúncios para maior conversão.

> **Nota sobre os dados de demonstração:** Os 3 cenários pré-carregados (*Combo Incompleto*, *Foto Escura* e *Padrão Ouro*) utilizam imagens geradas sinteticamente via `Pillow` para permitir testes instantâneos com 1 clique sem dependência de arquivos externos.

---

## 1. Problema de Negócio & Arquitetura

Em marketplaces de alimentação, fotos com baixa iluminação ou descrições divergentes da imagem (ex.: foto exibindo combo com batata e bebida enquanto o texto anuncia apenas o lanche) derrubam a taxa de conversão e aumentam chamados de reembolso.

```text
┌───────────────────────────┐   Upload / Exemplo (Multipart)   ┌──────────────────────────────┐
│   Web App (HTML/CSS/JS)   │ ───────────────────────────────► │   API FastAPI (main.py)      │
│   static/index.html       │                                  │   Swagger Docs em /docs      │
└───────────────────────────┘                                  └──────────────┬───────────────┘
              ▲                                                               │
              │ JSON Estrito + Telemetria                                     ▼
┌─────────────┴─────────────┐     Pydantic Schema Validation   ┌──────────────────────────────┐
│   Antes vs. Depois +      │ ◄─────────────────────────────── │   Gemini Vision Multimodal   │
│   Alertas de Coerência    │                                  │   (auditor_ia.py)            │
└───────────────────────────┘                                  └──────────────────────────────┘
