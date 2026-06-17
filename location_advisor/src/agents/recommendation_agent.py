import os
from openai import OpenAI

def generate_recommendation(brief: dict, areas: list) -> str:
    """
    Takes the business brief and a list of 3 researched areas.
    Asks GPT-4o to produce a plain-English recommendation containing:
    1. A top pick with a simple, non-technical reason.
    2. One honest tradeoff sentence for each of the other two areas.
    3. A practical budget tip based on brief['budget_pkr'].
    
    Ensures that no fictitious numbers or details are invented.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or "placeholder" in api_key.lower():
        raise ValueError("Please configure a valid OPENAI_API_KEY in your .env file.")

    client = OpenAI(api_key=api_key)

    system_instruction = (
        "You are a friendly, practical business consultant helping someone start a business in Pakistan.\n"
        "Analyze the provided business brief and the 3 researched areas, then write a simple, plain-English recommendation.\n\n"
        "Your recommendation must cover the following sections:\n"
        "1. **Top Pick**: Name the single best area from the 3 choices clearly, explaining why in simple, non-technical terms a regular person will easily understand.\n"
        "2. **Alternative Areas & Tradeoffs**: Briefly describe the other two areas, providing exactly one honest tradeoff sentence for each.\n"
        "3. **Practical Budget Tip**: Provide one practical piece of advice based on the user's budget.\n\n"
        "STRICT RULES:\n"
        "- Do not use technical jargon.\n"
        "- Never state any specific numbers (like rent prices or competitor counts) that were not explicitly provided in the input area data.\n"
        "- If a field in the input data says 'data not found', acknowledge this limitation honestly rather than inventing details."
    )

    user_message = (
        f"Business Brief:\n{brief}\n\n"
        f"Researched Areas:\n{areas}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    import pathlib
    from dotenv import load_dotenv

    # Locate the .env file in the project root
    env_path = pathlib.Path(__file__).parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    test_brief = {
        "city": "Lahore",
        "business_type": "bakery",
        "budget_pkr": 800000,
        "notes": "Interested in premium location"
    }

    test_areas = [
        {
            "area_name": "Johar Town",
            "competition_level": "medium",
            "foot_traffic": "high",
            "rent_notes": "Commercial shop rents range from PKR 50,000 to PKR 100,000.",
            "summary": "Johar Town has high foot traffic, making it ideal for a bakery."
        },
        {
            "area_name": "Bahria Town",
            "competition_level": "low",
            "foot_traffic": "medium",
            "rent_notes": "data not found",
            "summary": "Bahria Town offers lower competition and a modern setting."
        },
        {
            "area_name": "Wapda Town",
            "competition_level": "medium",
            "foot_traffic": "medium",
            "rent_notes": "A small shop rents for PKR 35,000 per month.",
            "summary": "Wapda Town is a residential neighborhood with a developing market."
        }
    ]

    print("Testing generate_recommendation...")
    try:
        rec = generate_recommendation(test_brief, test_areas)
        print("\nSuccess! Recommendation Output:\n")
        print(rec)
    except Exception as e:
        print(f"Error occurred during standalone test: {e}")
