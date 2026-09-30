from __future__ import annotations

import httpx
import pytest
import respx

from tandoor_mcp.client import TandoorClient
from tandoor_mcp.errors import TandoorAPIError

pytestmark = pytest.mark.asyncio


async def test_get_sends_bearer_token_and_accept_header(
    client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.get("/api/recipe/1/").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Soup"})
    )

    result = await client.get("recipe", 1)

    assert result == {"id": 1, "name": "Soup"}
    sent = route.calls.last.request
    assert sent.headers["Authorization"] == "Bearer tda_test_token"
    assert sent.headers["Accept"] == "application/json"


async def test_list_drops_none_valued_params(client: TandoorClient, mock_api: respx.MockRouter):
    route = mock_api.get("/api/recipe/").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )

    await client.list("recipe", params={"query": "soup", "page": None, "page_size": 10})

    sent = route.calls.last.request
    assert dict(httpx.QueryParams(sent.url.query)) == {"query": "soup", "page_size": "10"}


async def test_list_with_no_params_sends_no_query_string(
    client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.get("/api/keyword/").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )

    await client.list("keyword")

    assert route.calls.last.request.url.query == b""


async def test_create_posts_json_body(client: TandoorClient, mock_api: respx.MockRouter):
    route = mock_api.post("/api/keyword/").mock(
        return_value=httpx.Response(201, json={"id": 5, "name": "vegan"})
    )

    result = await client.create("keyword", {"name": "vegan"})

    assert result == {"id": 5, "name": "vegan"}
    assert route.calls.last.request.headers["Content-Type"] == "application/json"
    import json

    assert json.loads(route.calls.last.request.content) == {"name": "vegan"}


async def test_update_defaults_to_patch(client: TandoorClient, mock_api: respx.MockRouter):
    route = mock_api.patch("/api/recipe/9/").mock(
        return_value=httpx.Response(200, json={"id": 9, "name": "new"})
    )

    result = await client.update("recipe", 9, {"name": "new"})

    assert result == {"id": 9, "name": "new"}
    assert route.calls.last.request.method == "PATCH"


async def test_update_with_partial_false_uses_put(
    client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.put("/api/recipe/9/").mock(return_value=httpx.Response(200, json={"id": 9}))

    await client.update("recipe", 9, {"name": "new"}, partial=False)

    assert route.calls.last.request.method == "PUT"


async def test_delete_returns_none_on_204(client: TandoorClient, mock_api: respx.MockRouter):
    mock_api.delete("/api/recipe/3/").mock(return_value=httpx.Response(204))

    result = await client.delete("recipe", 3)

    assert result is None


async def test_404_raises_tandoor_api_error_with_status_and_detail(
    client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.get("/api/recipe/404/").mock(
        return_value=httpx.Response(404, json={"detail": "Not found."})
    )

    with pytest.raises(TandoorAPIError) as excinfo:
        await client.get("recipe", 404)

    assert excinfo.value.status_code == 404
    assert "Not found" in str(excinfo.value)


async def test_validation_error_payload_is_summarized_in_message(
    client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.post("/api/keyword/").mock(
        return_value=httpx.Response(400, json={"name": ["This field is required."]})
    )

    with pytest.raises(TandoorAPIError) as excinfo:
        await client.create("keyword", {})

    assert "name" in str(excinfo.value)
    assert "This field is required." in str(excinfo.value)
    assert excinfo.value.payload == {"name": ["This field is required."]}


async def test_error_with_empty_body_falls_back_to_reason_phrase(
    client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.get("/api/recipe/1/").mock(return_value=httpx.Response(404))

    with pytest.raises(TandoorAPIError) as excinfo:
        await client.get("recipe", 1)

    assert excinfo.value.status_code == 404
    assert excinfo.value.payload is None


async def test_401_raises_tandoor_api_error(client: TandoorClient, mock_api: respx.MockRouter):
    mock_api.get("/api/recipe/").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid token."})
    )

    with pytest.raises(TandoorAPIError) as excinfo:
        await client.list("recipe")

    assert excinfo.value.status_code == 401


async def test_500_with_non_json_body_falls_back_to_reason_phrase(
    client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.get("/api/recipe/").mock(return_value=httpx.Response(500, text="<html>boom</html>"))

    with pytest.raises(TandoorAPIError) as excinfo:
        await client.list("recipe")

    assert excinfo.value.status_code == 500


async def test_timeout_raises_tandoor_api_error(client: TandoorClient, mock_api: respx.MockRouter):
    mock_api.get("/api/recipe/").mock(side_effect=httpx.ConnectTimeout("boom"))

    with pytest.raises(TandoorAPIError, match="timed out"):
        await client.list("recipe")


async def test_network_error_raises_tandoor_api_error(
    client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.get("/api/recipe/").mock(side_effect=httpx.ConnectError("refused"))

    with pytest.raises(TandoorAPIError, match="failed"):
        await client.list("recipe")


async def test_empty_204_success_does_not_raise(client: TandoorClient, mock_api: respx.MockRouter):
    mock_api.post("/api/sync/").mock(return_value=httpx.Response(204))

    result = await client.request("POST", "/api/sync/")

    assert result is None


async def test_aclose_is_idempotent_safe(settings, mock_api: respx.MockRouter):
    c = TandoorClient(settings)
    await c.aclose()
    # closing an already-closed httpx client should not raise
    await c.aclose()


async def test_context_manager_closes_underlying_client(settings, mock_api: respx.MockRouter):
    async with TandoorClient(settings) as c:
        assert c is not None
    assert c._http.is_closed
