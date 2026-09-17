
from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name="home_page"),
    path("about_us/",views.aboutus,name="about_page"),
    path("contact_us/",views.contactus,name="contact_page"),
    path("faq/",views.faq,name="faq_page"),
    path("user_registration/",views.user_registration,name="user_registration page"),
    path("user_login/",views.user_login,name="user_login page"),
    path("user_feedback/",views.user_feedback,name="user_feedback page"),
    path("user_home/",views.user_home,name="user_home_page"),
    path("edit_profile_action/",views.edit_profile_action,name="edit_profile_action"),
    path("change_password/", views.change_password, name="change_password"),
    path("user_logout/",views.user_logout,name="user_logout_page"),


    path("creator_registration/",views.creator_registration,name="creator_registration page"),
    path("creator_login/",views.creator_login,name="creator_login page"),
    path("creator_home/",views.creator_home,name="creator_home_page"),
        path("creator_edit_profile/",views.creator_edit_profile,name="creator_edit_profile"),
        path("creator_logout/",views.creator_logout,name="creator_logout_page"),
    path("recipe_video/",views.recipe_video,name="recipe_video page"),
    path("my_video/",views.my_video,name="my_video page"),
    path("reviews/",views.reviews,name="user_reviews_page"),
    path("product/",views.product,name="product_page"),
    path("gift-box/<int:gift_box_id>/request/", views.request_gift_box, name="request_gift_box"),
    path("creator/<str:email>/custom-gift-box/", views.request_custom_gift_box, name="request_custom_gift_box"),
    path("delete_product/<int:product_id>/",views.delete_product,name="delete_product"),
    path("search_video/",views.search_video,name="search_video page"),
    path("my_recipe/",views.my_recipe,name="my_recipe page"),
    path("creator/enquiries/", views.creator_enquiries, name="creator_enquiries"),
    path("creator/orders/", views.creator_orders, name="creator_orders"),
    path("creator/<str:email>/enquire/", views.send_enquiry, name="send_enquiry"),
    path("creator/<str:email>/", views.creator_portfolio, name="creator_portfolio"),
    path("orders/", views.user_orders, name="user_orders"),
    path("orders/track/", views.track_order, name="track_order"),
    path("product/<int:product_id>/order/", views.request_order, name="request_order"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("orders/<int:order_id>/receipt/", views.order_receipt, name="order_receipt"),
    path("search/", views.advanced_search, name="advanced_search"),
    path("budget-recipes/", views.budget_recipes, name="budget_recipes"),
    path("recipes/compare/", views.compare_recipes, name="compare_recipes"),
    path("recipes/<int:recipe_id>/calculator/", views.recipe_calculator, name="recipe_calculator"),
    path("shopping-list/", views.shopping_list, name="shopping_list"),

    
    

    
]
