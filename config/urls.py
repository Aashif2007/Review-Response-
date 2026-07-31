from django.contrib import admin
from django.urls import path, include
from reviews import views
from business import views as business_views
from reviews import views as review_views

urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "accounts/",
        include("accounts.urls")
    ),

    path(
        "business/",
        include("business.urls")
    ),

    path(
        "reviews/",
        include("reviews.urls")
    ),

    # =====================================================
    # PUBLIC CUSTOMER-FACING PAGES (no login required)
    # =====================================================

    path(
        "b/<slug:slug>/",
        business_views.public_business_page,
        name="business_public"
    ),

    path(
        "b/<slug:slug>/review/",
        review_views.public_add_review,
        name="public_add_review"
    ),
]