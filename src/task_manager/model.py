"""The configured model. One call returns the text for one file."""

import json
import urllib.error
import urllib.request


class ModelUnavailable(Exception):
    """The saved model service could not be reached."""


class ScriptedModel:
    """A model that returns fixed text and records each prompt."""

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.text


class HttpModel:
    """One chat request to the saved model service."""

    def __init__(self, name: str, base_url: str, api_key: str | None = None) -> None:
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        body = json.dumps(
            {
                "model": self.name,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Return only the full text of the requested file. "
                            "Do not add an explanation."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            chat_url(self.base_url),
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ModelUnavailable() from None
        try:
            payload = json.loads(raw.decode("utf-8"))
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("The model did not return file text.")
        if not isinstance(content, str):
            raise ValueError("The model did not return file text.")
        return unwrap_fence(content)


def chat_url(base_url: str) -> str:
    trimmed = base_url.rstrip("/")
    if trimmed.endswith("/chat/completions"):
        return trimmed
    return trimmed + "/chat/completions"


def unwrap_fence(text: str) -> str:
    stripped = text.strip()
    if not (stripped.startswith("```") and stripped.endswith("```") and "\n" in stripped):
        return text
    closing = stripped.rfind("```")
    opened = stripped.find("\n")
    inner = stripped[opened + 1 : closing]
    if inner.endswith("\n"):
        return inner
    if closing > 0 and stripped[closing - 1] == "\n":
        return inner + "\n"
    return inner
