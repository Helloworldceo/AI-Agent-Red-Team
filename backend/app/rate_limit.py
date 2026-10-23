"""Shared Limiter instance — lives in its own module so both main.py (to
register it + the exception handler) and routes/scans.py (to decorate the
endpoint) can import it without a circular import."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
