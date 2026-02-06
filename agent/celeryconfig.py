broker_url = 'redis://localhost:6379/1'
result_backend = 'redis://localhost:6379/1'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Singapore'
enable_utc = True

# Result expires after 1 minute
result_expires = 600

# Rate limit example: limit to 100 tasks per minute
#task_default_rate_limit = '1/m' 
task_annotations = {
    'some_process': {'rate_limit': '100/m'},
    'invoke_agent_celery_task': {'rate_limit': '100/m'},
    'invoke_agent_langfuse_celery_task': {'rate_limit': '100/m'}
}

# this is the wrong way and does not work:
# task_annotations = {
#     'celery_test.some_process': {'rate_limit': '1/m'}
# }