from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Offer, Donation, Profile, Notification, User, SuccessStory, Comment
from .forms import ProfileUpdateForm, OfferCreateForm, DonationForm, SuccessStoryForm, CommentForm, DepositForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json


def home(request):
    offers = Offer.objects.all()

    # Filter based on destination
    destination = request.GET.get('destination')
    if destination:
        offers = offers.filter(destination__icontains=destination)

    travel_date = request.GET.get('travel_date')
    if travel_date:
        try:
            travel_date_parsed = datetime.strptime(travel_date, '%Y-%m-%d').date()
            offers = offers.filter(created_at__date=travel_date_parsed)
        except ValueError:
            # Handle the case where the date format is incorrect
            pass

    paginator = Paginator(offers, 10)
    page = request.GET.get('page')
    try:
        offers = paginator.page(page)
    except PageNotAnInteger:
        offers = paginator.page(1)
    except EmptyPage:
        offers = paginator.page(paginator.num_pages)

    for offer in offers:
        offer.top_donors = offer.get_top_donors()

    return render(request, 'home.html', {'offers': offers})


@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        offer_form = OfferCreateForm(request.POST, request.FILES)
        d_form = DepositForm(request.POST)

        if 'deposit_form' in request.POST:
            if d_form.is_valid():
                amount = d_form.cleaned_data['amount']
                profile.balance += amount
                profile.deposit_amount = amount
                profile.save()
                messages.success(request, f'Successfully deposited {amount} Taka')

                return redirect('profile')

        if 'profile_form' in request.POST:
            if p_form.is_valid():
                if profile:
                    p_form.save()
                else:
                    new_profile = p_form.save(commit=False)
                    new_profile.user = request.user
                    new_profile.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('profile')

        if 'offer_form' in request.POST:
            if offer_form.is_valid():
                new_offer = offer_form.save(commit=False)
                new_offer.user = request.user
                new_offer.save()
                messages.success(request, 'Your offer has been created!')
                return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=profile)
        offer_form = OfferCreateForm()
        d_form = DepositForm()

    offers = Offer.objects.filter(user=request.user)
    donations = Donation.objects.filter(user=request.user).order_by('-created_at')
    badges = profile.badges.all() if profile else []
    total_donated = Donation.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'p_form': p_form,
        'offer_form': offer_form,
        'offers': offers,
        'donations': donations,
        'badges': badges,
        'total_donated': total_donated,
        'd_form': d_form,
    }
    return render(request, 'profile.html', context)

@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    offers = Offer.objects.filter(user=profile_user)

    for offer in offers:
        offer.top_donors = offer.get_top_donors()

    # Retrieve badges for the profile_user
    badges = profile_user.profile.badges.all()
    total_donated = Donation.objects.filter(user=user_id).aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'view_profile.html', {'profile_user': profile_user, 'offers': offers, 'badges': badges, 'total_donated': total_donated})


@login_required
def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id, user=request.user)
    if request.method == 'POST':
        offer.delete()
        messages.success(request, 'Offer has been deleted successfully.')
        return redirect('profile')
    return render(request, 'confirm_delete.html', {'offer': offer})
@login_required
def offer_detail(request, id):
    offer = get_object_or_404(Offer, id=id)
    context = {
        'offer': offer,
    }
    offer.top_donors = offer.get_top_donors()
    return render(request, 'offer_detail.html', context)


@login_required
def donate(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    # Check if the offer has reached its target amount
    if offer.amount_collected >= offer.target_amount:
        messages.error(request, 'This offer has already reached its target amount. You cannot donate to this offer.')
        return redirect('offer_detail', id=offer_id)

    if request.method == 'POST':
        form = DonationForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            profile = request.user.profile

            # Check if user has enough balance
            if profile.balance < amount:
                messages.error(request, 'You do not have enough balance to make this donation.')
                return redirect('donate', offer_id=offer_id)

            # Deduct the donation amount from user's balance
            profile.balance -= amount
            profile.save()

            # Create the donation
            donation = Donation.objects.create(user=request.user, offer=offer, amount=amount)
            donation.save()

            # Update the offer's amount collected
            offer.amount_collected += amount

            # Check if the target amount is reached
            if offer.amount_collected >= offer.target_amount:
                offer.completed = True

                # Create a notification for the offer creator
                Notification.objects.create(
                    user=offer.user,
                    donor=request.user,
                    message=f'Congratulations! Your offer "{offer.destination}" has reached its target amount.',
                    type='Offer Update'
                )

            offer.save()

            request.user.profile.update_badges()

            messages.success(request, 'Donation successful!')
            return redirect('offer_detail', id=offer_id)
    else:
        form = DonationForm()

    return render(request, 'donate.html', {'form': form, 'offer': offer})

@login_required
def success_stories(request):
    if request.method == 'POST':
        form = SuccessStoryForm(request.POST, request.FILES)
        if form.is_valid():
            success_story = form.save(commit=False)
            success_story.user = request.user
            success_story.save()
            messages.success(request, 'Success story uploaded successfully!')
            return redirect('success_stories')  # Adjust the redirect as needed
    else:
        form = SuccessStoryForm()

    success_stories = SuccessStory.objects.all()
    return render(request, 'success_stories.html', {'form': form, 'success_stories': success_stories})

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'notifications': notifications
    }
    return render(request, 'notifications.html', context=context)

@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return redirect('notifications')
def get_highest_badge(user):
    badge_order = {'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4}
    badges = user.profile.badges.all()
    highest_badge = None
    highest_order = 0
    for badge in badges:
        if badge_order[badge.tier] > highest_order:
            highest_badge = badge
            highest_order = badge_order[badge.tier]
    return highest_badge

def leaderboard(request):
    # Aggregate donations by user and order them by total amount in descending order
    donors = Donation.objects.values('user').annotate(total_amount=Sum('amount')).order_by('-total_amount')

    # Get user objects for each donor and attach the total donation amount and highest badge
    leaderboard = []
    for donor in donors:
        user = User.objects.get(id=donor['user'])
        total_amount = donor['total_amount']
        highest_badge = get_highest_badge(user)
        leaderboard.append({'user': user, 'total_amount': total_amount, 'highest_badge': highest_badge})

    return render(request, 'leaderboard.html', {'leaderboard': leaderboard})

@login_required
@require_POST
def add_comment(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    data = json.loads(request.body)  # Load JSON data from the request body
    form = CommentForm(data)  # Pass JSON data to the form
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.offer = offer
        comment.save()
        return JsonResponse({
            'status': 'success',
            'comment': comment.text,
            'user': comment.user.username,
            'created_at': comment.created_at.strftime('%b %d, %Y, %I:%M %p')
        })
    return JsonResponse({'status': 'error', 'errors': form.errors})

def get_comments(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    comments = offer.comments.order_by('-created_at').values(
        'id', 'user__id', 'user__profile__name', 'user__profile__profile_picture', 'text', 'created_at'
    )
    comments_list = list(comments)
    for comment in comments_list:
        comment['user__profile__profile_picture'] = request.build_absolute_uri('/media/' + str(comment['user__profile__profile_picture']))
        comment['created_at'] = comment['created_at'].strftime('%b %d, %Y, %I:%M %p')
        comment['is_owner'] = (comment['user__id'] == request.user.id)
    return JsonResponse({'comments': comments_list})


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return JsonResponse({'status': 'success'})
