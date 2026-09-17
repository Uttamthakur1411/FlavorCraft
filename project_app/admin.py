from datetime import date

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count, Sum
from django.urls import reverse

from .models import (
    Contact, CreatorDetail, CreatorReview, Enquiry, Feedback, GiftBox, HomepagePick,
    OrderRequest, Product, RecipeVideo, ShoppingListItem, UserDetail,
)


class FlavorcraftAdminSite(AdminSite):
    site_header = "FlavorCraft Admin"
    site_title = "FlavorCraft Admin"
    index_title = "Recipe Portal"
    index_template = "admin/index.html"
    app_index_template = "admin/app_index.html"

    def index(self, request, extra_context=None):
        today = date.today()
        month_labels = [today.replace(month=month, day=1).strftime("%b") for month in range(1, 13)]

        def monthly_counts(model):
            counts = {month: 0 for month in range(1, 13)}
            primary_key = model._meta.pk.name
            rows = model.objects.filter(date__year=today.year).values("date__month").annotate(total=Count(primary_key))
            for row in rows:
                counts[row["date__month"]] = row["total"]
            return list(counts.values())

        activities = []
        activity_sources = [
            (UserDetail, "User registered", "fa-user"),
            (CreatorDetail, "Creator joined", "fa-chef-hat"),
            (RecipeVideo, "New recipe uploaded", "fa-bowl-food"),
            (Product, "New product added", "fa-bag-shopping"),
            (Feedback, "New review received", "fa-star"),
            (Contact, "New enquiry submitted", "fa-message"),
        ]
        for model, label, icon in activity_sources:
            has_date = any(field.name == "date" for field in model._meta.fields)
            item = model.objects.order_by("-date" if has_date else "-email").first()
            if item:
                title = getattr(item, "name", None) or getattr(item, "product_name", None) or "New activity"
                activities.append({"label": label, "title": title, "date": getattr(item, "date", today), "icon": icon})
        activities.sort(key=lambda activity: activity["date"], reverse=True)

        recent_feedback = Feedback.objects.order_by("-date")[:5]
        recent_contacts = Contact.objects.order_by("-date")[:5]

        context = {
            "dashboard_metrics": [
                {"label": "Users", "value": UserDetail.objects.count(), "icon": "fa-users", "tone": "blue", "url": reverse(f"{self.name}:project_app_userdetail_changelist")},
                {"label": "Creators", "value": CreatorDetail.objects.count(), "icon": "fa-chef-hat", "tone": "orange", "url": reverse(f"{self.name}:project_app_creatordetail_changelist")},
                {"label": "Recipes", "value": RecipeVideo.objects.count(), "icon": "fa-bowl-food", "tone": "green", "url": reverse(f"{self.name}:project_app_recipevideo_changelist")},
                {"label": "Products", "value": Product.objects.count(), "icon": "fa-bag-shopping", "tone": "violet", "url": reverse(f"{self.name}:project_app_product_changelist")},
                {"label": "Reviews", "value": Feedback.objects.count(), "icon": "fa-star", "tone": "yellow", "url": reverse(f"{self.name}:project_app_feedback_changelist")},
                {"label": "Homepage picks", "value": HomepagePick.objects.filter(is_active=True).count(), "icon": "fa-house", "tone": "red", "url": reverse(f"{self.name}:project_app_homepagepick_changelist")},
                {"label": "Enquiries", "value": Contact.objects.count(), "icon": "fa-inbox", "tone": "cyan", "url": reverse(f"{self.name}:project_app_contact_changelist")},
                {"label": "Recipe views", "value": RecipeVideo.objects.aggregate(total=Sum("views"))["total"] or 0, "icon": "fa-eye", "tone": "slate", "url": reverse(f"{self.name}:project_app_recipevideo_changelist")},
            ],
            "growth_labels": month_labels,
            "growth_values": monthly_counts(UserDetail),
            "content_statistics": [
                {"label": "Recipes uploaded", "value": RecipeVideo.objects.count(), "color": "#2d9d78"},
                {"label": "Products added", "value": Product.objects.count(), "color": "#ee8b3a"},
                {"label": "New creators", "value": CreatorDetail.objects.count(), "color": "#6c63d9"},
                {"label": "New users", "value": UserDetail.objects.count(), "color": "#3d8bfd"},
                {"label": "Reviews received", "value": Feedback.objects.count(), "color": "#e5ad37"},
            ],
            "recent_activities": activities[:6],
            "recent_feedback": recent_feedback,
            "recent_contacts": recent_contacts,
            "feedback_admin_url": reverse(f"{self.name}:project_app_feedback_changelist"),
            "contact_admin_url": reverse(f"{self.name}:project_app_contact_changelist"),
            "dashboard_year": today.year,
        }
        if extra_context:
            context.update(extra_context)
        return super().index(request, context)


flavorcraft_admin_site = FlavorcraftAdminSite(name="flavorcraft")


class ContactAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "question_preview", "date"]
    search_fields = ["name", "email", "question"]
    ordering = ["-date"]
    list_per_page = 20
    date_hierarchy = "date"
    readonly_fields = ["date"]

    @admin.display(description="Message")
    def question_preview(self, obj):
        return obj.question[:70] + ("..." if len(obj.question) > 70 else "")


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "rating", "review_preview", "date"]
    search_fields = ["name", "email", "review"]
    ordering = ["-date"]
    list_per_page = 20
    date_hierarchy = "date"
    readonly_fields = ["date"]

    @admin.display(description="Review")
    def review_preview(self, obj):
        return obj.review[:70] + ("..." if len(obj.review) > 70 else "")


class UserDetailAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "date"]
    search_fields = ["name", "email", "phone"]
    ordering = ["-date"]
    list_per_page = 20
    date_hierarchy = "date"
    readonly_fields = ["date"]


class CreatorDetailAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "city", "speciality", "is_verified", "is_blocked"]
    search_fields = ["name", "email", "city"]
    list_filter = ["city", "is_verified", "is_blocked"]
    list_per_page = 20
    fields = ["name", "email", "password", "phone", "city", "speciality", "about_me", "profile_pic", "delivery_radius_km", "response_time_minutes", "is_verified", "is_blocked"]


class RecipeVideoAdmin(admin.ModelAdmin):
    list_display = ["name", "recipe_category", "creator", "likes", "views", "status", "date"]
    list_filter = ["recipe_category", "status", "difficulty", "food_type"]
    search_fields = ["name", "recipe_category", "creator__name"]
    ordering = ["-date"]
    list_per_page = 20
    date_hierarchy = "date"
    list_select_related = ["creator"]
    readonly_fields = ["date"]
    fields = ["creator", "phone", "name", "recipe_category", "ingredients", "recipe_video", "thumbnail", "description", "cooking_time", "difficulty", "food_type", "servings", "likes", "views", "status", "date"]


class HomepagePickAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "city", "tag", "is_active", "sort_order"]
    list_filter = ["city", "is_active"]
    search_fields = ["title", "creator", "city", "description"]
    ordering = ["sort_order", "title"]
    list_per_page = 20
    fields = ["title", "creator", "city", "tag", "image", "description", "is_active", "sort_order"]


class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_name", "category", "creator", "price", "date"]
    list_filter = ["category"]
    search_fields = ["product_name", "category", "creator__name"]
    ordering = ["-date"]
    list_per_page = 20
    date_hierarchy = "date"
    list_select_related = ["creator"]
    readonly_fields = ["date"]


class EnquiryAdmin(admin.ModelAdmin):
    list_display = ["user", "creator", "product", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__name", "creator__name", "message", "reply"]
    readonly_fields = ["created_at", "updated_at"]
    list_select_related = ["user", "creator", "product"]


class GiftBoxAdmin(admin.ModelAdmin):
    list_display = ["name", "creator", "price", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "creator__name", "products__product_name"]
    filter_horizontal = ["products"]
    readonly_fields = ["created_at"]


class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ["order_code", "product", "user", "creator", "quantity", "total", "payment_method", "payment_status", "admin_approved", "status", "created_at"]
    list_filter = ["status", "payment_method", "payment_status", "admin_approved"]
    search_fields = ["product__product_name", "user__name", "creator__name"]
    readonly_fields = ["order_code", "total", "created_at", "updated_at"]
    fields = ["order_code", "user", "creator", "product", "quantity", "total", "delivery_address", "delivery_note", "payment_method", "payment_status", "payment_screenshot", "admin_approved", "status", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        if obj.admin_approved:
            obj.payment_status = "Verified"
            if obj.status == "Pending":
                obj.status = "Accepted"
        super().save_model(request, obj, form, change)
    list_select_related = ["product", "user", "creator"]


class CreatorReviewAdmin(admin.ModelAdmin):
    list_display = ["creator", "user", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["creator__name", "user__name", "text"]
    readonly_fields = ["created_at"]


class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ["ingredient", "quantity", "user", "is_purchased", "created_at"]
    list_filter = ["is_purchased"]
    search_fields = ["ingredient", "user__name"]
    readonly_fields = ["created_at"]


flavorcraft_admin_site.register(Contact, ContactAdmin)
flavorcraft_admin_site.register(Feedback, FeedbackAdmin)
flavorcraft_admin_site.register(UserDetail, UserDetailAdmin)
flavorcraft_admin_site.register(CreatorDetail, CreatorDetailAdmin)
flavorcraft_admin_site.register(RecipeVideo, RecipeVideoAdmin)
flavorcraft_admin_site.register(Product, ProductAdmin)
flavorcraft_admin_site.register(HomepagePick, HomepagePickAdmin)
flavorcraft_admin_site.register(Enquiry, EnquiryAdmin)
flavorcraft_admin_site.register(GiftBox, GiftBoxAdmin)
flavorcraft_admin_site.register(OrderRequest, OrderRequestAdmin)
flavorcraft_admin_site.register(CreatorReview, CreatorReviewAdmin)
flavorcraft_admin_site.register(ShoppingListItem, ShoppingListItemAdmin)

