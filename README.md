# 🍽️ Auditor Multimodal de Cardápio & Conversão (Gemini Vision + FastAPI + Pydantic)

[![Aplicação ao Vivo](https://img.shields.io/badge/App_ao_Vivo-Acessar_Sistema-e11d48?style=for-the-badge)](https://diegoschneider.pythonanywhere.com)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini Vision](https://img.shields.io/badge/Google_Gemini-Multimodal_Vision-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

* **🌐 Aplicação Web ao Vivo:** [https://diegoschneider.pythonanywhere.com](https://diegoschneider.pythonanywhere.com)
* **⚡ Documentação Interativa da API (Ambiente Local):** `http://127.0.0.1:8000/docs` *(Swagger / OpenAPI via FastAPI)*

Sistema full-stack de auditoria automatizada de qualidade e conversão para catálogos de delivery e marketplaces de alimentação. A aplicação combina **Visão Computacional Multimodal (`Gemini Vision`)**, **validação estrita de contratos JSON (`Pydantic Structured Outputs`)** e **telemetria de custo e latência (FinOps)** para avaliar simultaneamente a foto e o texto cadastrado de um item, detectar inconsistências operacionais e reescrever o anúncio com foco em conversão.

> **Nota sobre os dados de demonstração:** Os 3 cenários pré-carregados na interface (*Combo Incompleto*, *Foto Escura* e *Padrão Ouro*) utilizam imagens geradas sinteticamente via `Pillow` (`gerar_exemplos.py`) para permitir testes instantâneos com 1 clique sem depender de bancos de imagens externos. Também é possível enviar qualquer foto real (`PNG`, `JPG` ou `WEBP`) diretamente pela interface.

---

## 1. Problema de Negócio & Impacto

Em plataformas de food delivery e marketplaces, a qualidade do catálogo digital impacta diretamente o funil de vendas e a experiência pós-pedido:

1. **Queda na taxa de clique e conversão:** Fotos escuras, tremidas ou mal enquadradas reduzem a atratividade visual na vitrine do aplicativo.
2. **Churn, cancelamentos e chamados de suporte:** Quando a foto exibe um combo completo (ex.: hambúrguer, batata frita e refrigerante), mas o título e a descrição mencionam apenas o lanche unitário, gera-se atrito comercial e divergência na entrega.
3. **Subaproveitamento de ticket médio:** Descrições genéricas ou incompletas deixam de destacar atributos sensoriais, gramatura, acompanhamentos e diferenciais do preparo.

Este projeto automatiza a curadoria do catálogo em segundos, entregando um diagnóstico acionável para o restaurante parceiro.

---

## 2. Arquitetura da Solução

```text
┌─────────────────────────────┐   Multipart Form (Foto + Texto)   ┌──────────────────────────────┐
│   Frontend Web Responsivo   │ ────────────────────────────────► │   Camada API REST            │
│   static/index.html         │                                   │   FastAPI (main.py) / WSGI   │
└─────────────────────────────┘                                   └──────────────┬───────────────┘
               ▲                                                                 │
               │ JSON Tipado + Telemetria (Latência, Tokens, US$)                ▼
┌──────────────┴──────────────┐      Pydantic Schema Validation   ┌──────────────────────────────┐
│   Painel de Diagnóstico:    │ ◄──────────────────────────────── │   Motor Multimodal           │
│   • Scores (0 a 100)        │                                   │   Gemini Vision + Fallback   │
│   • Alerta Foto vs. Texto   │                                   │   (auditor_ia.py)            │
│   • Copy Antes vs. Depois   │                                   └──────────────────────────────┘
└─────────────────────────────┘
