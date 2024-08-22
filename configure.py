# global selected_subject
# config.py
subject_areas = ['HR', 'Customer Support', 'Medical', 'Inventory', 'Sales', 'Finance', 'Insurance', 'Legal']
selected_subject = subject_areas[0]
models = ['gpt-4o-mini', 'gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo']
selected_models = models[0]
database = ['PostgreSQL', 'Oracle', 'SQLite', 'MySQL']
selected_database = database[0]
gauge_config = {
    "Faithfulness": {"value": 95, "color": "green"},
    "Relevancy": {"value": 82, "color": "green"},
    "Precision": {"value": 80, "color": "green"},
    "Recall": {"value": 78, "color": "green"},
    "Harmfulness": {"value": 5, "color": "green"}
}