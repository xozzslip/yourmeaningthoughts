from kombu import Exchange, Queue
BROKER_URL = 'amqp://'

CELERY_DEFAULT_QUEUE = 'app2'
CELERY_QUEUES = (
    Queue('app2', Exchange('app2'), routing_key='app2'),
)
