import os
import json
from openai import OpenAI

def extract_brief(user_text: str) -> dict:
    """
    Sends user_text to GPT-4o-mini asking it to extract a JSON object with:
    city, business_type, budget_pkr, notes.
    
    If city or business_type can't be determined, they are set to null instead of guessing.
    Strips markdown fences, parses JSON, and raises a clear error if parsing fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or "placeholder" in api_key.lower():
        raise ValueError("Please configure a valid OPENAI_API_KEY in your .env file.")

    client = OpenAI(api_key=api_key)

    system_instruction = (
        "You are an intake assistant. Extract the following details from the user's business idea into a JSON object:\n"
        "- city: The city in Pakistan they want to set up in. Must be null if not specified or unclear. Do not guess.\n"
        "- business_type: The type of business (e.g., bakery, salon, cafe). Must be null if not specified or unclear. Do not guess.\n"
        "- budget_pkr: The budget in Pakistani Rupees (PKR) as a number or string, or null if not specified.\n"
        "- notes: Any other relevant details from the user request, or null if there are none.\n\n"
        "Return ONLY the JSON object. Do not wrap it in anything other than markdown code fences (optional)."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_text}
        ],
        temperature=0.0
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse GPT response as JSON. Response was: {content}") from e

if __name__ == "__main__":
    import pathlib
    from dotenv import load_dotenv

    # Locate the .env file in the project root
    env_path = pathlib.Path(__file__).parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    test_input = "I have 800000 rupees and want to open a bakery in Lahore"
    print(f"Testing extract_brief with input: '{test_input}'")
    
    try:
        result = extract_brief(test_input)
        print("Success! Parsed Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error occurred during standalone test: {e}")
