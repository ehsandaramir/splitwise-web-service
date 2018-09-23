from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

transaction_directions = [(0, '+'), (1, '-')]


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, primary_key=True)

    avatar = models.ImageField(null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return '(profile) user:{}'.format(self.user.id)


class Group(models.Model):
    title = models.CharField(max_length=30)
    date_created = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='bill_groups')


class Bill(models.Model):
    title = models.CharField(max_length=63)
    create_date = models.DateTimeField(auto_now_add=True)
    amount = models.CharField(max_length=16)

    creator = models.ForeignKey(User, related_name='bills', on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, related_name='bills', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ('create_date',)

    def __str__(self):
        return '(bill) id:{} title:{} amount:{} creator:{}'.format(
            self.id, self.title, self.amount, self.creator.id)


class Transaction(models.Model):
    bill = models.ForeignKey(Bill, related_name='transactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.DO_NOTHING)
    amount = models.CharField(max_length=16)
    direction = models.CharField(max_length=1, choices=transaction_directions)

    def __str__(self):
        return '(transaction) id:{} bill:{} amount:{} by:{}'.format(
            self.id, self.bill.id, self.amount, self.user.username)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
