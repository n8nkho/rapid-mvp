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

    def complete(self, prompt, system=""):
        msg = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system or "You are RAPID, an SAP implementation assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        self.call_count += 1
        self.total_input_tokens += msg.usage.input_tokens
        self.total_output_tokens += msg.usage.output_tokens
        return msg.content[0].text

def get_llm_provider():
    return AnthropicProvider()
