# global selected_subject
# config.py
#subject_areas = ['HR', 'Customer Support', 'Medical', 'Inventory', 'Sales', 'Finance', 'Insurance', 'Legal']
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
subject_areas = os.getenv('subject_areas').split(',')
selected_subject = subject_areas[0]
models = os.getenv('models').split(',')
selected_models = models[0]
# database = ['PostgreSQL', 'Oracle', 'SQLite', 'MySQL']
databases = os.getenv('databases').split(',')
selected_database = databases[0]
gauge_config = {
    "Faithfulness": {"value": 95, "color": "green"},
    "Relevancy": {"value": 82, "color": "lightgreen"},
    "Precision": {"value": 80, "color": "yellow"},
    "Recall": {"value": 78, "color": "orange"},
    "Harmfulness": {"value": 15, "color": "green"}
}