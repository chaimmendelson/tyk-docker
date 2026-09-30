"""MCP server exposing the Tandoor Recipes REST API as tools.

Design notes
------------
* One shared :class:`TandoorClient` per process (see ``get_client``), lazily
  built from environment configuration on first use and reused across calls
  so the underlying HTTP connection pool is actually pooled.
* Tools intentionally do not declare a ``Context`` parameter: none of them
  need progress reporting or client-side logging, and skipping it keeps
  ``mcp.call_tool()`` trivially callable in tests without a live session.
* ``TandoorAPIError`` (a failure we anticipated: 404, validation error,
  timeout, ...) is translated to ``ToolError`` so the MCP client gets a clean
  message instead of a stack trace. Anything else is a genuine bug and is
  left to propagate as a crash.
* A handful of resources (recipe, keyword, food, unit, meal-plan,
  shopping-list-entry, recipe-book, supermarket) get dedicated, ergonomic
  tools. Tandoor exposes ~50 resources in total; ``tandoor_api_request`` is a
  deliberate escape hatch covering everything else without needing a
  hand-written wrapper for each one.
"""

from __future__ import annotations

import functools
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from tandoor_mcp.client import TandoorClient
from tandoor_mcp.config import ConfigError, Settings
from tandoor_mcp.errors import TandoorAPIError

mcp = MCPServer(
    name="tandoor-recipes",
    instructions=(
        "Tools for the Tandoor Recipes instance configured via TANDOOR_BASE_URL / "
        "TANDOOR_API_TOKEN. Covers recipes, keywords, foods, units, meal plans, "
        "shopping lists, and recipe books, plus a raw tandoor_api_request escape "
        "hatch for any other endpoint under /api/."
    ),
)

_client: TandoorClient | None = None


def get_client() -> TandoorClient:
    """Return the process-wide TandoorClient, building it on first use."""
    global _client
    if _client is None:
        _client = TandoorClient(Settings.from_env())
    return _client


def set_client(client: TandoorClient | None) -> None:
    """Override the process-wide client. Used by tests; not part of the public API."""
    global _client
    _client = client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


_F = TypeVar("_F", bound=Callable[..., Awaitable[Any]])


def _translate_errors(func: _F) -> _F:
    """Turn TandoorAPIError into ToolError so MCP clients see a clean message."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except TandoorAPIError as exc:
            raise ToolError(str(exc)) from exc
        except ConfigError as exc:
            raise ToolError(str(exc)) from exc

    return wrapper  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Recipes
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def search_recipes(
    query: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    filters: dict[str, Any] | None = None,
) -> Any:
    """Search/list recipes.

    Args:
        query: Free-text search term (matches name/description/ingredients).
        page: 1-based page number.
        page_size: Results per page.
        filters: Extra query-string filters passed through verbatim, e.g.
            {"keywords": "3,7", "foods": "12", "rating": 5}. See the Tandoor
            API docs for the full filter set on GET /api/recipe/.
    """
    params = dict(filters or {})
    params.update({"query": query, "page": page, "page_size": page_size})
    return await get_client().list("recipe", params=params)


@mcp.tool()
@_translate_errors
async def get_recipe(recipe_id: int) -> Any:
    """Fetch a single recipe by ID, including its steps and ingredients."""
    return await get_client().get("recipe", recipe_id)


@mcp.tool()
@_translate_errors
async def create_recipe(name: str, extra: dict[str, Any] | None = None) -> Any:
    """Create a recipe.

    Args:
        name: Recipe name (required by Tandoor).
        extra: Any other recipe fields (description, servings, working_time,
            waiting_time, keywords, steps, ...) merged into the create
            payload as-is. See GET /api/recipe/ (OPTIONS) for the full
            field list.
    """
    data = dict(extra or {})
    data["name"] = name
    return await get_client().create("recipe", data)


@mcp.tool()
@_translate_errors
async def update_recipe(recipe_id: int, data: dict[str, Any]) -> Any:
    """Partially update a recipe (PATCH) with the given fields."""
    return await get_client().update("recipe", recipe_id, data)


@mcp.tool()
@_translate_errors
async def delete_recipe(recipe_id: int) -> Any:
    """Delete a recipe by ID."""
    await get_client().delete("recipe", recipe_id)
    return {"status": "deleted", "resource": "recipe", "id": recipe_id}


# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def list_keywords(query: str | None = None, page: int | None = None) -> Any:
    """List keywords (tags), optionally filtered by name."""
    return await get_client().list("keyword", params={"query": query, "page": page})


@mcp.tool()
@_translate_errors
async def create_keyword(name: str, description: str | None = None) -> Any:
    """Create a keyword (tag)."""
    data: dict[str, Any] = {"name": name}
    if description is not None:
        data["description"] = description
    return await get_client().create("keyword", data)


@mcp.tool()
@_translate_errors
async def delete_keyword(keyword_id: int) -> Any:
    """Delete a keyword by ID."""
    await get_client().delete("keyword", keyword_id)
    return {"status": "deleted", "resource": "keyword", "id": keyword_id}


# ---------------------------------------------------------------------------
# Foods
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def list_foods(query: str | None = None, page: int | None = None) -> Any:
    """List foods (ingredients), optionally filtered by name."""
    return await get_client().list("food", params={"query": query, "page": page})


@mcp.tool()
@_translate_errors
async def create_food(
    name: str,
    plural_name: str | None = None,
    description: str | None = None,
) -> Any:
    """Create a food (ingredient)."""
    data: dict[str, Any] = {"name": name}
    if plural_name is not None:
        data["plural_name"] = plural_name
    if description is not None:
        data["description"] = description
    return await get_client().create("food", data)


@mcp.tool()
@_translate_errors
async def delete_food(food_id: int) -> Any:
    """Delete a food by ID."""
    await get_client().delete("food", food_id)
    return {"status": "deleted", "resource": "food", "id": food_id}


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def list_units(query: str | None = None, page: int | None = None) -> Any:
    """List units of measurement, optionally filtered by name."""
    return await get_client().list("unit", params={"query": query, "page": page})


@mcp.tool()
@_translate_errors
async def create_unit(
    name: str,
    plural_name: str | None = None,
    description: str | None = None,
) -> Any:
    """Create a unit of measurement."""
    data: dict[str, Any] = {"name": name}
    if plural_name is not None:
        data["plural_name"] = plural_name
    if description is not None:
        data["description"] = description
    return await get_client().create("unit", data)


# ---------------------------------------------------------------------------
# Meal types / meal plans
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def list_meal_types() -> Any:
    """List meal types (e.g. Breakfast, Lunch, Dinner) defined in this space."""
    return await get_client().list("meal-type")


@mcp.tool()
@_translate_errors
async def list_meal_plans(from_date: str | None = None, to_date: str | None = None) -> Any:
    """List planned meals.

    Args:
        from_date: ISO date (YYYY-MM-DD) lower bound, inclusive.
        to_date: ISO date (YYYY-MM-DD) upper bound, inclusive.
    """
    return await get_client().list("meal-plan", params={"from_date": from_date, "to_date": to_date})


@mcp.tool()
@_translate_errors
async def create_meal_plan(
    servings: float,
    from_date: str,
    meal_type: int,
    recipe: int | None = None,
    title: str | None = None,
    note: str | None = None,
    to_date: str | None = None,
) -> Any:
    """Schedule a meal.

    Args:
        servings: Number of servings planned.
        from_date: ISO date (YYYY-MM-DD) the meal starts.
        meal_type: ID of an existing meal type (see list_meal_types).
        recipe: Optional recipe ID to attach.
        title: Optional free-text title (used instead of/alongside a recipe).
        note: Optional note, markdown supported.
        to_date: Optional ISO date the meal plan ends (defaults to from_date).
    """
    data: dict[str, Any] = {
        "servings": servings,
        "from_date": from_date,
        "meal_type": meal_type,
    }
    if recipe is not None:
        data["recipe"] = recipe
    if title is not None:
        data["title"] = title
    if note is not None:
        data["note"] = note
    if to_date is not None:
        data["to_date"] = to_date
    return await get_client().create("meal-plan", data)


@mcp.tool()
@_translate_errors
async def update_meal_plan(meal_plan_id: int, data: dict[str, Any]) -> Any:
    """Partially update a meal plan entry (PATCH) with the given fields."""
    return await get_client().update("meal-plan", meal_plan_id, data)


@mcp.tool()
@_translate_errors
async def delete_meal_plan(meal_plan_id: int) -> Any:
    """Delete a meal plan entry by ID."""
    await get_client().delete("meal-plan", meal_plan_id)
    return {"status": "deleted", "resource": "meal-plan", "id": meal_plan_id}


# ---------------------------------------------------------------------------
# Shopping list entries
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def list_shopping_list_entries(checked: bool | None = None, page: int | None = None) -> Any:
    """List shopping list entries.

    Args:
        checked: Filter to only checked (True) or only unchecked (False) items.
        page: 1-based page number.
    """
    return await get_client().list("shopping-list-entry", params={"checked": checked, "page": page})


@mcp.tool()
@_translate_errors
async def create_shopping_list_entry(
    food_id: int,
    amount: float,
    unit_id: int | None = None,
) -> Any:
    """Add an item to the shopping list.

    Args:
        food_id: ID of an existing food (see list_foods).
        amount: Quantity to add.
        unit_id: Optional ID of an existing unit (see list_units).
    """
    data: dict[str, Any] = {"food": {"id": food_id}, "amount": amount}
    if unit_id is not None:
        data["unit"] = {"id": unit_id}
    return await get_client().create("shopping-list-entry", data)


@mcp.tool()
@_translate_errors
async def update_shopping_list_entry(entry_id: int, data: dict[str, Any]) -> Any:
    """Partially update a shopping list entry (PATCH), e.g. {"checked": true}."""
    return await get_client().update("shopping-list-entry", entry_id, data)


@mcp.tool()
@_translate_errors
async def delete_shopping_list_entry(entry_id: int) -> Any:
    """Delete a shopping list entry by ID."""
    await get_client().delete("shopping-list-entry", entry_id)
    return {"status": "deleted", "resource": "shopping-list-entry", "id": entry_id}


# ---------------------------------------------------------------------------
# Recipe books / supermarkets
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def list_recipe_books() -> Any:
    """List recipe books (user-defined recipe collections)."""
    return await get_client().list("recipe-book")


@mcp.tool()
@_translate_errors
async def create_recipe_book(
    name: str,
    description: str | None = None,
    shared_user_ids: list[int] | None = None,
) -> Any:
    """Create a recipe book.

    Args:
        name: Book name.
        description: Optional description.
        shared_user_ids: User IDs to share the book with (empty/omitted = private).
    """
    data: dict[str, Any] = {
        "name": name,
        "shared": [{"id": uid} for uid in (shared_user_ids or [])],
    }
    if description is not None:
        data["description"] = description
    return await get_client().create("recipe-book", data)


@mcp.tool()
@_translate_errors
async def list_supermarkets() -> Any:
    """List supermarkets configured for shopping list category ordering."""
    return await get_client().list("supermarket")


# ---------------------------------------------------------------------------
# Users / spaces (read-only context)
# ---------------------------------------------------------------------------


@mcp.tool()
@_translate_errors
async def list_users() -> Any:
    """List users visible in the current space."""
    return await get_client().list("user")


@mcp.tool()
@_translate_errors
async def list_spaces() -> Any:
    """List spaces (Tandoor's tenant/workspace concept) accessible to this token."""
    return await get_client().list("space")


# ---------------------------------------------------------------------------
# Escape hatch
# ---------------------------------------------------------------------------

_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


@mcp.tool()
@_translate_errors
async def tandoor_api_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> Any:
    """Make a raw request against the Tandoor API for endpoints with no dedicated tool.

    Use this for any of Tandoor's other /api/ resources (e.g. automation,
    cook-log, inventory-entry, storage, sync, property, ...) - see the API
    root at GET /api/ for the full resource list.

    Args:
        method: HTTP method: GET, POST, PUT, PATCH, or DELETE.
        path: Path relative to the API root, e.g. "cook-log/" or "storage/3/".
            Leading "/api/" is optional and stripped if present.
        params: Query string parameters.
        json_body: JSON request body for POST/PUT/PATCH.
    """
    method = method.upper()
    if method not in _ALLOWED_METHODS:
        raise ToolError(f"Unsupported method {method!r}; use one of {sorted(_ALLOWED_METHODS)}")

    clean_path = path.strip()
    if clean_path.startswith("/api/"):
        clean_path = clean_path[len("/api/") :]
    clean_path = clean_path.lstrip("/")
    full_path = f"/api/{clean_path}"

    return await get_client().request(method, full_path, params=params, json_body=json_body)
