from agent_queue_tasks import app

try:
    app.config_from_object('celeryconfig')
    print("Configuration successfully loaded ")
except Exception as e:
    print(f"Error loading configuration: {e}")