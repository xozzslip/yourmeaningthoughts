import math
from django.db import models
from django.db import transaction
from django.db.utils import IntegrityError
from vk.custom_api import PublicApiCommands
from img.render import render

FORBID = ["instagram", "ints", "twitter", "facebook", ".ru", ".com", "http", "ask", "выплаты", "продам", "whatsup", "inst", "нах", "ху", "пизд", "пид", "еб", "сука", "viber", "whatsapp", "куплю", "periscope", "89", "+79", "лс", "л.с", "тел", "http"]
ALLOWED_LETTERS = list(""":;'"?!.,-_~}{[]\/ `+=*)(йцукенгшёщзхъфывапролджэячсмитьбюqwertyuiіopasdfghjklzxcvbnm1234567890\n""")


class TargetManager(models.Manager):
    @transaction.atomic
    def upload(self, domen, count=None):
        api = PublicApiCommands(access_token="", domen=domen)
        total_count, members = api.get_members(domen=domen, count=10)
        initial_offset = math.ceil(total_count * 0.5)
        members = api.get_members_extended(domen, count=count, initial_offset=initial_offset)
        for user in members:
            if "status" not in user:
                continue
            status = self.rewrite_status(user["status"])
            if not self.is_status_ok(user["status"]):
                continue
            if not self.is_target_ok(user):
                continue
            try:
                Target(name=user["first_name"] + " " + user["last_name"],
                       status=status,
                       vk_id=user["id"]).save()
            except IntegrityError:
                continue

    def refresh(self, domen, count=None):
        self.all().delete()
        self.upload(domen, count=count)

    def is_status_ok(self, status):
        status = status.lower()
        if any(word in FORBID for word in status.split()):
            return False
        if len(status) < 3:
            return False
        return True

    def rewrite_status(self, status):
        status_allowed_symbols = ""
        for l in list(status.lower()):
            if l in ALLOWED_LETTERS:
                status_allowed_symbols += l
        return status_allowed_symbols

    def is_target_ok(self, user):
        if user['sex'] == 2:
            return False
        if 'bdate' in user:
            bdate = user['bdate'].split('.')
            if len(bdate) == 3 and int(bdate[-1]) > 1992:
                return False
        return True


class Target(models.Model):
    name = models.CharField(max_length=300)
    status = models.TextField()
    vk_id = models.IntegerField()
    is_posted = models.BooleanField(default=False)

    objects = TargetManager()

    class Meta:
        unique_together = (("name", "status"),)


class Community(models.Model):
    group_id = models.IntegerField()
    access_token = models.CharField(max_length=500)

    @property
    def api(self):
        return PublicApiCommands(access_token=self.access_token, domen=self.group_id)

    def post(self, target):
        pil_image = render(text=target.status, signature=target.name)
        path = pil_image.save()
        with open(path, 'rb') as photo:
            attachment = self.api.upload_picture(photo=photo)
        self.api.create_post(text="%s\n\n@id%s" % (target.status, target.vk_id),
                             attachments=attachment)
