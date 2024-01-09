"""
Library to handle OpenAPI GPT API calls.
"""

# Import necessary modules
# from typing import Optional
# from dataclasses import dataclass, asdict

import os
import requests

from openai import OpenAI, OpenAIError

client = OpenAI(api_key=os.environ.get("OPENAI"))
MAX_RETRIES = 3


def completion(
    system_msg: str, user_msg: str, model: str = "gpt-4-1106-preview"
) -> str:
    """
    This function sends a system message and a user message to the OpenAI API
    and receives a response.
    It then extracts the content from the response, removes double quotes from
    the content, and returns the content.

    Args:
        system_msg (str): The system message to send to the OpenAI API.
        user_msg (str): The user message to send to the OpenAI API.
        model (str, optional): The model to use for the OpenAI API. Defaults
            to 'gpt-4-1106-preview'.

    Returns:
        str: The content from the OpenAI API response, with double quotes
        removed.
    """
    response = {
        "choices": [
            {"message": {"content": "default value"}},
        ]
    }
    for i in range(MAX_RETRIES):
        try:
            # Call the OpenAI API
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_msg,
                    },
                    {
                        "role": "user",
                        "content": user_msg,
                    },
                ],
                # List of available model:
                # https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
                model=model,
            )
            # If the API call is successful, exit the loop
            break
        except (requests.exceptions.Timeout, OpenAIError) as e:
            if i < MAX_RETRIES - 1:  # i is zero indexed
                print(f"Retrying {i+1}/{MAX_RETRIES}...")
                continue  # Try again
            print(f"Error: {e}")
            raise  # If this was the last attempt, re-raise the last exception

    # Assuming `completion` is your response object from OpenAI
    content = response.choices[0].message.content

    # Remove double quotes from the content
    return content.replace('"', "")


def generate_title(text: str) -> str:
    """
    This function generates a title for a given text using the OpenAI API.
    It sends a system message and a user message to the API, receives a
    response, removes double quotes from the response content, and returns
    the content.
    """

    # Define the system message
    system_msg = (
        "You are a motivational title generator. You write powerfull title "
        "yet simple and concise. You use the same language as in the text."
    )

    # Define the user message
    user_msg = f"Write me a title for this text: {text}"

    # Define the model
    model = "gpt-3.5-turbo-1106"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_note(text: str) -> str:
    """
    This function improves the clarity of an idea by adding more context,
    describing goals and expected results.
    It sends a system message and a user message to the OpenAI API, receives a
    response, removes double quotes from the response content, and returns
    the content.

    Args:
        text (str): The idea text that needs to be improved.

    Returns:
        str: The improved idea in JSON format.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve the clarity "
        "of an idea by adding more context, describing goals and expected "
        "results. You do not add a title, a plan or an how to do this. "
        "You are concise yet clear. You use Markdown for the output and "
        "you structure your content in parts to ease readability. You use "
        "the same language as in the text."
    )

    # Define the user message
    user_msg = f"Improve this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_concept(text: str) -> str:
    """
    This function improves the clarity of an idea by describing its concept.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve the clarity "
        "of an idea by describing its concept and the related reasons. You do "
        "not add a title, a plan or an how to do this. You are concise yet "
        "clear. You use simple text for the output. You use the same language "
        "as in the text."
    )

    # Define the user message
    user_msg = f"Describe the concept of this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_results(text: str) -> str:
    """
    This function improves the clarity of an idea by describing its expected
    results.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve the clarity "
        "of an idea by describing its expected result for the end-user. You "
        "do not add a title, a plan or an how to do this. You are concise yet "
        "clear. You use simple text for the output. You use the same language "
        "as in the text."
    )

    # Define the user message
    user_msg = f"Describe the expected results of this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_goals(text: str) -> str:
    """
    This function improves the clarity of an idea by describing its goals.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve the clarity "
        "of an idea by describing its goals. You do not add a title, a plan "
        "or an how to do this. You are concise yet clear. You use simple text "
        "for the output. You use the same language as in the text."
    )

    # Define the user message
    user_msg = f"Describe the goals of this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_improvements(text: str) -> str:
    """
    This function improves an idea by suggesting improvement.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve an idea by "
        "suggesting improvements to it. You do not add a title, a plan or an "
        "how to do this. You are concise yet clear. You use simple text for "
        "the output. You use the same language as in the text."
    )

    # Define the user message
    user_msg = f"Add improvement to this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)
