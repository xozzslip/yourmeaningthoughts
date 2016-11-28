from kombu import Exchange, Queue
BROKER_URL = 'amqp://'

CELERY_DEFAULT_QUEUE = 'thoughts'
CELERY_QUEUES = (
    Queue('thoughts', Exchange('thoughts'), routing_key='thoughts'),
)


CELERY_IGNORE_RESULT = True
CELERY_TASK_RESULT_EXPIRES = 10000
CELERY_ALWAYS_EAGER = False

