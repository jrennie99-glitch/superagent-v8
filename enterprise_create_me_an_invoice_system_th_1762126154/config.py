"""
Configuration file for the invoice system.

This module defines configuration settings for the invoice system,
including database connection details, file storage paths,
email configuration, and other application-specific settings.
"""

import os
from typing import Optional, Dict, Any

# ---- Database Configuration ----
DATABASE_HOST: str = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT: int = int(os.environ.get("DATABASE_PORT", "5432"))  # Defaults to PostgreSQL port
DATABASE_NAME: str = os.environ.get("DATABASE_NAME", "invoice_db")
DATABASE_USER: str = os.environ.get("DATABASE_USER", "invoice_user")
DATABASE_PASSWORD: str = os.environ.get("DATABASE_PASSWORD", "secure_password")  # Store in secure vault in production


# ---- File Storage Configuration ----
INVOICE_STORAGE_PATH: str = os.environ.get("INVOICE_STORAGE_PATH", "invoices")
if not os.path.exists(INVOICE_STORAGE_PATH):
    try:
        os.makedirs(INVOICE_STORAGE_PATH)
    except OSError as e:
        print(f"Error creating invoice storage directory: {e}")


# ---- Email Configuration ----
EMAIL_HOST: str = os.environ.get("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT: int = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER: str = os.environ.get("EMAIL_HOST_USER", "user@example.com")
EMAIL_HOST_PASSWORD: str = os.environ.get("EMAIL_HOST_PASSWORD", "secure_email_password") # Store in secure vault in production
EMAIL_USE_TLS: bool = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
DEFAULT_FROM_EMAIL: str = os.environ.get("DEFAULT_FROM_EMAIL", "invoices@example.com")


# ---- SMS Configuration (Optional - using Twilio as example) ----
TWILIO_ACCOUNT_SID: Optional[str] = os.environ.get("TWILIO_ACCOUNT_SID") # Optional
TWILIO_AUTH_TOKEN: Optional[str] = os.environ.get("TWILIO_AUTH_TOKEN") # Optional
TWILIO_PHONE_NUMBER: Optional[str] = os.environ.get("TWILIO_PHONE_NUMBER") # Optional


# ---- Invoice Customization ----
COMPANY_NAME: str = os.environ.get("COMPANY_NAME", "Your Company Name")
COMPANY_ADDRESS: str = os.environ.get("COMPANY_ADDRESS", "123 Main St, Anytown")
COMPANY_CONTACT_EMAIL: str = os.environ.get("COMPANY_CONTACT_EMAIL", "contact@example.com")
COMPANY_CONTACT_PHONE: str = os.environ.get("COMPANY_CONTACT_PHONE", "555-123-4567")
INVOICE_LOGO_PATH: Optional[str] = os.environ.get("INVOICE_LOGO_PATH") # Optional path to company logo

# ---- Security Settings ----
SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev_secret_key") # Change for production
PASSWORD_SALT: str = os.environ.get("PASSWORD_SALT", "dev_password_salt")  # Change for production


# ---- Currency Configuration ----
DEFAULT_CURRENCY: str = os.environ.get("DEFAULT_CURRENCY", "USD")


# ---- Date Format ----
DEFAULT_DATE_FORMAT: str = os.environ.get("DEFAULT_DATE_FORMAT", "%Y-%m-%d")  # YYYY-MM-DD


# ---- Debug Mode ----
DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"


# ---- Rate Limiting (Example using tokens) ----
RATE_LIMIT_MAX_REQUESTS: int = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", "100"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))


# ---- Logging Configuration ----
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FILE: str = os.environ.get("LOG_FILE", "invoice_system.log")



# ---- Configuration Dictionary (for accessing settings programmatically) ----
CONFIG: Dict[str, Any] = {
    "database_host": DATABASE_HOST,
    "database_port": DATABASE_PORT,
    "database_name": DATABASE_NAME,
    "database_user": DATABASE_USER,
    "database_password": DATABASE_PASSWORD,
    "invoice_storage_path": INVOICE_STORAGE_PATH,
    "email_host": EMAIL_HOST,
    "email_port": EMAIL_PORT,
    "email_host_user": EMAIL_HOST_USER,
    "email_host_password": EMAIL_HOST_PASSWORD,
    "email_use_tls": EMAIL_USE_TLS,
    "default_from_email": DEFAULT_FROM_EMAIL,
    "twilio_account_sid": TWILIO_ACCOUNT_SID,
    "twilio_auth_token": TWILIO_AUTH_TOKEN,
    "twilio_phone_number": TWILIO_PHONE_NUMBER,
    "company_name": COMPANY_NAME,
    "company_address": COMPANY_ADDRESS,
    "company_contact_email": COMPANY_CONTACT_EMAIL,
    "company_contact_phone": COMPANY_CONTACT_PHONE,
    "invoice_logo_path": INVOICE_LOGO_PATH,
    "secret_key": SECRET_KEY,
    "password_salt": PASSWORD_SALT,
    "default_currency": DEFAULT_CURRENCY,
    "default_date_format": DEFAULT_DATE_FORMAT,
    "debug": DEBUG,
    "rate_limit_max_requests": RATE_LIMIT_MAX_REQUESTS,
    "rate_limit_window_seconds": RATE_LIMIT_WINDOW_SECONDS,
    "log_level": LOG_LEVEL,
    "log_file": LOG_FILE
}


def get_config(key: str) -> Any:
    """
    Retrieves a configuration value by key.

    Args:
        key: The configuration key.

    Returns:
        The configuration value, or None if the key is not found.
    """
    return CONFIG.get(key)