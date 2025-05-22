"""
Application-wide settings and configurations.

This module centralizes configurations for the application. Settings are primarily
loaded from environment variables, with sensible defaults provided for development
or when specific environment variables are not set. This approach allows for
flexible deployment and configuration across different environments (development,
staging, production) without code changes.

To override a default setting, set the corresponding environment variable.
For example, to change the TodayPickup API base URL:
    export TODAY_PICKUP_BASE_URL="http://localhost:8080/mockapi"
"""
import os

# --- TodayPickup API Configuration ---

# Base URL for the TodayPickup API.
# This can be overridden by setting the TODAY_PICKUP_BASE_URL environment variable.
# Defaults to the production API URL if the environment variable is not set.
TODAY_PICKUP_BASE_URL: str = os.getenv("TODAY_PICKUP_BASE_URL", "https://admin.todaypickup.com/api")


# --- Other Potential Configurations (Examples) ---
# These are commented out but show how other settings could be managed.

# Example: General API Key for another service
# API_KEY: Optional[str] = os.getenv("API_KEY") # No default, making it mandatory if used

# Example: Debug mode flag
# DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() in ('true', '1', 't')

# Example: Database URL (though often kept in database.py or a more specific config)
# DATABASE_URL_EXAMPLE: str = os.getenv("DATABASE_URL", "postgresql://user:pass@host:port/db")
