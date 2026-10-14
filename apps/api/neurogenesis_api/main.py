"""FastAPI application factory and lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neurogenesis_connectors import PubMedClient, PubMedClientSettings

from neurogenesis_api.routes import health, literature, research_runs
from neurogenesis_api.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_environment()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with httpx.AsyncClient(
            base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            headers={"User-Agent": "NeuroGenesisAI/0.1 (developers@neurogenesis.ai)"},
        ) as http_client:
            app.state.pubmed = PubMedClient(
                http_client,
                PubMedClientSettings(
                    email=resolved_settings.ncbi_email,
                    api_key=resolved_settings.ncbi_api_key,
                ),
            )
            yield

    app = FastAPI(
        title="NeuroGenesis AI API",
        version="0.1.0",
        description="Evidence-first research planning and biomedical literature metadata API.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved_settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    app.include_router(health.router)
    app.include_router(literature.router)
    app.include_router(research_runs.router)
    return app


app = create_app()
