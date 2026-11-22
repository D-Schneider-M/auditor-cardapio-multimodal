# 🍽️ Auditor Multimodal de Cardápio & Conversão (Gemini Vision + FastAPI)

Sistema full-stack de auditoria automatizada para catálogos de delivery e marketplaces. Combina **Visão Computacional (`Gemini Vision`)**, **validação estrita de contrato JSON (`Pydantic Structured Outputs`)** e **API REST (`FastAPI`)** com interface web moderna para diagnosticar qualidade fotográfica, detectar divergências entre foto e texto e reescrever anúncios para maior conversão.

> **Nota:** As imagens de demonstração pré-carregadas são geradas sinteticamente via `Pillow` para permitir testes instantâneos com 1 clique sem dependência de arquivos externos.

## 1. Problema de Negócio e Arquitetura

Em marketplaces de alimentação, fotos com baixa iluminação ou descrições divergentes da imagem (ex.: foto exibindo combo completo enquanto o texto anuncia apenas o lanche) reduzem a conversão e aumentam solicitações de reembolso.

```text
┌───────────────────────────┐   Upload / Exemplo (Multipart)   ┌──────────────────────────────┐
│   Web App (HTML/Tailwind) │ ───────────────────────────────► │   API FastAPI (main.py)      │
│   static/index.html       │                                  │   Swagger Docs em /docs      │
└───────────────────────────┘                                  └──────────────┬───────────────┘
              ▲                                                               │
              │ JSON Estrito + Telemetria                                     ▼
┌─────────────┴─────────────┐     Pydantic Schema Validation   ┌──────────────────────────────┐
│   Antes vs. Depois +      │ ◄─────────────────────────────── │   Gemini Vision Multimodal   │
│   Alertas de Coerência    │                                  │   (auditor_ia.py)            │
└───────────────────────────┘                                  └──────────────────────────────┘