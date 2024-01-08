"""
Create the content to send into the Notion database
"""
import datetime
import json
import os

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from lib.notion import create_new_row
from lib.gpt import (
    generate_concept,
    generate_events,
    generate_followup,
    generate_goals,
    generate_improvements,
    generate_mood,
    generate_name,
    generate_preparation,
    generate_recommandations,
    generate_results,
    generate_tasks,
    generate_title,
    transcribe,
)

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"m4a"}

# Load the JSON config file
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    """
    This function checks if the file extension is allowed
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_config(text: str):
    """
    This function loads the config.json file based on the
    """
    # Get the first sentence of the text, we'll search the first keyword that
    # could match in it
    first_sentence = text.split(".")[0]
    # Load the JSON config file in a Python dictionary
    with open("config.json", encoding="utf-8") as f:
        user_config = json.load(f)
    # Select only one item in the dictionnary, the one that matches the text
    # inside the keywords value
    for destination in user_config["destinations"]:
        # For each word in the first sentence of the text
        for word in first_sentence.split():
            if word in destination["keywords"]:
                user_config = destination
                break
    return user_config


def generate_content(text: str, db: str, fields: list):
    """
    This function generates the content for the Notion database
    """

    # Define the current date in iso8601 format
    date = datetime.datetime.now().isoformat()

    # Define an empty payload
    payload = {}

    for field in fields:
        if field == "Concept":
            concept = generate_concept(text)
            payload[field] = {"type": "rich_text", "value": concept}
        elif field == "Date":
            payload[field] = {"type": "date", "value": {"start": date}}
        elif field == "Events":
            events = generate_events(text)
            payload[field] = {"type": "rich_text", "value": events}
        elif field == "Followup":
            followup = generate_followup(tasks)
            payload[field] = {"type": "rich_text", "value": followup}
        elif field == "Goals":
            goals = generate_goals(text)
            payload[field] = {"type": "rich_text", "value": goals}
        elif field == "Improvements":
            improvements = generate_improvements(text)
            payload[field] = {"type": "rich_text", "value": improvements}
        elif field == "Input":
            payload[field] = {"type": "rich_text", "value": text}
        elif field == "Mood":
            mood = generate_mood(text)
            payload[field] = {"type": "rich_text", "value": mood}
        elif field == "Name":
            name = generate_name(text)
            payload[field] = {"type": "rich_text", "value": name}
        elif field == "Preparation":
            preparation = generate_preparation(tasks)
            payload[field] = {"type": "rich_text", "value": preparation}
        elif field == "Recommendations":
            recommandations = generate_recommandations(mood, events)
            payload[field] = {"type": "rich_text", "value": recommandations}
        elif field == "Results":
            result = generate_results(text)
            payload[field] = {"type": "rich_text", "value": result}
        elif field == "Tasks":
            tasks = generate_tasks(text)
            payload[field] = {"type": "rich_text", "value": tasks}
        elif field == "Title":
            title = generate_title(text)
            payload[field] = {"type": "title", "value": title}
        elif field == "Weather":
            # Todo: call the weather API
            # https://api.openweathermap.org/data/3.0/onecall
            # /day_summary?lat={lat}&lon={lon}&date={date}&tz={tz}&appid={API key}
            payload[field] = {"type": "rich_text", "value": "No implementation yet"}
        else:
            payload[field] = {"type": "rich_text", "value": text}

    create_new_row(db, payload)


@app.route("/", methods=["POST"])
def generate():
    """
    This function generates the content for the Notion database
    """

    # check if the post request has the file part
    if "file" not in request.files:
        return jsonify({"message": "File missing"}), 400

    file = request.files["file"]

    if file is not None and allowed_file(file.filename):
        if file.filename is not None:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        else:
            return jsonify({"message": "Invalid file name"}), 400
    else:
        return jsonify({"message": "Invalid file"}), 400

    idea = transcribe(filepath)
    destination = load_config(idea)
    print(f"Doing:{destination['name']}")
    database_id = destination["db_id"]
    print(f"Db:{database_id}")

    if idea is not None:
        # Call your main function with the idea from the request
        generate_content(idea, database_id, destination["fields"])

        return jsonify({"message": "Success"}), 200
    return jsonify({"message": "No idea provided"}), 400


if __name__ == "__main__":
    app.run(port=5000)
