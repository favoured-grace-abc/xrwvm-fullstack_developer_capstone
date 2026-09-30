# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from pathlib import Path
from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
# from .populate import initiate

from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Update the `get_dealerships` view to render list of dealerships all by
# default, particular state if state is passed
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def home(request):
    dealerships = get_request("/fetchDealers") or []
    states = sorted({
        dealer['state']
        for dealer in dealerships
        if dealer.get('state')
    })
    selected_state = request.GET.get('state', '')
    if selected_state:
        dealerships = [
            dealer for dealer in dealerships
            if dealer.get('state') == selected_state
        ]

    return render(
        request,
        'Home.html',
        {
            'dealerships': dealerships,
            'states': states,
            'selected_state': selected_state,
        },
    )


def get_dealer_details(request, dealer_id):
    data_dir = Path(settings.BASE_DIR) / 'database' / 'data'
    with (data_dir / 'dealerships.json').open(encoding='utf-8') as data_file:
        dealerships = json.load(data_file)['dealerships']
    dealer = next(
        (dealer for dealer in dealerships if dealer['id'] == dealer_id),
        None,
    )
    if dealer is None:
        raise Http404('Dealership not found')

    with (data_dir / 'reviews.json').open(encoding='utf-8') as data_file:
        all_reviews = json.load(data_file)['reviews']
    reviews = [
        review for review in all_reviews
        if review['dealership'] == dealer_id
    ]
    return render(
        request,
        'dealer_details.html',
        {'dealer': dealer, 'reviews': reviews},
    )


def post_review_page(request, dealer_id):
    data_dir = Path(settings.BASE_DIR) / 'database' / 'data'
    with (data_dir / 'dealerships.json').open(encoding='utf-8') as data_file:
        dealerships = json.load(data_file)['dealerships']
    dealer = next(
        (dealer for dealer in dealerships if dealer['id'] == dealer_id),
        None,
    )
    if dealer is None:
        raise Http404('Dealership not found')

    if request.method == 'POST':
        review_text = request.POST.get('review', '').strip()
        purchase_date = request.POST.get('purchase_date', '').strip()
        car = request.POST.get('car', '').strip().split(' ', 1)
        car_year = request.POST.get('car_year', '').strip()
        if (
            not review_text
            or not purchase_date
            or len(car) != 2
            or not car_year
        ):
            return render(request, 'post_review.html', {'dealer': dealer})

        reviews_path = data_dir / 'reviews.json'
        with reviews_path.open(encoding='utf-8') as data_file:
            reviews_data = json.load(data_file)
        reviews = reviews_data['reviews']
        reviews.append({
            'id': max((review['id'] for review in reviews), default=0) + 1,
            'name': (
                request.user.username if request.user.is_authenticated
                else 'Guest Reviewer'
            ),
            'dealership': dealer_id,
            'review': review_text,
            'purchase': True,
            'purchase_date': purchase_date,
            'car_make': car[0],
            'car_model': car[1],
            'car_year': int(car_year),
        })
        with reviews_path.open('w', encoding='utf-8') as data_file:
            json.dump(reviews_data, data_file, indent=2)
        return redirect('dealer_details', dealer_id=dealer_id)

    return render(request, 'post_review.html', {'dealer': dealer})


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


@csrf_exempt
@require_GET
def logout_user(request):
    logout(request)
    return JsonResponse({"userName": ""})

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships


def dealers(request):
    return render(request, 'dealers.html',
                  {'dealerships': get_request("/fetchDealers")})


# Create a `get_dealer_details` method which takes the dealer_id as a parameter

def get_cars(request):
    data_path = Path(settings.BASE_DIR) / 'database' / 'data' / 'car_records.json'
    with data_path.open(encoding='utf-8') as data_file:
        cars = json.load(data_file)['cars']

    car_models = sorted({(car['make'], car['model']) for car in cars})
    return JsonResponse({
        'CarModels': [
            {'CarMake': make, 'CarModel': model}
            for make, model in car_models
        ],
    })

def get_dealer_details_api(request, dealer_id):
    # if dealer id has been provided
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealer = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealer})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `get_dealer_reviews` method which takes the dealer_id as a parameter
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create an `add_review` view to submit a review
def add_review(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review",
            })
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
