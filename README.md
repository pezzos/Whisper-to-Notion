# Project Title

This project is about creating a treasure hunt application where the game master is ChatGPT.

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
git clone <repository_url>
```
Navigate into the project directory:
```bash
cd <project_directory>
```

### Running the program

Before running the program, you need to set the following environment variables:

NOTION: Your Notion token
NOTION_IDEADB: The ID of your Notion database
You can set these variables in your shell, or you can add them to a .env file in the project root.

To run the program, use the following command:
```bash
python3 -m venv env
source env/bin/activate  # On Windows, use `.\env\Scripts\activate`
pip install -r requirements.txt
python main.py
```

### Authors

Alexandre 'Pezzos' Pezzotta 

### License

This project is licensed under the MIT License - see the LICENSE.md file for details