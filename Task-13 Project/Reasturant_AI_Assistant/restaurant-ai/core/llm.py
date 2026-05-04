import os

def generate_response(prompt: str, context: str = "") -> str:
    """Generate a response using Claude."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "I'm sorry, the AI service is not configured. Please contact support."

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
    except ImportError:
        return "I'm sorry, the AI service is not available. Please contact support."

    full_prompt = f"{context}\n\nUser: {prompt}\n\nAssistant:"

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"