import openai
MAX_TOKENS = 1000
MODEL = "text-davinci-003"
TEMPERATURE = 0.7
# Add OpenI Key Here
API_TOKEN = "sk-JMn2YCnb1zTMqEjpIRXMpixxZyEXU4Uw87jlSTyP"


class OpenAi:
    def __init__(self, max_tokens=MAX_TOKENS, temperature=TEMPERATURE) -> None:
        openai.api_key = API_TOKEN
        self.model = MODEL
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, text: str) -> str:
        response = openai.Completion.create(
            engine=MODEL,
            prompt=text,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=1,
            best_of=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["#", "\"\"\""]
        )
        return response["choices"][0]["text"].strip()
