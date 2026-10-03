"""The two ways a CRM lookup can fail. Both are ApiErrors, so routes need not catch them.

Task 9 catches CrmUnavailableError to fall back to a stale cached copy; CrmNotFoundError is
never served from cache.
"""

from app.errors import ApiError


class CrmNotFoundError(ApiError):
    def __init__(self, portfolio_id: str) -> None:
        super().__init__(404, "not_found", f"Portfolio {portfolio_id} not found")


class CrmUnavailableError(ApiError):
    def __init__(self, reason: str) -> None:
        super().__init__(503, "crm_unavailable", f"Portfolio data is unavailable: {reason}")
