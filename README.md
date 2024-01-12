# Whisper To Notion

This project is about simplifying the note taking, the idea dropping, etc.
Thanks to a simple iOS Shortcuts, you capture a little piece of audio and it is brought to Notion and enriched with valuable insight, based on your expectations.
It could be used to:
- maintain a personal diary with external feedback, 
- draft idea of projects, 
- log your daily work and never forget the followup, 
- add tasks to your todolist with informations about preparation, 
- log your dreams and get interpretation, 
- draft an article for a blog...

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need Python 3.8 or later to run this project. You can check your Python version by running:

```bash
python --version
```

### Installing

Clone the repository to your local machine:
```bash
git clone git@github.com:pezzos/Whisper-to-Notion.git   
```
Navigate into the project directory:
```bash
cd Whisper-to-Notion
```

### Running the program

Before running the program, you need to set the following environment variables:
```bash
NOTION: Your Notion token
OPENAI: You OpenAI API Key
```
You can set these variables in your shell, or you can add them to a .env file in the project root.
```bash
vim .zshrc
# then add the following:
export OPENAI="sk-youropenai-api-key"
```

You also neeed to create your config.json:
```bash
mv config.json.template config.json
# then update it according to your setup
```
This file is filed with some example you can use.
Keep in mind that each Notion DB (see: db_id) has fields described in this file and you MUST respect the same name in your Notion DB in order to have it works.
For now, the available fields are:
- Concept: to describe the concept of an idea, a project
- Date: the current date
- Events: the events listed in the text
- Followup: followup suggestions from the tasks in the text
- Goals: to describe the goals of an idea, a project
- Improvements: to describe what could be improved from an idea
- Input: the input received
- Mood: the mood(s) detected in the text
- Name: a name to sumup the content
- Preparation: suggest ideas to prepare a task easily
- Recommendations: suggest ideas to improve yourself from your current mood and events
- Results: the expected results of an idea
- Tasks: extracts the tasks from a text
- Title: give a motivational title to an idea, a project
- Weather

And for technical reasons, some fields are dependant from other and should be listed before the required ones:
- Followup requires Tasks
- Preparation requires Tasks
- Recommendations requires Mood and Events

To run the program, use the following command:
```bash
python3 -m venv env
source env/bin/activate  # On Windows, use `.\env\Scripts\activate`
pip install -r requirements.txt
python main.py
```

To send a file to the server:
```bash
curl -F file=@./test.txt -X POST http://127.0.0.1:5000/
```
Note: this should be done through a Shorcuts within iOS or MacOS

### iOS/MacOS Shortcut

For now, this script is only usable locally.
So, the Shortcut must run on the same computer as this script.

The Shortcut to use it locally is available there:
[Shortcut: Whisper-to-Notion](https://www.icloud.com/shortcuts/b1a0c95e85ad430894dab9856e1d86ad)

### Authors

Alexandre 'Pezzos' Pezzotta 

### License

This project is licensed under the MIT License - see the LICENSE.md file for details

### Fixing some errors
```json
{'object': 'error', 'status': 400, 'code': 'validation_error', 'message': 'Recommendations is not a property that exists.', 'request_id': 'some-caracters'}
```
It means the field you add in the config.json has a different name from your Notion DB, please update your Notion DB.

### TODO

- [ ] Fallback to a default config if no config is found
- [ ] Make it run from a server (not only locally)
- [ ] Add the different keys into the config.json
- [ ] Allow the endpoint to be called by different users
- [ ] Add more examples in a dedicated README.md to understand the different use-cases
- [ ] Output to a Notion page
- [ ] Output to something else (like a blog post)
- [ ] Input: Weather
- [ ] Input: Health and Activity
- [ ] Input: Calendar
- [ ] Add an UI for users to handle their config
