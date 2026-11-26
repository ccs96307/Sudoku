"""Firebase Authentication and callable-function REST client for desktop."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

from PySide6.QtCore import QThread, Signal


class FirebaseClientError(RuntimeError):
    """Raised when Firebase rejects a desktop cloud request."""


class FirebaseRestClient:
    """Use Firebase Auth REST and callable Functions without extra packages."""

    def __init__(
        self, api_key: str, project_id: str, google_client_id: str = ""
    ):
        """Initialize the client with Firebase's public app identifiers."""
        self.api_key = api_key
        self.project_id = project_id
        self.google_client_id = google_client_id
        self.id_token = ""
        self.refresh_token = ""
        self.uid = ""
        self.email = ""
        self.display_name = ""

    @classmethod
    def from_environment(cls) -> FirebaseRestClient:
        """Read public Firebase configuration from environment variables."""
        return cls(
            os.getenv("STILL_SUDOKU_FIREBASE_API_KEY", "").strip(),
            os.getenv("STILL_SUDOKU_FIREBASE_PROJECT_ID", "").strip(),
            os.getenv("STILL_SUDOKU_GOOGLE_CLIENT_ID", "").strip(),
        )

    @property
    def configured(self) -> bool:
        """Return whether Firebase API configuration is present."""
        return bool(self.api_key and self.project_id)

    @property
    def signed_in(self) -> bool:
        """Return whether this client currently has an authenticated user."""
        return bool(self.id_token and self.uid)

    def register(self, email: str, password: str, display_name: str) -> dict:
        """Create an email/password account and initialize its profile."""
        result = self._post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}",
            {"email": email, "password": password, "returnSecureToken": True},
        )
        self._accept_auth(result)
        self._post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={self.api_key}",
            {
                "idToken": self.id_token,
                "displayName": display_name,
                "returnSecureToken": True,
            },
        )
        self.display_name = display_name
        self.call("updateProfile", {"displayName": display_name})
        return result

    def sign_in(self, email: str, password: str) -> dict:
        """Sign in with Firebase email/password authentication."""
        result = self._post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}",
            {"email": email, "password": password, "returnSecureToken": True},
        )
        self._accept_auth(result)
        self.display_name = result.get("displayName", "")
        return result

    def sign_in_google(self) -> dict:
        """Sign in with Google using OAuth authorization code and PKCE."""
        if not self.google_client_id:
            raise FirebaseClientError(
                "Set STILL_SUDOKU_GOOGLE_CLIENT_ID first."
            )
        verifier = secrets.token_urlsafe(64)
        challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(verifier.encode("ascii")).digest()
            )
            .decode("ascii")
            .rstrip("=")
        )
        state = secrets.token_urlsafe(24)
        received: dict[str, str] = {}
        ready = threading.Event()

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                query = urllib.parse.parse_qs(
                    urllib.parse.urlparse(self.path).query
                )
                received["state"] = query.get("state", [""])[0]
                received["code"] = query.get("code", [""])[0]
                received["error"] = query.get("error", [""])[0]
                body = (
                    b"You can return to Still Sudoku now. "
                    b"This window may be closed."
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                ready.set()

            def log_message(self, _format, *_args):
                return

        server = HTTPServer(("127.0.0.1", 0), CallbackHandler)
        server.timeout = 120
        redirect_uri = f"http://127.0.0.1:{server.server_port}"
        params = urllib.parse.urlencode(
            {
                "client_id": self.google_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "access_type": "online",
            }
        )
        import webbrowser

        webbrowser.open(
            f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
        )
        try:
            server.handle_request()
        finally:
            server.server_close()
        if not ready.is_set() or received.get("state") != state:
            raise FirebaseClientError(
                "Google sign-in was cancelled or timed out."
            )
        if received.get("error") or not received.get("code"):
            raise FirebaseClientError(
                received.get("error") or "Google sign-in failed."
            )
        token_data = self._post_form(
            "https://oauth2.googleapis.com/token",
            {
                "client_id": self.google_client_id,
                "code": received["code"],
                "code_verifier": verifier,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )
        body = {
            "requestUri": redirect_uri,
            "postBody": urllib.parse.urlencode(
                {
                    "access_token": token_data["access_token"],
                    "providerId": "google.com",
                }
            ),
            "returnIdpCredential": True,
            "returnSecureToken": True,
        }
        result = self._post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={self.api_key}",
            body,
        )
        self._accept_auth(result)
        self.display_name = result.get("displayName", "")
        return result

    def call(self, name: str, data: dict | None = None) -> dict:
        """Call an authenticated Firebase callable Cloud Function."""
        if not self.signed_in:
            raise FirebaseClientError("Sign in to use cloud features.")
        url = f"https://{self._region}-{self.project_id}.cloudfunctions.net/{name}"
        try:
            return self._call_once(url, data or {})
        except FirebaseClientError as error:
            if "401" not in str(error) or not self.refresh_token:
                raise
            refreshed = self._post_form(
                f"https://securetoken.googleapis.com/v1/token?key={self.api_key}",
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            )
            self.id_token = refreshed["id_token"]
            self.refresh_token = refreshed["refresh_token"]
            return self._call_once(url, data or {})

    @property
    def _region(self) -> str:
        return "asia-east1"

    def _call_once(self, url: str, data: dict) -> dict:
        request = urllib.request.Request(
            url,
            data=json.dumps({"data": data}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.id_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        result = self._request(request)
        if "error" in result:
            error = result["error"]
            raise FirebaseClientError(
                error.get("message", "Firebase function failed.")
            )
        return result.get("result", {})

    def _accept_auth(self, result: dict) -> None:
        self.id_token = result["idToken"]
        self.refresh_token = result["refreshToken"]
        self.uid = result["localId"]
        self.email = result.get("email", "")

    def _post(self, url: str, data: dict) -> dict:
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return self._request(request)

    def _post_form(self, url: str, data: dict) -> dict:
        request = urllib.request.Request(
            url,
            data=urllib.parse.urlencode(data).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        return self._request(request)

    @staticmethod
    def _request(request: urllib.request.Request) -> dict:
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            try:
                message = (
                    json.loads(detail).get("error", {}).get("message", detail)
                )
            except json.JSONDecodeError:
                message = detail
            raise FirebaseClientError(
                f"HTTP {error.code}: {message}"
            ) from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise FirebaseClientError(
                f"Could not reach Firebase: {error}"
            ) from error


class CloudTask(QThread):
    """Run one blocking REST operation away from the Qt interface thread."""

    succeeded = Signal(str, object)
    failed = Signal(str, str)

    def __init__(self, action: str, operation):
        """Initialize a named background operation."""
        super().__init__()
        self.action = action
        self.operation = operation

    def run(self):
        """Execute the task and signal its result on completion."""
        try:
            self.succeeded.emit(self.action, self.operation())
        except Exception as error:  # UI surfaces the service error to the user.
            self.failed.emit(self.action, str(error))
