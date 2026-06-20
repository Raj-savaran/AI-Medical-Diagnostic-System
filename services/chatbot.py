from utils.config import client

def medical_chat(question):

    prompt = f"""
You are a professional medical assistant.

User Question:
{question}

IMPORTANT:
- Reply in the SAME language as the user.
- Hindi → Hindi
- English → English
- Hinglish → Hinglish
- Use simple language.

Use EXACTLY these sections:

## Possible Cause

## Symptoms

## Home Care

## OTC Medicines

## Specialist Doctor

## Emergency Warning

Do not create any extra headings.
Do not write 'ever symptom'.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
You are an expert medical assistant.

Always answer in the user's language.

Use only these sections:
Possible Cause
Symptoms
Home Care
OTC Medicines
Specialist Doctor
Emergency Warning

Do not invent new headings.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content