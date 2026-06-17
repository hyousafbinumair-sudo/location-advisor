import os
import json
from openai import OpenAI

def research_areas(brief: dict) -> list:
    """
    Identifies 3 commercial areas in the brief's city suitable for the business_type.
    Gathers general info on competition level, foot traffic, and typical rent expectations.
    
    Returns a list of 3 dicts: area_name, competition_level, foot_traffic, rent_notes, summary.
    Raises an error if fewer than 3 areas are returned.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or "placeholder" in api_key.lower():
        raise ValueError("Please configure a valid OPENAI_API_KEY in your .env file.")

    client = OpenAI(api_key=api_key)

    city = brief.get("city")
    business_type = brief.get("business_type")
    
    if not city or not business_type:
        raise ValueError("City and business_type must be specified in the brief for research.")

    system_instruction = (
        "You are a local business market research assistant in Pakistan.\n"
        "Your task is to identify exactly 3 well-known commercial areas or neighborhoods in the specified city that are suitable for the given business type.\n"
        "Conduct web searches to retrieve recent, accurate details about:\n"
        "1. competition_level: Must be 'low', 'medium', or 'high'. If not found, use 'data not found'.\n"
        "2. foot_traffic: Must be 'low', 'medium', or 'high'. If not found, use 'data not found'.\n"
        "3. rent_notes: General commercial rent expectations/ranges for a typical shop in that area. If not found, use 'data not found'.\n"
        "4. summary: A 2 to 3 sentence description explaining why this area is relevant for the specified business type.\n\n"
        "Return the result ONLY as a raw JSON list containing exactly 3 objects, each having these keys:\n"
        "- area_name\n"
        "- competition_level\n"
        "- foot_traffic\n"
        "- rent_notes\n"
        "- summary\n\n"
        "Do not include any other conversational text, headers, or markdown formatting outside of optional JSON code fences."
    )

    user_message = f"City: {city}\nBusiness Type: {business_type}\nBudget: {brief.get('budget_pkr')} PKR"

    # Attempt to use gpt-4o-search-preview; fallback to gpt-4o if not available
    try:
        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ]
        )
    except Exception as search_err:
        print(f"Note: gpt-4o-search-preview failed or unavailable. Falling back to gpt-4o. (Detail: {search_err})")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
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
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse GPT response as JSON. Response was: {content}") from e

    if not isinstance(data, list) or len(data) < 3:
        raise ValueError(f"Expected at least 3 research areas in response, but got: {len(data) if isinstance(data, list) else type(data)}")

    # Keep only the first 3 areas
    return data[:3]

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
    
    print(f"Testing research_areas with brief: {test_brief}")
    try:
        results = research_areas(test_brief)
        print("Success! Research Results:")
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error occurred during standalone test: {e}")
