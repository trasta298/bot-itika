import os

import google.generativeai as genai
from google.api_core import retry


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

BOT_PROMPT = """
Your Name is Itika (いちか, 一華). You are a bot created by trasta(とらすた).
You are a bot that can answer questions about traP. But always answer what you don't know that you don't know.
You should ask me anything about traP. You must speak in Japanese.

First, you must always refer to the context with get_context before responding.
Also, when a user gives you knowledge related to traP, update the knowledge with update_context by adding to the context retrieved with get_context.

## For example
get_context:
```
{
    "traP": {
        "活動内容": "プログラミングやゲーム制作",
        "所属": "東工大",
    }
}
```
user: traPの代表はtakeno_hitoです。
->
update_context (add to the context):
```
{
    "traP": {
        "活動内容": "プログラミングやゲーム制作",
        "所属": "東工大",
        "代表": "takeno_hito",
    }
}
```

"""

INIT_CONTEXT = """
{
  "traP": {
    "活動内容": "プログラミングやゲーム制作",
    "所属": "東工大",
    "利用SNS": {
        "name: "traQ",
        "説明": "Discordのような部員専用SNS",
    },
    "代表": "takeno_hito",
    "部員数": 674
  }
}
"""


class Llm:
    model_name = "gemini-1.5-pro-latest"
    context = ""

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Llm, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.get_context()
        if not hasattr(self, 'model'):
            self.model = genai.GenerativeModel(
                self.model_name,
                tools=[self.update_context, self.get_context],
                system_instruction=BOT_PROMPT
            )
            self.convo = self.model.start_chat(
                enable_automatic_function_calling=True,
            )

    def get_context(self) -> str:
        """Get context about traP or its surroundings."""
        try:
            with open("/data/context.txt", "r") as f:
                self.context = f.read()
        except FileNotFoundError:
            self.context = INIT_CONTEXT
            with open("/data/context.txt", "w") as f:
                f.write(INIT_CONTEXT)
        return self.context

    def update_context(self, context: str) -> None:
        """Update the context of information about traP based on the information given by the user.
        Even minor information will be updated in the form of additions and alterations to the context given in advance."""
        context = context.replace("\n", "\n")
        self.context = context
        # overwrite the context file
        with open("/data/context.txt", "w") as f:
            f.write(context)
        print(context)

    @retry.Retry(initial=10)
    def send_message(self, message: str) -> str:
        print(f"context: {self.context}\nmessage: {message}")
        res = self.convo.send_message(message)
        return res.text
