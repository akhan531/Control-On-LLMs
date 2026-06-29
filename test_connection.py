import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads your .env file

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

resp = client.chat.completions.create(
    model="qwen/qwen3-8b",
    messages=[{"role": "user", "content": "Reply with a short compliment"}],
    max_tokens=20,
)

print(resp.choices[0].message.content)