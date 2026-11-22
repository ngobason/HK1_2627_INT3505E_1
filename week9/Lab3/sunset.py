from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps
from flask import request, jsonify
import logging

log = logging.getLogger("sunset")


def http_date(dt):
    return format_datetime(dt, usegmt=True)


def deprecate_at(sunset_date, replacement=None):
    def wrap(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            now = datetime.now(timezone.utc)

            # Sau ngay Sunset: tu choi request
            if now >= sunset_date:
                return jsonify({
                    "error": "gone",
                    "sunset": http_date(sunset_date),
                    "use_instead": replacement
                }), 410

            # Truoc ngay Sunset: API van hoat dong
            result = fn(*args, **kwargs)
            body, status = (
                result if isinstance(result, tuple)
                else (result, 200)
            )

            response = jsonify(body)
            response.status_code = status

            response.headers["Sunset"] = http_date(sunset_date)
            response.headers["Deprecation"] = "true"

            if replacement:
                response.headers["Link"] = (
                    f'<{replacement}>; rel="successor-version"'
                )

            log.warning(
                "deprecated_call %s %s",
                request.path,
                request.remote_addr
            )

            return response

        return inner

    return wrap
