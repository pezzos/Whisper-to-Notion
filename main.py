"""
Create the content to send into the Notion database
"""
import datetime
import json
import logging
import pytz
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from lib.notion import create_new_row
from lib.gpt import (
    generate_concept,
    generate_draft,
    generate_events,
    generate_excerpt,
    generate_followup,
    generate_further_reading,
    generate_goals,
    generate_improvements,
    generate_interpretation,
    generate_keywords,
    generate_mood,
    generate_name,
    generate_preparation,
    generate_recommandations,
    generate_results,
    generate_target_audience,
    generate_tasks,
    generate_title,
    transcribe,
)

load_dotenv()

# Set loggin config
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename=os.environ.get("LOG_PATH"),
    filemode="w",
)

# Get the script directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Set default settings for the app
UPLOAD_FOLDER = SCRIPT_DIR + "/uploads"
CONFIG_FILE = SCRIPT_DIR + "/config.json"
ALLOWED_EXTENSIONS = {"m4a"}
PORT = os.environ.get("PORT")

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
    # Load the JSON config file in a Python dictionary
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            user_config = json.load(f)
    except FileNotFoundError:
        logging.error("The config.json is not found", exc_info=True)
        user_config = None
    # Select only one item in the dictionnary, the one that matches the text
    # inside the keywords value
    if user_config is not None:
        for word in text.split():
            # Remove any punctuations and lower the word
            normalized_word = word.lower().strip(".,!?")
            word_length = len(normalized_word)
            logging.debug("The word is: %s", normalized_word)
            for destination in user_config["destinations"]:
                logging.debug("The destination is: %s", destination)
                if normalized_word in destination["keywords"]:
                    logging.debug("The destination is: %s", destination)
                    # The rest of the text from the current word is the idea
                    idea: str = "".join(
                        text[text.index(normalized_word) + word_length + 1 :]
                    )
                    logging.debug("The idea is: %s", idea)
                    # Return the destination and the idea
                    return destination, idea
            # If a point is found, then we stop the loop because
            # the keyword is not found
            if "." in word:
                break
        # Fallback to the first item in the config file
        logging.warning("No destination found, using default", exc_info=True)
        return user_config["destinations"][0], text
    else:
        logging.error("No config file found, using default", exc_info=True)
        raise FileNotFoundError


def generate_content(text: str, db: str, fields: list, lang: str):
    """
    This function generates the content for the Notion database
    """

    # Define the current date in iso8601 format
    # Set the timezone to Paris
    timezone = pytz.timezone(os.environ.get("TIME_ZONE"))
    # Get the current time in Paris
    date = datetime.datetime.now(timezone).isoformat()

    # Define an empty payload
    payload = {}

    for field in fields:
        if field == "Concept":
            concept = generate_concept(text, language=lang)
            payload[field] = {"type": "rich_text", "value": concept}
        elif field == "Date":
            payload[field] = {"type": "date", "value": {"start": date}}
        elif field == "Draft":
            draft = generate_draft(text, target, keywords, sources, language=lang)
            payload[field] = {"type": "rich_text", "value": draft}
        elif field == "Events":
            events = generate_events(text, language=lang)
            payload[field] = {"type": "rich_text", "value": events}
        elif field == "Excerpt":
            excerpt = generate_excerpt(text, keywords, language=lang)
            payload[field] = {"type": "rich_text", "value": excerpt}
        elif field == "Followup":
            followup = generate_followup(tasks, language=lang)
            payload[field] = {"type": "rich_text", "value": followup}
        elif field == "Reading":
            further_reading = generate_further_reading(text, language=lang)
            payload[field] = {"type": "rich_text", "value": further_reading}
        elif field == "Goals":
            goals = generate_goals(text, language=lang)
            payload[field] = {"type": "rich_text", "value": goals}
        elif field == "Improvements":
            improvements = generate_improvements(text, language=lang)
            payload[field] = {"type": "rich_text", "value": improvements}
        elif field == "Interpretation":
            interpretation = generate_interpretation(text, language=lang)
            payload[field] = {"type": "rich_text", "value": interpretation}
        elif field == "Keywords":
            keywords = generate_keywords(text, language=lang)
            payload[field] = {"type": "rich_text", "value": keywords}
        elif field == "Input":
            payload[field] = {"type": "rich_text", "value": text}
        elif field == "Mood":
            mood = generate_mood(text, language=lang)
            payload[field] = {"type": "rich_text", "value": mood}
        elif field == "Name":
            name = generate_name(text, language=lang)
            payload[field] = {"type": "title", "value": name}
        elif field == "Preparation":
            preparation = generate_preparation(tasks, language=lang)
            payload[field] = {"type": "rich_text", "value": preparation}
        elif field == "Recommendations":
            recommandations = generate_recommandations(mood, events, language=lang)
            payload[field] = {"type": "rich_text", "value": recommandations}
        elif field == "Results":
            result = generate_results(text, language=lang)
            payload[field] = {"type": "rich_text", "value": result}
        elif field == "Target":
            target = generate_target_audience(text, language=lang)
            payload[field] = {"type": "rich_text", "value": target}
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

    # Trasncribe the audio file
    idea = transcribe(filepath)

    # Load the config file
    destination, idea = load_config(idea)
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
    app.run(host="0.0.0.0", port=PORT)
