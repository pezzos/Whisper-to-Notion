"""
Library to handle Notion API calls.

Inspired by: 
https://medium.com/@pratikdeshmukhlobhi2004/notion-api-with-python-916024cb9138
"""

# Import necessary modules
# from typing import Dict
# from dataclasses import dataclass, asdict

import json
import requests


def format_row(payload, db: str):
    """
    This function formats the row to be ready to be inserted in the database.
    """
    sourcelist = []
    comments = []
    row = {
        "parent": {"database_id": db},
        "properties": {},
    }
    properties = row["properties"]
    for item in payload:
        if payload[item]["type"] == "title":
            properties[item] = {
                "title": [{"text": {"content": payload[item]["value"]}}]
            }
        elif payload[item]["type"] == "select":
            properties[item] = {"select": {"name": payload[item]["value"]}}
        elif payload[item]["type"] == "number":
            properties[item] = {"number": payload[item]["value"]}
        elif payload[item]["type"] == "phone":
            properties[item] = {"phone_number": payload[item]["value"]}
        elif payload[item]["type"] == "date":
            properties[item] = {"date": payload[item]["value"]}
        elif payload[item]["type"] == "multi_select":
            sourcelist.append({"name": payload[item]["value"]})
            properties[item] = {"multi_select": sourcelist}
        elif payload[item]["type"] == "rich_text":
            comments.append(
                {"type": "text", "text": {"content": payload[item]["value"]}}
            )
            properties[item] = {
                "rich_text": [
                    {"type": "text", "text": {"content": payload[item]["value"]}}
                ]
            }
    return row


def create_new_row(db: str, token: str, payload):
    """
    This function creates a new row in the database.
    exemple:
    payload = {
        'Name': {"type": "title", "value": "New Row in Table"},
        'Status': {"type": "select", "value": "To Do" }
        }
    create_new_row(database_id, token, payload)
    """
    try:
        headers = {
            "Notion-Version": "2021-05-13",
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }
        url = "https://api.notion.com/v1/pages"
        payload = format_row(payload, db)
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(payload), timeout=10
        )
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error while inserting row in notion.", e)
        return None


def get_page_by_id(token: str, page_id: str):
    """
    This function fetches a page by its ID.
    example: get_page_by_id(token, "59eff577-418d-4ece-bb83-1ee2e3aa51ce")
    """
    try:
        headers = {
            "Notion-Version": "2021-05-13",
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }
        url = "https://api.notion.com/v1/pages/" + page_id
        response = requests.request("GET", url, headers=headers, timeout=10)
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error while fetching page:", e)
        return None


def update_notion_row(db, token, page_id, payload):
    """
    This function updates a row in the database.
    example:
    payload = {
        'Name': {"type": "title", "value": "New Row in Table updated"},
        'Status': {"type": "select", "value": "Done" }
        }
    update_notion_row(database_id ,token, page_id, payload)
    """
    try:
        headers = {
            "Notion-Version": "2021-05-13",
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }
        url = "https://api.notion.com/v1/pages/" + page_id
        payload = format_row(payload, db)
        del payload["parent"]
        response = requests.request(
            "PATCH", url, headers=headers, data=json.dumps(payload), timeout=10
        )
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error while updating row in notion.", e)
        return None


def delete_row_by_id(token, page_id):
    """
    This function deletes a row by its ID.
    example:
    delete_row_by_id(token, "59eff577-418d-4ece-bb83-1ee2e3aa51ce")
    """
    try:
        headers = {
            "Notion-Version": "2021-05-13",
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }
        url = "https://api.notion.com/v1/blocks/" + page_id
        response = requests.request("DELETE", url, headers=headers, timeout=10)
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error while DELETING page...", e)
        return None
