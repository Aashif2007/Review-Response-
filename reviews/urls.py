
from django.urls import path
from . import views


urlpatterns = [

    # =====================================================
    # REVIEWS
    # =====================================================

    path(
        "",
        views.review_list,
        name="review_list"
    ),

    # Add new review
    path(
        "add/",
        views.add_review,
        name="add_review"
    ),


    # =====================================================
    # DASHBOARD
    # =====================================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),


    # =====================================================
    # SETTINGS
    # =====================================================

    path(
        "settings/",
        views.settings_page,
        name="settings_page"
    ),


    # =====================================================
    # AI REPLY MANAGEMENT
    # =====================================================

    # Approve AI reply
    path(
        "approve/<int:review_id>/",
        views.approve_reply,
        name="approve_reply"
    ),

    # Reject AI reply
    path(
        "reject/<int:review_id>/",
        views.reject_reply,
        name="reject_reply"
    ),

    # Edit AI reply
    path(
        "edit/<int:review_id>/",
        views.edit_reply,
        name="edit_reply"
    ),

]
