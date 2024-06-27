# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Donation, Notification, Badge, User, Profile
from django.db.models import Sum

@receiver(post_save, sender=Donation)
def create_donation_notification(sender, instance, created, **kwargs):
    if created:
        recipient_profile_url = reverse('offer_detail', args=[instance.offer.id])
        donor_profile_url = reverse('view_profile', args=[instance.user.id])

        # Notification for the recipient
        Notification.objects.create(
            user=instance.offer.user,
            donor=instance.user,
            message=(
                f'You have received a donation of {instance.amount} Taka for your offer to '
                f'<a href="{recipient_profile_url}">{instance.offer.destination}</a> from '
                f'<a href="{donor_profile_url}">{instance.user.profile.name}</a>.'
            ),
            type='Donation'
        )

        # Notification for the donor
        Notification.objects.create(
            user=instance.user,
            message=(
                f'You donated {instance.amount} Taka to the offer for '
                f'<a href="{recipient_profile_url}">{instance.offer.destination}</a> by '
                f'<a href="{recipient_profile_url}">{instance.offer.user.profile.name}</a>.'
            ),
            type='Donation'
        )

@receiver(post_save, sender=Profile)
def create_deposit_notification(sender, instance, created, **kwargs):
    if not created:
        deposit_amount = instance.deposit_amount  # Assuming you have this attribute in Profile
        if deposit_amount > 0:
            Notification.objects.create(
                user=instance.user,
                message=f'You have successfully deposited {deposit_amount} Taka to your account.',
                type='Deposit'
            )
            instance.deposit_amount = 0
            instance.save()


@receiver(post_save, sender=Donation)
def award_badges(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        total_donations = Donation.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum']

        thresholds = {
            'Bronze': 10000,
            'Silver': 50000,
            'Gold': 100000,
            'Platinum': 500000,
        }

        for badge_name, threshold in thresholds.items():
            if total_donations >= threshold:
                # Get or create the badge based on the tier name
                badge, created = Badge.objects.get_or_create(name=badge_name)
                user.profile.badges.add(badge)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

