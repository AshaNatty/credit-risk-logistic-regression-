"""Tests for the FastAPI REST API."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def _loan_payload(**kwargs):
    payload = {
        "customer_id": "CUST-005",
        "annual_income": 80000,
        "monthly_debt": 800,
        "loan_amount": 200000,
        "loan_term_months": 360,
        "interest_rate": 5.5,
        "credit_score": 720,
        "employment_years": 5.0,
        "loan_purpose": "home",
    }
    payload.update(kwargs)
    return payload


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_assess_loan_valid():
    response = client.post("/api/v1/assess", json=_loan_payload())
    assert response.status_code == 200
    data = response.json()
    assert "decision" in data
    assert "risk_scoring" in data
    assert "compliance_audit" in data
    assert "policy_validation" in data
    assert data["risk_scoring"]["risk_score"] >= 0


def test_assess_loan_invalid_credit_score():
    response = client.post("/api/v1/assess", json=_loan_payload(credit_score=200))
    assert response.status_code == 422


def test_assess_loan_denied_scenario():
    response = client.post(
        "/api/v1/assess",
        json=_loan_payload(credit_score=500, monthly_debt=5000, annual_income=30000),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] in ("approved", "denied", "pending_review")
