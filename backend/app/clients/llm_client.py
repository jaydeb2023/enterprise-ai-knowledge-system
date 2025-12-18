from groq import Groq
import os

class LLMClient:
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate answer using Groq LLM.
        prompt: Full context + question string
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.3,      # Low for factual answers
                max_tokens=1024,
                top_p=1,
                stream=False,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")