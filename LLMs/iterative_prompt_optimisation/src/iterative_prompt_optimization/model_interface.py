import os
import ollama
import openai
from openai import AzureOpenAI
import anthropic
import google.generativeai as genai
from . import config

MAX_RETRIES = 3

def get_model_output(full_prompt: str, text: str, index: int, total: int):
    """
    Get the output from the selected AI model for a given input.

    This function handles different AI providers and models, including error handling
    and retries. It uses the globally selected model and provider.

    Args:
        full_prompt (str): The complete prompt including system instructions
        text (str): The input text to be processed
        index (int): Current index in the dataset
        total (int): Total number of samples

    Returns:
        str: The model's output, or '0' as a default prediction if all retries fail
    """
    SELECTED_PROVIDER, MODEL_NAME = config.get_model()
    print(f"Processing text {index + 1}/{total}")
    
    for retry in range(MAX_RETRIES):
        try:
            if SELECTED_PROVIDER == "ollama":
                return _get_ollama_output(MODEL_NAME, full_prompt, text)
            elif SELECTED_PROVIDER == "openai":
                return _get_openai_output(MODEL_NAME, full_prompt, text)
            elif SELECTED_PROVIDER == "azure_openai":
                return _get_azure_openai_output(MODEL_NAME, full_prompt, text)
            elif SELECTED_PROVIDER == "anthropic":
                return _get_anthropic_output(MODEL_NAME, full_prompt, text)
            elif SELECTED_PROVIDER == "google":
                return _get_google_output(MODEL_NAME, full_prompt, text)
        except Exception as e:
            print(f"API error for text at index {index}: {str(e)}. Retrying... (Attempt {retry + 1}/{MAX_RETRIES})")
    print(f"Max retries reached. Using default prediction.")
    return '0'  # Default prediction

def _get_ollama_output(model_name, full_prompt, text):
    """Helper function to get output from Ollama models."""
    response = ollama.chat(
        model=model_name,
        messages=[
            {'role': 'system', 'content': full_prompt},
            {'role': 'user', 'content': text},
        ],
        stream=False
    )
    if 'message' in response and 'content' in response['message']:
        return response['message']['content'].strip()
    else:
        raise ValueError("Unexpected Ollama response format")

def _get_openai_output(model_name, full_prompt, text):
    """Helper function to get output from OpenAI models."""
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message['content'].strip()

def _get_azure_openai_output(model_name, full_prompt, text):
    """Helper function to get output from Azure OpenAI models."""
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def _get_anthropic_output(model_name, full_prompt, text):
    """Helper function to get output from Anthropic models."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.completions.create(
        model=model_name,
        prompt=f"{anthropic.HUMAN_PROMPT} {full_prompt}\n\n{text}{anthropic.AI_PROMPT}",
        max_tokens_to_sample=100
    )
    return response.completion.strip()

def _get_google_output(model_name, full_prompt, text):
    """Helper function to get output from Google models."""
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(f"{full_prompt}\n\n{text}")
    return response.text.strip()

def get_analysis(analysis_prompt: str):
    """
    Get an analysis from the selected AI model.

    This function is used for generating analysis of misclassifications
    and suggestions for prompt improvements.

    Args:
        analysis_prompt (str): The prompt for analysis

    Returns:
        str: The model's analysis output, or a default message if all retries fail
    """
    SELECTED_PROVIDER, MODEL_NAME = config.get_model()
    for retry in range(MAX_RETRIES):
        try:
            if SELECTED_PROVIDER == "ollama":
                return _get_ollama_analysis(MODEL_NAME, analysis_prompt)
            elif SELECTED_PROVIDER == "openai":
                return _get_openai_analysis(MODEL_NAME, analysis_prompt)
            elif SELECTED_PROVIDER == "azure_openai":
                return _get_azure_openai_analysis(MODEL_NAME, analysis_prompt)
            elif SELECTED_PROVIDER == "anthropic":
                return _get_anthropic_analysis(MODEL_NAME, analysis_prompt)
            elif SELECTED_PROVIDER == "google":
                return _get_google_analysis(MODEL_NAME, analysis_prompt)
        except Exception as e:
            print(f"API error during analysis: {e}. Retrying... (Attempt {retry + 1}/{MAX_RETRIES})")
    print(f"Max retries reached. Using default analysis.")
    return "Unable to generate analysis due to API errors."

# Helper functions for get_analysis (similar structure to the output helpers)
def _get_ollama_analysis(model_name, analysis_prompt):
    analysis_response = ollama.chat(model=model_name, messages=[
        {'role': 'user', 'content': analysis_prompt},
    ])
    return analysis_response['message']['content'].strip()

# ... (similar helper functions for other providers)