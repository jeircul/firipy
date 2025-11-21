"""Expose the requests-backed client classes at the package root for import."""

from .api import (  # noqa: F401 re-export is intentional
	FiriAPI,
	FiriAPIError,
	FiriHTTPError,
)

__all__ = ["FiriAPI", "FiriHTTPError", "FiriAPIError"]
