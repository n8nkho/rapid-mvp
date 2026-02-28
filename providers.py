import os
from dotenv import load_dotenv
load_dotenv()

class AnthropicProvider:
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.call_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def complete(self, system_prompt, user_prompt, max_tokens=1024):
        msg = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        self.call_count += 1
        self.total_input_tokens += msg.usage.input_tokens
        self.total_output_tokens += msg.usage.output_tokens
        tokens_used = msg.usage.input_tokens + msg.usage.output_tokens
        return {
            "content": msg.content[0].text,
            "tokens_used": tokens_used
        }

def get_provider():
    return AnthropicProvider()

def get_llm_provider():
    return AnthropicProvider()
