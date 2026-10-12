"""The configured model. One call returns the text for one file."""


class ScriptedModel:
    """A model that returns fixed text and records each prompt."""

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.text
