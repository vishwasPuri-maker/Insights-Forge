# /scraper/market_intelligence_spider.py
# Task 2: Resilient Market Intelligence Spider & Validation Barrier
# Mapping: Doc 2 (TRD Section 9.3), Doc 1 (PRD Section 1.1)
"""
Scrapy spider that gathers external sector indicators without ever touching
the transactional (OLTP) systems. Every scraped row is passed through the
Pydantic validation barrier before being written to S3. Rows below the
structural completeness threshold are written to an append-only
dead-letter path instead of being dropped silently.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

import scrapy

from validation_schema import validate_row

RAW_LANDING_TEMPLATE = "tenants/{tenant_id}/raw/{date}/market_intel_{ts}.jsonl"
DEAD_LETTER_TEMPLATE = "tenants/{tenant_id}/deadletter/{date}/rejected_{ts}.jsonl"


class MarketIntelligenceSpider(scrapy.Spider):
    name = "market_intelligence_spider"

    custom_settings = {
        # Decoupling Principle: never allow this spider to be invoked against
        # internal/transactional hosts.
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 1.5,
        "AUTOTHROTTLE_ENABLED": True,
    }

    def __init__(self, tenant_id: str, start_urls: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant_id = tenant_id
        self.start_urls = start_urls.split(",") if start_urls else []
        self._valid_buffer: list[dict] = []
        self._dead_letter_buffer: list[dict] = []

    def parse(self, response):
        """
        Extract sector indicator rows from the response. Selector logic is
        intentionally generic here — real deployments supply per-source
        parsing rules registered in a source config table.
        """
        for row_sel in response.css(".indicator-row"):
            raw_row = {
                "tenant_id": self.tenant_id,
                "source_url": response.url,
                "indicator_name": row_sel.css(".name::text").get(),
                "indicator_metric": self._safe_float(row_sel.css(".metric::text").get()),
                "temporal_stamp": row_sel.css(".timestamp::text").get(),
                "sector": row_sel.css(".sector::text").get(),
                "raw_snippet": row_sel.get(),
            }
            self._route_row(raw_row)

        yield from self._flush()

    def _route_row(self, raw_row: dict) -> None:
        is_valid, model, score = validate_row(raw_row)
        if is_valid and model is not None:
            self._valid_buffer.append(model.model_dump(mode="json"))
        else:
            raw_row["_completeness_score"] = score
            raw_row["_rejected_at"] = datetime.now(timezone.utc).isoformat()
            self._dead_letter_buffer.append(raw_row)

    def _flush(self):
        """Write buffered valid/dead-letter rows to their S3 landing paths."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if self._valid_buffer:
            key = RAW_LANDING_TEMPLATE.format(tenant_id=self.tenant_id, date=date, ts=ts)
            yield {"_s3_key": key, "_payload": self._valid_buffer, "_kind": "raw"}
            self._valid_buffer = []

        if self._dead_letter_buffer:
            key = DEAD_LETTER_TEMPLATE.format(tenant_id=self.tenant_id, date=date, ts=ts)
            # Append-only: dead-letter records are never overwritten or deleted.
            yield {"_s3_key": key, "_payload": self._dead_letter_buffer, "_kind": "deadletter"}
            self._dead_letter_buffer = []

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
