"""Auth placeholder: partner A builds Task 4 here.

Plan (BRIEF.md section 6, rule R7): our own check, not HTTPBearer (which can answer 403). Only
`Authorization: Bearer <API_TOKEN>` passes (token from app.config.get_settings().api_token,
default "superday-demo-token"). Runs before route logic on every route except /health; a
missing, malformed or wrong token gives 401 {"error": "unauthorized", "message": ...}, never 500.
"""
