from config import settings


def get_llm_response(system_prompt: str, user_message: str) -> str:
    """
    Route the LLM request to the configured provider.

    Reads LLM_PROVIDER from settings and delegates to the
    appropriate client (OpenAI or Gemini).

    Args:
        system_prompt: Instructions that define the agent's behavior.
        user_message: The actual input from the student.

    Returns:
        A JSON string with the model's response.

    Raises:
        ValueError: If LLM_PROVIDER is not 'openai' or 'gemini'.
    """
    if settings.llm_provider == "openai":
        return _call_openai(system_prompt, user_message)
    elif settings.llm_provider == "gemini":
        return _call_gemini(system_prompt, user_message)
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def _call_openai(system_prompt: str, user_message: str) -> str:
    """
    Call the OpenAI chat completions API.

    Uses the model and API key defined in settings.
    Forces JSON response format to ensure structured output.

    Args:
        system_prompt: Instructions that define the agent's behavior.
        user_message: The actual input from the student.

    Returns:
        A JSON string with the model's response.
    """
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _call_gemini(system_prompt: str, user_message: str) -> str:
    """
    Call the Google Gemini generative API.

    Uses the model and API key defined in settings.
    The system prompt is passed as a system instruction.

    Args:
        system_prompt: Instructions that define the agent's behavior.
        user_message: The actual input from the student.

    Returns:
        A string with the model's response.
    """
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=system_prompt,
    )
    response = model.generate_content(user_message)
    return response.text
