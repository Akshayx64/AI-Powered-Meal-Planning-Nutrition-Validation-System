import os

# Kroger API Credentials
# Set these via environment variables before running server.
KROGER_CLIENT_ID = os.getenv("KROGER_CLIENT_ID", "YOUR_KROGER_CLIENT_ID")
KROGER_CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET", "YOUR_KROGER_CLIENT_SECRET")

# Redirect URI for OAuth2 authorization code flow.
KROGER_REDIRECT_URI = os.getenv("KROGER_REDIRECT_URI", "http://localhost:8080/callback")

# Kroger API Environment
# For development, use "https://api-ce.kroger.com" (Certification)
# For production, use "https://api.kroger.com"
KROGER_API_BASE_URL = os.getenv("KROGER_API_BASE_URL", "https://api-ce.kroger.com")
KROGER_AUTHORIZE_URL = f"{KROGER_API_BASE_URL}/v1/connect/oauth2/authorize"
KROGER_TOKEN_URL = f"{KROGER_API_BASE_URL}/v1/connect/oauth2/token"
KROGER_LOCATIONS_URL = f"{KROGER_API_BASE_URL}/v1/locations"
KROGER_PRODUCTS_URL = f"{KROGER_API_BASE_URL}/v1/products"

KROGER_CART_API_URL = f"{KROGER_API_BASE_URL}/v1/cart/addItem" 

