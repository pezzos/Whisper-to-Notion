"""
Library to handle OpenAPI GPT API calls.
"""

# Import necessary modules
# from typing import Optional
# from dataclasses import dataclass, asdict

import logging
import os
import requests

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MAX_RETRIES = 3

# Set loggin config
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename=os.environ.get("LOG_PATH"),
    filemode="w",
)


def transcribe(audio_file_path: str) -> str:
    """
    This function takes a file path as an argument, reads the content
    of the file, and calls the OpenAI Whisper API to generate a response.
    It returns the generated response as a string.

    Args:
        audio_file_path (str): The path to the file.

    Returns:
        str: The generated response from the OpenAI Whisper API.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        logging.error("OPENAI_API_KEY environment variable is not set", exc_info=True)
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    audio_file = open(audio_file_path, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    audio_file.close()

    # Create a file path for the transcript from the audio file path
    transcript_file_path = audio_file_path.replace(".m4a", ".txt")

    # Save the transcript to a file
    with open(transcript_file_path, "w", encoding="utf-8") as f:
        f.write(transcript.text)

    logging.info("Transcription: %s", transcript.text)
    return transcript.text


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
    if not os.environ.get("OPENAI_API_KEY"):
        logging.error("OPENAI_API_KEY environment variable is not set", exc_info=True)
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
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
                logging.warning("Retrying %s/%s...", i + 1, MAX_RETRIES)
                continue  # Try again
            logging.error("Error: %s", e)
            raise  # If this was the last attempt, re-raise the last exception

    # Assuming `completion` is your response object from OpenAI
    content = response.choices[0].message.content if response.choices else ""
    # To test :
    # content = response["choices"][0]["message"]["content"]
    # if response["choices"]
    # else ""

    # Remove double quotes from the content
    logging.debug("The content is: %s", content)
    return content.replace('"', "")


def generate_concept(text: str, language: str) -> str:
    """
    This function improves the clarity of an idea by describing its concept.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve the clarity "
        "of an idea by describing its concept and the related reasons. You do "
        "not add a title, a plan or an how to do this. You are concise yet "
        f"clear. You use simple text for the output. You use {language} as "
        "output language."
    )

    # Define the user message
    user_msg = f"Describe the concept of this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_draft(text: str, target: str, keywords: str, language: str) -> str:
    """
    This function generate a draft for an article.
    """

    # Define the system message
    system_msg = (
        "You are an expert in writing content. You write a draft for a "
        "blog post that is optimized for SEO and includes relevant keywords "
        "and their declinaison for the target audience. You are concise yet "
        "clear. You can split the text into paragraphs with title. If it adds "
        "value to support your texte, you can add actionable tips, advice, "
        "real-life examples or case studies. You use simple text for the "
        "output. You never invent something you can't prove. You add reliable "
        f"sources. You use {language} as output language. The tone is "
        "friendly and approachable, using casual language and relatable "
        "examples to appeal to a wide range of readers. The post should aim "
        "to establish a personal connection with the reader and create a "
        "sense of community. Write in a personal style using singular "
        "first-person pronouns only."
    )

    # Define the user message
    user_msg = (
        f"Craft a blog post about {text} that will engage and inform: {target}. "
        f"Use these keywords: {keywords}."
    )

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_events(text: str, language: str) -> str:
    """
    This function extract the events from a text.
    """

    # Define the system message
    system_msg = (
        "You are an expert to understand content. You extract from the "
        "texts all the described events. You rephrase them and create an "
        "ordered list of them. The person talking is me, so you describe "
        "the task talking about me, you use 'you'. You are concise yet "
        "clear. You use simple list for the output without formatting. "
        f"You use {language} as output language."
    )

    # Define the user message
    user_msg = f"Extract the events from this text: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_excerpt(text: str, keywords: str, language: str) -> str:
    """
    This function generate an excerpt for an article.
    """

    # Define the system message
    system_msg = (
        "You are an expert in making someone wants to read and discover more "
        "about a topic. You create a short text in a few sentences using some "
        f"keywords. You are concise yet clear. You use {language} as output "
        "language. You use simple text for the output. You do not add a title."
    )

    # Define the user message
    user_msg = (
        f"Make someone wanting to read about: {text}. Use "
        f"these keywords if possible: {keywords}"
    )

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_followup(text: str, language: str) -> str:
    """
    This function suggests follow-ups for tasks.
    """

    # Define the system message
    system_msg = (
        "You are an expert in productivity. You suggest follow-ups for "
        "lists of tasks, helping me to avoid missing the big picture or todo."
        "You create an ordered list of them. You are concise yet clear. You "
        "use simple list for the output without formatting. You use "
        f"{language} as output language"
    )

    # Define the user message
    user_msg = f"Suggest followup from these tasks: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_further_reading(text: str, language: str) -> str:
    """
    This function returns sources of information about a subject.
    """

    # Define the system message
    system_msg = (
        "You are an expert in searching real fact. Provide me with a list of "
        "related articles, blog posts, videos, podcasts, books that I can "
        "reference in my blog post for further reading. You are concise yet "
        f"clear. You only output the list without comment. You use {language} "
        "as output language."
    )

    # Define the user message
    user_msg = f"Suggest some sources of information that I can suggest for further reading in my blog post about: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_goals(text: str, language: str) -> str:
    """
    This function improves the clarity of an idea by describing its goals.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve the clarity "
        "of an idea by describing its goals. You do not add a title, a plan "
        f"or an how to do this. You are concise yet clear. You use {language} "
        "as output language."
    )

    # Define the user message
    user_msg = f"Describe the goals of this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_improvements(text: str, language: str) -> str:
    """
    This function improves an idea by suggesting improvement.
    """

    # Define the system message
    system_msg = (
        "You are an expert in adding value to idea. You improve an idea by "
        "suggesting improvements to it, mainly quick wins. You do not add a "
        "title, a plan or an how to do this. You are concise yet clear. You "
        f"create a list of improvement for the output. You use {language} as "
        "output language."
    )

    # Define the user message
    user_msg = f"Suggest improvement to this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_interpretation(text: str, language: str) -> str:
    """
    This function describe the interpretation of a dream, a tought.
    """

    # Define the system message
    system_msg = (
        "You are a professional dream interpreter. From the descriptions "
        "of dreams, and you provide interpretations based on the symbols "
        "and themes present in the dream. Do not provide personal opinions "
        "or assumptions about the dreamer. Provide only factual "
        f"interpretations based on the information given. You use {language} "
        "as output language."
    )

    # Define the user message
    user_msg = f"Interprete this: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_keywords(text: str, language: str) -> str:
    """
    This function generate keywords.
    """

    # Define the system message
    system_msg = (
        "You are an expert in SEO. You suggests the list of keywords "
        "the most relevant that I must use for a topic. You create a list of "
        f"them. You limit this list to 5 items. You use {language} as output "
        "language. You use simple text for the output."
    )

    # Define the user message
    user_msg = f"Find keywords about: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_mood(text: str, language: str) -> str:
    """
    This function extract the moods from a text.
    """

    # Define the system message
    system_msg = (
        "You are an expert to understand emotions and feelings from the diary "
        "of a user. You extract from the texts written by the narator his "
        "general moods and feeling. You create a list of them and limit to "
        "2-3 main moods. You are concise yet clear. You use simple list for "
        f"the output without formatting. You use {language} as output language"
    )

    # Define the user message
    user_msg = f"Extract the moods from this text: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_name(text: str, language: str) -> str:
    """
    This function generates a name to sum up a given text using the OpenAI API.
    It sends a system message and a user message to the API, receives a
    response, removes double quotes from the response content, and returns
    the content.
    """

    # Define the system message
    system_msg = (
        "You are an expert to summarize content. You write a simple and "
        "concise title about a content, it should be no longer than a "
        f"sentence. You use {language} as output language."
    )

    # Define the user message
    user_msg = f"Summarize this text in a title: {text}"

    # Define the model
    model = "gpt-3.5-turbo-1106"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_preparation(text: str, language: str) -> str:
    """
    This function suggests preparation for tasks.
    """

    # Define the system message
    system_msg = (
        "You are an expert in productivity. You suggest preparation to do in "
        "order to easily handle a task, helping me to avoid missing the big "
        "picture or todo. You create an ordered list of them. You are "
        "concise yet clear. You use simple list for the output without "
        f"formatting. You use {language} as output language"
    )

    # Define the user message
    user_msg = "Suggest preparation to do in order to handle these tasks: " f"{text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_recommandations(moods: str, events: str, language: str) -> str:
    """
    This function generate recommandation to self improve based
    on moods and events.
    """

    # Define the system message
    system_msg = (
        "You are an expert to helping person with theirs emotions and "
        "feelings. You suggest recommandations to self improve based "
        "moods and the events occured during the day. The recommandations "
        "are limited to one or two, excluding writing in a diary as it's "
        "already done. The recommendations are easy to put in place. "
        "You create a list of them. You are concise yet clear. You use simple "
        f"list for the output without formatting. You use {language} as "
        "output language."
    )

    # Define the user message
    user_msg = (
        f"Suggest recommandation for user feeling: {moods} and having "
        f"these events today: {events}"
    )

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_results(text: str, language: str) -> str:
    """
    This function describes the expected results.
    """

    # Define the system message
    system_msg = (
        "You are an expert in understanding what could be achieve with an "
        "idea or a project. You describe the expected results for the "
        "end-user if the idea/project is created, its true value. You "
        "do not add a title. You are concise yet clear. You use simple "
        f"text for the output. You use {language} as output language."
    )

    # Define the user message
    user_msg = f"Describe the expected results of this idea: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_target_audience(text: str, language: str) -> str:
    """
    This function returns the target audience of a subject.
    """

    # Define the system message
    system_msg = (
        "You are an marketing expert. You help me to understand who is my "
        "target audience so that I can write a blog post that addresses "
        "their needs. You are concise yet clear. You output simple list of "
        "concise descriptions, 3 at most, without comment. You use "
        f"{language} as output language."
    )

    # Define the user message
    user_msg = f"Provide me a list of target audience for my blog post about: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_tasks(text: str, language: str) -> str:
    """
    This function extract the tasks from a text.
    """

    # Define the system message
    system_msg = (
        "You are an expert to understand content. You extract from the "
        "texts all the described tasks. You rephrase them and create a "
        " list of them. You are concise yet clear. You use simple "
        f"list for the output without formatting. You use {language} "
        "as output language."
    )

    # Define the user message
    user_msg = f"Extract the tasks from this text: {text}"

    # Define the model
    model = "gpt-4-1106-preview"

    # Call the completion function
    return completion(system_msg, user_msg, model)


def generate_title(text: str, language: str) -> str:
    """
    This function generates a title for a given text using the OpenAI API.
    It sends a system message and a user message to the API, receives a
    response, removes double quotes from the response content, and returns
    the content.
    """

    # Define the system message
    system_msg = (
        "You are a motivational title generator. You write powerfull title "
        f"yet simple and concise. You use {language} as output language."
    )

    # Define the user message
    user_msg = f"Write me a title for this text: {text}"

    # Define the model
    model = "gpt-3.5-turbo-1106"

    # Call the completion function
    return completion(system_msg, user_msg, model)
