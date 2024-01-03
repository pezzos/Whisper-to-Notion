"""
Create the content to send into the Notion database
"""
import datetime
import os

from typing import Optional
from lib.notion import create_new_row
from lib.gpt import (
    generate_title,
    generate_concept,
    generate_results,
    generate_improvements,
)

IDEA = (
    "Je voudrais créer une application pour faire une chasse aux trésors "
    "et le maître du jeu serait ChatGPT"
)

# Define the current date in iso8601 format
date = datetime.datetime.now().isoformat()

notion_token: Optional[str] = os.environ.get("NOTION")
database_id: Optional[str] = os.environ.get("NOTION_IDEADB")

title = generate_title(IDEA)
concept = generate_concept(IDEA)
results = generate_results(IDEA)
improvements = generate_improvements(IDEA)

payload = {
    "Date": {"type": "date", "value": {"start": date}},
    "Title": {"type": "title", "value": title},
    "Concept": {"type": "rich_text", "value": concept},
    "Results": {"type": "rich_text", "value": results},
    "Improvement": {"type": "rich_text", "value": improvements},
    "Input": {"type": "rich_text", "value": IDEA},
}

if notion_token is not None and database_id is not None:
    create_new_row(database_id, notion_token, payload)
