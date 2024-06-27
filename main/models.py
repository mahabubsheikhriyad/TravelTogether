from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Badge(models.Model):
    BRONZE = 'Bronze'
    SILVER = 'Silver'
    GOLD = 'Gold'
    PLATINUM = 'Platinum'

    TIER_CHOICES = [
        (BRONZE, 'Bronze'),
        (SILVER, 'Silver'),
        (GOLD, 'Gold'),
        (PLATINUM, 'Platinum'),
    ]

    name = models.CharField(max_length=50, choices=TIER_CHOICES, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='badges/')
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notify_donations = models.BooleanField(default=True)
    notify_offers = models.BooleanField(default=True)
    notify_announcements = models.BooleanField(default=True)
    name = models.CharField(max_length=100, null=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    badges = models.ManyToManyField(Badge, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_badges(self):
        total_donations = Donation.objects.filter(user=self.user).aggregate(Sum('amount'))['amount__sum'] or 0

        # Define the donation thresholds
        thresholds = {
            'Bronze': 10000,
            'Silver': 50000,
            'Gold': 100000,
            'Platinum': 500000,
        }

        current_badges = self.badges.all()
        current_badge_tiers = set(current_badges.values_list('tier', flat=True))

        for tier, amount in thresholds.items():
            if total_donations >= amount:
                if tier not in current_badge_tiers:
                    badge, created = Badge.objects.get_or_create(tier=tier)
                    self.badges.add(badge)
            else:
                if tier in current_badge_tiers:
                    badge = Badge.objects.get(tier=tier)
                    self.badges.remove(badge)

    def __str__(self):
        return self.user.username


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.destination}"

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return (self.amount_collected / self.target_amount) * 100
        return 0

    def get_top_donors(self):
        # Aggregate donations by user
        donations = Donation.objects.filter(offer=self).values('user').annotate(total_amount=Sum('amount')).order_by(
            '-total_amount')[:3]
        top_donors = []
        for donation in donations:
            user = User.objects.get(id=donation['user'])
            top_donors.append({'user': user, 'amount': donation['total_amount']})
        return top_donors

class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} donated {self.amount} to {self.offer.destination}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('Donation', 'Donation'),
        ('Offer Update', 'Offer Update'),
        ('Announcement', 'Announcement'),
    ]

    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    donor = models.ForeignKey(User, related_name='donations_made', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='General')

    def __str__(self):
        return f"Notification for {self.user.username}"

class SuccessStory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='success_stories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username}'


