import os
import sys
import pytest
from fastapi.testclient import TestClient
import httpx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.services.todaypickup_service import TodayPickupService
from app.repositories.todaypickup_repository import TodayPickupRepository
from app.controllers import todaypickup_controller
from app.schemas.todaypickup import AuthAgencyDTO, GoodsNoDawnDTO


@pytest.fixture
def client():
    return TestClient(app)


def setup_mock(monkeypatch, expected_path, response_json):
    async def handler(request):
        assert request.url.path == expected_path
        return httpx.Response(200, json=response_json)

    transport = httpx.MockTransport(handler)
    repo = TodayPickupRepository(client=httpx.AsyncClient(transport=transport, base_url="https://admin.todaypickup.com"))
    service = TodayPickupService(repo)
    app.dependency_overrides[todaypickup_controller.get_service] = lambda: service
    return transport


def teardown_mock():
    app.dependency_overrides.clear()


def test_mall_possible_delivery(client, monkeypatch):
    setup_mock(monkeypatch, "/api/mall/possibleDelivery", {"result": "ok"})
    resp = client.get("/api/mall/possibleDelivery", headers={"Authorization": "x"}, params={"address": "addr"})
    assert resp.status_code == 200
    assert resp.json() == {"result": "ok"}
    teardown_mock()


def test_mall_delivery_register(client, monkeypatch):
    setup_mock(monkeypatch, "/api/mall/deliveryRegister", {"id": 1})
    payload = {
        "deliveryAddress": "addr",
        "deliveryName": "name",
        "deliveryPhone": "010",
        "mallName": "mall"
    }
    resp = client.post("/api/mall/deliveryRegister", headers={"Authorization": "x"}, json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"id": 1}
    teardown_mock()


def test_agency_auth_token(client, monkeypatch):
    setup_mock(monkeypatch, "/api/agency/auth/token", {"token": "abc"})
    dto = {
        "accessKey": "k",
        "nonce": "n",
        "timestamp": "t"
    }
    resp = client.post("/api/agency/auth/token", headers={"Authorization": "x", "agencyId": "a"}, json=dto)
    assert resp.status_code == 200
    assert resp.json() == {"token": "abc"}
    teardown_mock()
