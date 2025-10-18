
import requests
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "insert api key")

def get_llm_interpretation(question, user_answer, correct_answer):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "matthewvaldez.com",
        "X-Title": "TriviaAppTest",
    }
    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": f"""
                Trivia question: {question}
                User's answer: {user_answer}
                Correct answer: {correct_answer}

                Please give a friendly explanation:
                - Why the correct answer is correct.
                - Hint what the user might have been thinking if they were close.
                - Keep it concise and polite.
                """
            }
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        # Safe access
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"Unexpected response format: {data}"

    except Exception as e:
        return f"Error calling OpenRouter API: {str(e)}"


# ---- Test ----
if __name__ == "__main__":
    question = "What is the largest planet in our solar system?"
    user_answer = "Jupiter"
    correct_answer = "Jupiter"

    print("Trivia Chatbot says:\n", get_llm_interpretation(question, user_answer, correct_answer))


