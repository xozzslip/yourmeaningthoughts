from datetime import timedelta
from celery.decorators import periodic_task
from posting.models import Community, Target


@periodic_task(run_every=timedelta(seconds=60 * 25))
def post_target():
    community = Community.objects.all()[0]
    target = Target.objects.filter(is_posted=False).order_by('?')[0]
    community.post(target)
    target.posted = True
    target.save()
