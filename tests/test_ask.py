import sys
from types import SimpleNamespace

from app import ask


def test_main_reuses_chat_for_follow_up_questions(monkeypatch):
    sent_questions = []

    class FakeChat:
        def send_message(self, question):
            sent_questions.append(question)
            return SimpleNamespace(text=f"回答: {question}", usage_metadata=None)

    class FakeChats:
        def create(self, *, model):
            assert model == ask.MODEL
            return FakeChat()

    class FakeClient:
        chats = FakeChats()

    monkeypatch.setattr(ask.genai, "Client", lambda **kwargs: FakeClient())
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(sys, "argv", ["app.ask", "最初の質問"])
    answers = iter(["続きの質問", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    ask.main()

    assert sent_questions == ["最初の質問", "続きの質問"]