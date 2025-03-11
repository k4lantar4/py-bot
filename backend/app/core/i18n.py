"""Internationalization setup for multi-language support."""

import os
from pathlib import Path
from typing import Dict, Optional

import i18n
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

# Configure i18n
i18n.load_path.append(str(Path(__file__).parent.parent / "locales"))
i18n.set("fallback", "en")
i18n.set("skip_locale_root_data", True)
i18n.set("filename_format", "{locale}.{format}")
i18n.set("enable_memoization", True)
i18n.set("file_format", "json")


def t(key: str, locale: Optional[str] = None, **kwargs) -> str:
    """Translate a string."""
    if locale:
        i18n.set("locale", locale)
    return i18n.t(key, **kwargs)


class I18nMiddleware(BaseHTTPMiddleware):
    """Middleware for handling internationalization."""

    async def dispatch(self, request: Request, call_next):
        """Set language based on request headers or query params."""
        # Try to get language from query params
        lang = request.query_params.get("lang")

        # If not in query params, try Accept-Language header
        if not lang:
            accept_language = request.headers.get("Accept-Language", "")
            lang = accept_language.split(",")[0].strip().split("-")[0]

        # If still no language or not in available languages, use default
        if not lang or lang not in settings.AVAILABLE_LANGUAGES:
            lang = settings.DEFAULT_LANGUAGE

        # Set language for this request
        i18n.set("locale", lang)
        request.state.lang = lang

        response = await call_next(request)
        return response


def setup_i18n(app: FastAPI) -> None:
    """Set up internationalization for the application."""
    # Add i18n middleware
    app.add_middleware(I18nMiddleware)

    # Load translations
    load_translations()


def load_translations() -> None:
    """Load translation files."""
    locales_dir = Path(__file__).parent.parent / "locales"
    if not locales_dir.exists():
        locales_dir.mkdir(parents=True)

    # Create default translation files if they don't exist
    for lang in settings.AVAILABLE_LANGUAGES:
        lang_file = locales_dir / f"{lang}.json"
        if not lang_file.exists():
            create_default_translations(lang_file, lang)


def create_default_translations(file_path: Path, lang: str) -> None:
    """Create default translation file for a language."""
    default_translations: Dict[str, str] = {
        # General
        "welcome": "Welcome" if lang == "en" else "خوش آمدید",
        "error": "Error" if lang == "en" else "خطا",
        "success": "Success" if lang == "en" else "موفقیت",

        # Authentication
        "login": "Login" if lang == "en" else "ورود",
        "logout": "Logout" if lang == "en" else "خروج",
        "register": "Register" if lang == "en" else "ثبت نام",
        "password": "Password" if lang == "en" else "رمز عبور",
        "email": "Email" if lang == "en" else "ایمیل",
        "username": "Username" if lang == "en" else "نام کاربری",

        # Account
        "account": "Account" if lang == "en" else "حساب کاربری",
        "profile": "Profile" if lang == "en" else "پروفایل",
        "settings": "Settings" if lang == "en" else "تنظیمات",
        "balance": "Balance" if lang == "en" else "موجودی",

        # Orders
        "order": "Order" if lang == "en" else "سفارش",
        "orders": "Orders" if lang == "en" else "سفارش‌ها",
        "order_status": "Order Status" if lang == "en" else "وضعیت سفارش",
        "order_date": "Order Date" if lang == "en" else "تاریخ سفارش",

        # Payments
        "payment": "Payment" if lang == "en" else "پرداخت",
        "payments": "Payments" if lang == "en" else "پرداخت‌ها",
        "payment_method": "Payment Method" if lang == "en" else "روش پرداخت",
        "payment_status": "Payment Status" if lang == "en" else "وضعیت پرداخت",

        # Support
        "support": "Support" if lang == "en" else "پشتیبانی",
        "tickets": "Tickets" if lang == "en" else "تیکت‌ها",
        "new_ticket": "New Ticket" if lang == "en" else "تیکت جدید",
        "ticket_status": "Ticket Status" if lang == "en" else "وضعیت تیکت",
    }

    import json
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(default_translations, f, ensure_ascii=False, indent=2) 