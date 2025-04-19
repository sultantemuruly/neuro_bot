import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def get_recommendations(history):
    if not OPENAI_API_KEY:
        print("OpenAI API key is missing")
        return "Error: Unable to process recommendations."

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Create a simple formatted summary of user responses
        formatted_input = "Based on the user's responses:\n\n"
        for entry in history:
            question = entry.get("question", "").split("(")[0].strip()
            answer = entry.get("answer", "")
            formatted_input += f"- {question} User answered: {answer}/5\n"

        prompt = (
            formatted_input
            + "\n\nProvide 5 specific, actionable recommendations to improve their neurological wellbeing. Be concise, supportive, and use bullet points."
        )

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a supportive mental health assistant. Provide 5 concise, practical recommendations as bullet points. Start with a brief compassionate acknowledgment and end with an encouraging message. Keep your entire response under 300 words.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.7,
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return "Sorry, I wasn't able to generate recommendations at this time."
