"""
Create the content to send into the Notion database
"""
import datetime
import json
import logging
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

# Set loggin config
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="main.log",
    filemode="w",
)

# Set default settings for the app
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"m4a"}

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
    # Initialize user_config variable
    user_config = None
    try:
        with open("config.json", encoding="utf-8") as f:
            user_config = json.load(f)
    except FileNotFoundError:
        logging.error("The config.json is not found", exc_info=True)
    # Select only one item in the dictionnary, the one that matches the text
    # inside the keywords value
    if user_config is not None:
        for destination in user_config["destinations"]:
            # For each word in the first sentence of the text
            for word in first_sentence.split():
                if word in destination["keywords"]:
                    user_config = destination
                    break
        return user_config
    logging.error("The config.json is empty", exc_info=True)
    return None


def generate_content(text: str, db: str, fields: list, lang: str):
    """
    This function generates the content for the Notion database
    """

    # Define the current date in iso8601 format
    date = datetime.datetime.now().isoformat()

    # Define an empty payload
    payload = {}

    for field in fields:
        if field == "Concept":
            concept = generate_concept(text, language=lang)
            payload[field] = {"type": "rich_text", "value": concept}
        elif field == "Date":
            payload[field] = {"type": "date", "value": {"start": date}}
        elif field == "Events":
            events = generate_events(text, language=lang)
            payload[field] = {"type": "rich_text", "value": events}
        elif field == "Followup":
            followup = generate_followup(tasks, language=lang)
            payload[field] = {"type": "rich_text", "value": followup}
        elif field == "Goals":
            goals = generate_goals(text, language=lang)
            payload[field] = {"type": "rich_text", "value": goals}
        elif field == "Improvements":
            improvements = generate_improvements(text, language=lang)
            payload[field] = {"type": "rich_text", "value": improvements}
        elif field == "Input":
            payload[field] = {"type": "rich_text", "value": text}
        elif field == "Mood":
            mood = generate_mood(text, language=lang)
            payload[field] = {"type": "rich_text", "value": mood}
        elif field == "Name":
            name = generate_name(text, language=lang)
            payload[field] = {"type": "rich_text", "value": name}
        elif field == "Preparation":
            preparation = generate_preparation(tasks, language=lang)
            payload[field] = {"type": "rich_text", "value": preparation}
        elif field == "Recommendations":
            recommandations = generate_recommandations(mood, events, language=lang)
            payload[field] = {"type": "rich_text", "value": recommandations}
        elif field == "Results":
            result = generate_results(text, language=lang)
            payload[field] = {"type": "rich_text", "value": result}
        elif field == "Tasks":
            tasks = generate_tasks(text, language=lang)
            payload[field] = {"type": "rich_text", "value": tasks}
        elif field == "Title":
            title = generate_title(text, language=lang)
            payload[field] = {"type": "title", "value": title}
        elif field == "Weather":
            # Todo: call the weather API
            # https://api.openweathermap.org/data/3.0/onecall
            # /day_summary?lat={lat}&lon={lon}&date={date}&tz={tz}&appid={API key}
            payload[field] = {"type": "rich_text", "value": "No implementation yet"}
        else:
            payload[field] = {"type": "rich_text", "value": text}
    logging.debug("The payload is: %s", payload)
    create_new_row(db, payload)


@app.route("/", methods=["POST"])
def generate():
    """
    This function generates the content for the Notion database
    """

    # check if the post request has the file part
    if "file" not in request.files:
        logging.error("No file in the POST request", exc_info=True)
        return jsonify({"message": "File missing"}), 400

    file = request.files["file"]
    logging.debug("The file is: %s", file)

    if file is not None and allowed_file(file.filename):
        if file.filename is not None:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            logging.debug("The file path is: %s", filepath)
        else:
            logging.error("The file name is invalid", exc_info=True)
            return jsonify({"message": "Invalid file name"}), 400
    else:
        logging.error("The file is invalid", exc_info=True)
        return jsonify({"message": "Invalid file"}), 400

    idea = transcribe(filepath)
    destination = load_config(idea)
    logging.debug("The destination is: %s", destination)
    print(f"Doing:{destination['name']}")
    database_id = destination["db_id"]
    logging.debug("The database id is: %s", database_id)
    print(f"Db:{database_id}")

    if idea is not None:
        # Call your main function with the idea from the request
        generate_content(
            idea, database_id, destination["fields"], destination["language"]
        )
        logging.debug("The content is generated")
        return jsonify({"message": "Success"}), 200
    logging.error("No idea provided", exc_info=True)
    return jsonify({"message": "No idea provided"}), 400


if __name__ == "__main__":
    app.run(port=5000)
