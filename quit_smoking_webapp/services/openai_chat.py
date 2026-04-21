from google import genai
from django.conf import settings

client = genai.Client(api_key=settings.OPENAI_API_KEY)

prompt = """
You are a supporter inside of Django web app of user who want to quit smoking.
Your role is to help users stay motivated, identify triggers, suggest healthy tips.

Rules:
- Be supportive
- Do not shame user
- Do not provide medical diagnosis
- If user mentions distress, self-harm, chest pain or urgent medical issues, then advise contacting emergency services immediately
- Keep answers fairly short
"""

def get_chatbot_reply(message: str, chat_history) -> str:
    history_text = "\n".join(chat_history)

    full_prompt = f"""
        {prompt}

        Conversation so far:
        {history_text}

        User message:
        {message}
        """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt
    )

    return response.text


