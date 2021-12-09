from enum import Enum
import os

# Auth
class AuthType(Enum):
    INTERNAL = 1
    AZURE = 2

AUTH_TYPE = AuthType.INTERNAL

# Twilio
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_PHONE_NUMBER = os.environ['TWILIO_PHONE_NUMBER']

# Database
MONGODB_URL = os.environ['MONGODB_URL']
MONGODB_DATA = os.environ['MONGODB_DATA']

# Azure oauth
CLIENT_ID = os.environ['CLIENT_ID'] # Application (client) ID of app registration
CLIENT_SECRET = os.environ['CLIENT_SECRET']

AUTHORITY = "https://login.microsoftonline.com/" + os.environ['AUTHORITY']

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
