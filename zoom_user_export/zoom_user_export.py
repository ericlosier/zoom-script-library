"""
Zoom Users Export Script
------------------------

This script:
  - Authenticates to the Zoom API using Server-to-Server OAuth
  - Retrieves ALL users in the account
  - Exports them to a timestamped CSV file including login type details

Requirements:
  - Python 3.8+
  - requests

Usage:
  1. Fill in CLIENT_ID, CLIENT_SECRET, and ACCOUNT_ID below from your Zoom app.
  2. Run:
       python zoom_user_export.py
"""

from __future__ import annotations

import base64
import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional

import requests


# ======================
# Configuration
# ======================

# TODO: Fill these in with your Zoom Server-to-Server OAuth app credentials
CLIENT_ID: str = "CLIENT_ID"
CLIENT_SECRET: str = "CLIENT_SECRET"
ACCOUNT_ID: str = "ACCOUNT_ID"

ZOOM_OAUTH_TOKEN_URL = "https://zoom.us/oauth/token"
ZOOM_API_BASE_URL = "https://api.zoom.us/v2"


class ZoomAPIError(RuntimeError):
    """Generic error for Zoom API failures."""


def _encode_basic_auth(client_id: str, client_secret: str) -> str:
    """
    Encode client_id and client_secret for HTTP Basic auth header.
    """
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")


def get_access_token(client_id: str, client_secret: str, account_id: str) -> str:
    """
    Obtain an access token using Zoom Server-to-Server OAuth.

    This uses the "account_credentials" grant type as described in:
    https://developers.zoom.us/docs/api/rest/auth/#overview
    """
    headers = {
        "Authorization": f"Basic {_encode_basic_auth(client_id, client_secret)}",
    }
    params = {
        "grant_type": "account_credentials",
        "account_id": account_id,
    }

    response = requests.post(ZOOM_OAUTH_TOKEN_URL, headers=headers, params=params, timeout=30)
    if response.status_code != 200:
        msg = (
            f"Failed to obtain access token (status={response.status_code}). "
            f"Response: {response.text}"
        )
        raise ZoomAPIError(msg)

    data = response.json()
    access_token = data.get("access_token")
    if not access_token:
        raise ZoomAPIError("Access token not found in OAuth response.")

    return access_token


def map_login_type(code: Optional[int]) -> str:
    """
    Map Zoom login_type integer code to the corresponding value
    from the Zoom Users API login_types enum.

    Known values (subject to change; see Zoom docs):
      0  - Facebook
      1  - Google
      11 - Phone Number
      21 - WeChat (China Only)
      23 - Alipay (China Only)
      24 - Apple
      27 - Microsoft
      97 - Mobile device
      98 - RingCentral
      99 - API user
      100 - Work Email
      101 - Single Sign-On (SSO)
    """
    if code is None:
        return "Unknown"

    mapping = {
        0: "Facebook",
        1: "Google",
        11: "Phone Number",
        21: "WeChat",
        23: "Alipay",
        24: "Apple",
        27: "Microsoft",
        97: "Mobile device",
        98: "RingCentral",
        99: "API user",
        100: "Work Email",
        101: "Single Sign-On (SSO)",
    }
    return mapping.get(code, f"Other ({code})")


@dataclass
class ZoomUser:
    id: str
    email: str
    first_name: str
    last_name: str
    status: str
    type: int
    # A user can have multiple login types (login_types is an array).
    # We store all codes here.
    login_type_codes: List[int]

    @property
    def login_type_label(self) -> str:
        """
        Human-readable labels for all login types, joined by ', '.
        """
        if not self.login_type_codes:
            return "Unknown"
        return ", ".join(map_login_type(code) for code in self.login_type_codes)

    @property
    def login_type_code_str(self) -> str:
        """
        String representation of all login type codes joined by ', '.
        """
        if not self.login_type_codes:
            return ""
        return ", ".join(str(code) for code in self.login_type_codes)

    @classmethod
    def from_list_api(cls, payload: Dict) -> "ZoomUser":
        """
        Create a ZoomUser from the lightweight object returned by GET /users.
        (This does not include login_type.)
        """
        return cls(
            id=payload.get("id", ""),
            email=payload.get("email", ""),
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name", ""),
            status=payload.get("status", ""),
            type=payload.get("type", 0),
            login_type_codes=[],
        )

    @classmethod
    def from_detail_api(cls, payload: Dict) -> "ZoomUser":
        """
        Create a ZoomUser from the full object returned by GET /users/{userId},
        which includes login_types (an array of integer codes).
        """
        raw_login_types = payload.get("login_types", payload.get("login_type"))
        codes: List[int] = []
        if isinstance(raw_login_types, list):
            for item in raw_login_types:
                if item is None:
                    continue
                try:
                    codes.append(int(item))
                except (TypeError, ValueError):
                    continue
        elif isinstance(raw_login_types, int):
            codes = [raw_login_types]

        return cls(
            id=payload.get("id", ""),
            email=payload.get("email", ""),
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name", ""),
            status=payload.get("status", ""),
            type=payload.get("type", 0),
            login_type_codes=codes,
        )


def _get_user_detail(access_token: str, user_id: str) -> Dict:
    """
    Call GET /users/{userId} to retrieve full user details, including login_type.
    Docs: https://developers.zoom.us/docs/api/users/#tag/users/get/users/{userId}
    """
    url = f"{ZOOM_API_BASE_URL}/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        msg = (
            f"Failed to fetch user details for {user_id} (status={resp.status_code}). "
            f"Response: {resp.text}"
        )
        raise ZoomAPIError(msg)
    return resp.json()


def get_zoom_users(access_token: str, page_size: int = 300) -> List[ZoomUser]:
    """
    Retrieve all users from the Zoom account.

    Uses GET /users with pagination via next_page_token.
    """
    url = f"{ZOOM_API_BASE_URL}/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    users: List[ZoomUser] = []
    next_page_token: Optional[str] = None

    while True:
        params = {
            "page_size": page_size,
        }
        if next_page_token:
            params["next_page_token"] = next_page_token

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code != 200:
            msg = (
                f"Failed to fetch users (status={resp.status_code}). "
                f"Response: {resp.text}"
            )
            raise ZoomAPIError(msg)

        data = resp.json()
        api_users = data.get("users", []) or []
        for u in api_users:
            # For each user returned by GET /users, call GET /users/{userId}
            # to obtain login_type and other full details.
            detail_payload = _get_user_detail(access_token, u.get("id", ""))
            users.append(ZoomUser.from_detail_api(detail_payload))

        next_page_token = data.get("next_page_token") or None
        if not next_page_token:
            break

    return users


def write_users_to_csv(users: Iterable[ZoomUser], filename_prefix: str = "zoom_users") -> str:
    """
    Write the given users to a timestamped CSV file.

    Returns the path to the created file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"

    fieldnames = [
        "id",
        "email",
        "first_name",
        "last_name",
        "status",
        "type",
        "login_type_code",
        "login_type_label",
    ]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow(
                {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "status": user.status,
                    "type": user.type,
                    # Both columns contain comma-separated values if there
                    # are multiple login types for a user.
                    "login_type_code": user.login_type_code_str,
                    "login_type_label": user.login_type_label,
                }
            )

    return filename


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET or not ACCOUNT_ID:
        print(
            "ERROR: Please set CLIENT_ID, CLIENT_SECRET, and ACCOUNT_ID "
            "at the top of zoom_user_export.py.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        print("Requesting Zoom access token...")
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID)
        print("Access token obtained.")

        print("Fetching users from Zoom...")
        users = get_zoom_users(access_token)
        print(f"Fetched {len(users)} users.")

        print("Writing users to CSV...")
        csv_path = write_users_to_csv(users)
        print(f"Export complete: {csv_path}")

        if not users:
            print("No users were returned by the Zoom API.")

    except ZoomAPIError as e:
        print(f"Zoom API error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error while communicating with Zoom: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pragma: no cover - generic fallback
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

