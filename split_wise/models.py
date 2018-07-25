from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return 'profile: {}'.format(self.user.__str__())


class Bill(models.Model):
    creator = models.ForeignKey(User, related_name='bills', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=63)
    desc = models.CharField(max_length=127, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    amount = models.FloatField(default=0.0)

    class Meta:
        ordering = ('create_date',)


class Payment(models.Model):
    bill = models.ForeignKey(Bill, related_name='payments', on_delete=models.CASCADE)
    paid_by = models.ForeignKey(User, related_name='payments', on_delete=models.DO_NOTHING)
    amount = models.FloatField(default=0.0)

    class Meta:
        ordering = ('bill',)


class Debt(models.Model):
    bill = models.ForeignKey(Bill, related_name='debts', on_delete=models.CASCADE)
    owed_by = models.ForeignKey(User, related_name='debts', on_delete=models.DO_NOTHING)
    amount = models.FloatField(default=0.0)

    class Meta:
        ordering = ('bill',)
