from __future__ import annotations

import json

import httpx
import pytest
import respx
from mcp.server.mcpserver.exceptions import ToolError

from tandoor_mcp import server as s
from tandoor_mcp.client import TandoorClient

pytestmark = pytest.mark.asyncio


def _body(result) -> dict:
    """Tool results come back as a single TextContent block of JSON."""
    assert len(result.content) == 1
    return json.loads(result.content[0].text)


async def test_all_tools_are_registered():
    names = {t.name for t in await s.mcp.list_tools()}
    assert names == {
        "search_recipes",
        "get_recipe",
        "create_recipe",
        "update_recipe",
        "delete_recipe",
        "list_keywords",
        "create_keyword",
        "delete_keyword",
        "list_foods",
        "create_food",
        "delete_food",
        "list_units",
        "create_unit",
        "list_meal_types",
        "list_meal_plans",
        "create_meal_plan",
        "update_meal_plan",
        "delete_meal_plan",
        "list_shopping_list_entries",
        "create_shopping_list_entry",
        "update_shopping_list_entry",
        "delete_shopping_list_entry",
        "list_recipe_books",
        "create_recipe_book",
        "list_supermarkets",
        "list_users",
        "list_spaces",
        "tandoor_api_request",
    }


async def test_every_tool_has_a_description():
    for tool in await s.mcp.list_tools():
        assert tool.description, f"{tool.name} is missing a docstring/description"


async def test_get_recipe_returns_decoded_json(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.get("/api/recipe/1/").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Soup"})
    )

    result = await s.mcp.call_tool("get_recipe", {"recipe_id": 1})

    assert result.is_error is False
    assert _body(result) == {"id": 1, "name": "Soup"}


async def test_get_recipe_translates_404_into_tool_error(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.get("/api/recipe/404/").mock(
        return_value=httpx.Response(404, json={"detail": "Not found."})
    )

    with pytest.raises(ToolError, match="Not found"):
        await s.mcp.call_tool("get_recipe", {"recipe_id": 404})


async def test_unknown_tool_raises_tool_error():
    with pytest.raises(ToolError, match="Unknown tool"):
        await s.mcp.call_tool("does_not_exist", {})


async def test_missing_required_argument_raises_tool_error(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    with pytest.raises(ToolError):
        await s.mcp.call_tool("get_recipe", {})


async def test_search_recipes_merges_query_and_filters(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.get("/api/recipe/").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )

    await s.mcp.call_tool(
        "search_recipes",
        {"query": "soup", "page": 2, "filters": {"keywords": "3,7"}},
    )

    sent = route.calls.last.request
    qs = dict(httpx.QueryParams(sent.url.query))
    assert qs == {"query": "soup", "page": "2", "keywords": "3,7"}


async def test_create_recipe_merges_extra_fields(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/recipe/").mock(
        return_value=httpx.Response(201, json={"id": 1, "name": "Soup"})
    )

    result = await s.mcp.call_tool(
        "create_recipe", {"name": "Soup", "extra": {"description": "Warm", "servings": 4}}
    )

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {"name": "Soup", "description": "Warm", "servings": 4}
    assert _body(result) == {"id": 1, "name": "Soup"}


async def test_create_recipe_extra_cannot_override_name(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/recipe/").mock(return_value=httpx.Response(201, json={"id": 1}))

    await s.mcp.call_tool("create_recipe", {"name": "Soup", "extra": {"name": "Ignored"}})

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body["name"] == "Soup"


async def test_delete_recipe_returns_status_dict(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    mock_api.delete("/api/recipe/7/").mock(return_value=httpx.Response(204))

    result = await s.mcp.call_tool("delete_recipe", {"recipe_id": 7})

    assert _body(result) == {"status": "deleted", "resource": "recipe", "id": 7}


async def test_create_shopping_list_entry_builds_nested_food_and_unit(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/shopping-list-entry/").mock(
        return_value=httpx.Response(201, json={"id": 1})
    )

    await s.mcp.call_tool(
        "create_shopping_list_entry", {"food_id": 12, "amount": 2.5, "unit_id": 3}
    )

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {"food": {"id": 12}, "amount": 2.5, "unit": {"id": 3}}


async def test_create_shopping_list_entry_omits_unit_when_not_given(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/shopping-list-entry/").mock(
        return_value=httpx.Response(201, json={"id": 1})
    )

    await s.mcp.call_tool("create_shopping_list_entry", {"food_id": 12, "amount": 1})

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {"food": {"id": 12}, "amount": 1}


async def test_create_recipe_book_defaults_shared_to_empty_list(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/recipe-book/").mock(
        return_value=httpx.Response(201, json={"id": 1})
    )

    await s.mcp.call_tool("create_recipe_book", {"name": "Favorites"})

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body == {"name": "Favorites", "shared": []}


async def test_create_food_includes_optional_fields_when_given(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/food/").mock(return_value=httpx.Response(201, json={"id": 1}))

    await s.mcp.call_tool(
        "create_food", {"name": "Tomato", "plural_name": "Tomatoes", "description": "Red"}
    )

    assert json.loads(route.calls.last.request.content) == {
        "name": "Tomato",
        "plural_name": "Tomatoes",
        "description": "Red",
    }


async def test_create_unit_includes_optional_fields_when_given(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/unit/").mock(return_value=httpx.Response(201, json={"id": 1}))

    await s.mcp.call_tool(
        "create_unit", {"name": "g", "plural_name": "grams", "description": "grams"}
    )

    assert json.loads(route.calls.last.request.content) == {
        "name": "g",
        "plural_name": "grams",
        "description": "grams",
    }


async def test_create_recipe_book_includes_description_when_given(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/recipe-book/").mock(
        return_value=httpx.Response(201, json={"id": 1})
    )

    await s.mcp.call_tool("create_recipe_book", {"name": "Favorites", "description": "Best of"})

    assert json.loads(route.calls.last.request.content) == {
        "name": "Favorites",
        "description": "Best of",
        "shared": [],
    }


async def test_create_meal_plan_includes_all_optional_fields_when_given(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/meal-plan/").mock(return_value=httpx.Response(201, json={"id": 1}))

    await s.mcp.call_tool(
        "create_meal_plan",
        {
            "servings": 2,
            "from_date": "2026-01-01",
            "meal_type": 1,
            "recipe": 9,
            "title": "Dinner",
            "note": "spicy",
            "to_date": "2026-01-02",
        },
    )

    assert json.loads(route.calls.last.request.content) == {
        "servings": 2,
        "from_date": "2026-01-01",
        "meal_type": 1,
        "recipe": 9,
        "title": "Dinner",
        "note": "spicy",
        "to_date": "2026-01-02",
    }


async def test_create_recipe_book_wraps_shared_user_ids(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.post("/api/recipe-book/").mock(
        return_value=httpx.Response(201, json={"id": 1})
    )

    await s.mcp.call_tool("create_recipe_book", {"name": "Favorites", "shared_user_ids": [1, 2]})

    sent_body = json.loads(route.calls.last.request.content)
    assert sent_body["shared"] == [{"id": 1}, {"id": 2}]


async def test_update_meal_plan_sends_patch_with_given_fields(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.patch("/api/meal-plan/9/").mock(
        return_value=httpx.Response(200, json={"id": 9})
    )

    await s.mcp.call_tool("update_meal_plan", {"meal_plan_id": 9, "data": {"servings": 3}})

    assert route.calls.last.request.method == "PATCH"
    assert json.loads(route.calls.last.request.content) == {"servings": 3}


async def test_list_shopping_list_entries_passes_checked_filter(
    mcp_client: TandoorClient, mock_api: respx.MockRouter
):
    route = mock_api.get("/api/shopping-list-entry/").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )

    await s.mcp.call_tool("list_shopping_list_entries", {"checked": False})

    qs = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert qs == {"checked": "false"}


class TestTandoorApiRequestEscapeHatch:
    async def test_passes_through_to_arbitrary_resource(
        self, mcp_client: TandoorClient, mock_api: respx.MockRouter
    ):
        route = mock_api.get("/api/cook-log/").mock(
            return_value=httpx.Response(200, json={"count": 0, "results": []})
        )

        result = await s.mcp.call_tool(
            "tandoor_api_request", {"method": "get", "path": "cook-log/"}
        )

        assert route.calls.last.request.method == "GET"
        assert _body(result) == {"count": 0, "results": []}

    async def test_strips_leading_api_prefix(
        self, mcp_client: TandoorClient, mock_api: respx.MockRouter
    ):
        route = mock_api.get("/api/storage/3/").mock(
            return_value=httpx.Response(200, json={"id": 3})
        )

        await s.mcp.call_tool("tandoor_api_request", {"method": "GET", "path": "/api/storage/3/"})

        assert route.calls.last.request.url.path == "/api/storage/3/"

    async def test_rejects_unsupported_method(
        self, mcp_client: TandoorClient, mock_api: respx.MockRouter
    ):
        with pytest.raises(ToolError, match="Unsupported method"):
            await s.mcp.call_tool("tandoor_api_request", {"method": "TRACE", "path": "recipe/"})

    async def test_forwards_json_body_on_post(
        self, mcp_client: TandoorClient, mock_api: respx.MockRouter
    ):
        route = mock_api.post("/api/automation/").mock(
            return_value=httpx.Response(201, json={"id": 1})
        )

        await s.mcp.call_tool(
            "tandoor_api_request",
            {"method": "POST", "path": "automation/", "json_body": {"name": "x"}},
        )

        assert json.loads(route.calls.last.request.content) == {"name": "x"}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "method", "path"),
    [
        ("list_keywords", {"query": "veg"}, "GET", "/api/keyword/"),
        ("create_keyword", {"name": "vegan", "description": "d"}, "POST", "/api/keyword/"),
        ("delete_keyword", {"keyword_id": 1}, "DELETE", "/api/keyword/1/"),
        ("list_foods", {}, "GET", "/api/food/"),
        ("create_food", {"name": "Tomato"}, "POST", "/api/food/"),
        ("delete_food", {"food_id": 2}, "DELETE", "/api/food/2/"),
        ("list_units", {}, "GET", "/api/unit/"),
        ("create_unit", {"name": "g"}, "POST", "/api/unit/"),
        ("list_meal_types", {}, "GET", "/api/meal-type/"),
        ("list_meal_plans", {}, "GET", "/api/meal-plan/"),
        (
            "create_meal_plan",
            {"servings": 2, "from_date": "2026-01-01", "meal_type": 1},
            "POST",
            "/api/meal-plan/",
        ),
        ("delete_meal_plan", {"meal_plan_id": 4}, "DELETE", "/api/meal-plan/4/"),
        ("update_recipe", {"recipe_id": 1, "data": {"name": "x"}}, "PATCH", "/api/recipe/1/"),
        (
            "update_shopping_list_entry",
            {"entry_id": 5, "data": {"checked": True}},
            "PATCH",
            "/api/shopping-list-entry/5/",
        ),
        ("delete_shopping_list_entry", {"entry_id": 6}, "DELETE", "/api/shopping-list-entry/6/"),
        ("list_recipe_books", {}, "GET", "/api/recipe-book/"),
        ("list_supermarkets", {}, "GET", "/api/supermarket/"),
        ("list_users", {}, "GET", "/api/user/"),
        ("list_spaces", {}, "GET", "/api/space/"),
    ],
)
async def test_simple_tool_hits_expected_endpoint(
    mcp_client: TandoorClient,
    mock_api: respx.MockRouter,
    tool_name: str,
    arguments: dict,
    method: str,
    path: str,
):
    status = 204 if method == "DELETE" else (201 if method == "POST" else 200)
    body = None if status == 204 else {"id": 1}
    mock_api.route(method=method, path=path).mock(return_value=httpx.Response(status, json=body))

    result = await s.mcp.call_tool(tool_name, arguments)

    assert result.is_error is False


async def test_get_client_builds_from_env_when_unset(monkeypatch: pytest.MonkeyPatch):
    s.set_client(None)
    monkeypatch.setenv("TANDOOR_BASE_URL", "http://env.test")
    monkeypatch.setenv("TANDOOR_API_TOKEN", "env-token")

    built = s.get_client()
    try:
        assert isinstance(built, TandoorClient)
        assert built is s.get_client()  # cached, not rebuilt
    finally:
        await s.close_client()


async def test_get_client_raises_tool_error_without_token(monkeypatch: pytest.MonkeyPatch):
    s.set_client(None)
    monkeypatch.delenv("TANDOOR_API_TOKEN", raising=False)

    with pytest.raises(ToolError, match="TANDOOR_API_TOKEN"):
        await s.mcp.call_tool("list_meal_types", {})
