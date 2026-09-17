from datetime import date, timedelta
from decimal import Decimal
import re

from django.db.models import Avg, F, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from.models import (
    Feedback, Contact, UserDetail, CreatorDetail, RecipeVideo, Product, HomepagePick,
    CreatorReview, Enquiry, GiftBox, OrderRequest, ShoppingListItem,
)
from django.contrib import messages


INGREDIENT_RATES = {
    "paneer": Decimal("280"), "potato": Decimal("35"), "aloo": Decimal("35"),
    "onion": Decimal("40"), "pyaz": Decimal("40"), "tomato": Decimal("50"),
    "rice": Decimal("70"), "flour": Decimal("50"), "atta": Decimal("50"),
    "besan": Decimal("90"), "chickpea": Decimal("110"), "dal": Decimal("120"),
    "milk": Decimal("60"), "curd": Decimal("80"), "oil": Decimal("140"),
    "ghee": Decimal("600"), "sugar": Decimal("50"), "masala": Decimal("350"),
    "spice": Decimal("350"), "salt": Decimal("25"), "chilli": Decimal("220"),
}


def estimate_recipe_cost(ingredients):
    total = Decimal("0")
    for line in (ingredients or "").splitlines():
        text = line.strip().lower()
        if not text:
            continue
        rate = next((value for keyword, value in INGREDIENT_RATES.items() if keyword in text), Decimal("20"))
        quantity = re.search(r"(\d+(?:\.\d+)?)\s*(kg|g|l|ml|tbsp|tsp)?", text)
        if quantity:
            amount = Decimal(quantity.group(1))
            unit = quantity.group(2) or "portion"
            multiplier = {"g": Decimal("0.001"), "ml": Decimal("0.001"), "tbsp": Decimal("0.05"), "tsp": Decimal("0.03")}.get(unit, Decimal("1"))
            total += rate * amount * multiplier
        else:
            total += rate * Decimal("0.25")
    return total.quantize(Decimal("1"))



def home(request):
    city_filter = (request.GET.get("city") or "").strip()

    products = Product.objects.select_related("creator").order_by("-date")[:8]
    creators = CreatorDetail.objects.order_by("-name")
    if city_filter:
        creators = creators.filter(city__icontains=city_filter)
    creators = creators[:6]

    trending_recipes = RecipeVideo.objects.filter(status="Published").order_by("-views", "-likes", "-date")[:4]
    today_picks = HomepagePick.objects.filter(is_active=True)[:4]

    taste_cards = [
        {"label": "Vegetarian", "icon": "fa-leaf"},
        {"label": "Spicy", "icon": "fa-pepper-hot"},
        {"label": "Sweet", "icon": "fa-cake-candles"},
        {"label": "Healthy", "icon": "fa-heart-pulse"},
        {"label": "Quick", "icon": "fa-clock"},
        {"label": "Regional", "icon": "fa-map-location-dot"},
    ]

    cart = request.session.get("cart", {})
    return render(request, "html/index.html", {
        "products": products,
        "creators": creators,
        "trending_recipes": trending_recipes,
        "today_picks": today_picks,
        "taste_cards": taste_cards,
        "selected_city": city_filter,
        "cart_count": sum(cart.values()),
    })
def aboutus(request):
    return render(request,"html/about_us.html")
def contactus(request):
    if request.method=="GET":
    
       return render(request,"html/contact_us.html")
    if request.method=="POST":
        nm=request.POST["name"]
        em=request.POST["email"]
        ph=request.POST["phone"]
        qt=request.POST["question"]
        ##craeting object of Contact Model class
        c=Contact(name=nm,email=em,phone=ph,question=qt)
        c.save()##it write insert data into contact table
        messages.success(request,"Thank you for Contact")
        return redirect("contact_page")

    

def faq(request):
    return render(request,"html/faq.html")
def user_registration(request):
    if request.method=="GET":
        return render(request,"creator/creator_registration.html", {"registration_role": "user"})
    if request.method=="POST":
        nm=request.POST["name"]
        em=request.POST["email"].strip().lower()
        ps=request.POST["password"]
        ph=request.POST["phone"]
        pic=request.FILES.get("profile_pic")
        if UserDetail.objects.filter(email__iexact=em).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("user_registration page")
        u=UserDetail(name=nm,email=em,password=ps,phone=ph,profile_pic=pic)
        u.save()##insert data into UserField table
        return redirect("user_login page")
    

def user_login(request):
    if request.method == "GET":
        if request.session.get("role") == "user" and _session_user(request):
            return redirect("user_home_page")
        return render(request, "user/user_login.html")

    if request.method == "POST":
        em = (request.POST.get("email") or "").strip().lower()
        ps = (request.POST.get("password") or "").strip()

        if not em or not ps:
            messages.error(request, "Email and password are required.")
            return redirect("user_login page")

        user_list = UserDetail.objects.filter(email__iexact=em, password=ps)
        if user_list.exists():
            request.session["session_key"] = em
            request.session["role"] = "user"
            request.session.set_expiry(None)
            return redirect("user_home_page")

        messages.error(request, "Invalid Credentials")
        return redirect("user_login page")
def user_home(request):
    email_id = request.session.get("session_key")
    if not email_id:
        messages.info(request, "Please login to open your home page")
        return redirect("user_login page")

    try:
        user_object = UserDetail.objects.get(email=email_id)
    except UserDetail.DoesNotExist:
        request.session.flush()
        messages.error(request, "Your session expired. Please login again.")
        return redirect("user_login page")

    site_rating = CreatorReview.objects.aggregate(value=Avg("rating"))["value"] or 0
    context = {
        "user_key": user_object,
        "site_recipe_count": RecipeVideo.objects.filter(status="Published").count(),
        "site_average_rating": round(float(site_rating), 1),
        "site_review_count": CreatorReview.objects.count(),
        "site_visitor_count": CreatorDetail.objects.aggregate(total=Sum("profile_views"))["total"] or 0,
    }
    return render(request, "user/user_home.html", context)

def edit_profile_action(request):
    if request.method != "POST":
        return redirect("user_home_page")

    current_email = request.session.get("session_key")
    if not current_email:
        return redirect("user_login page")

    user_object = UserDetail.objects.get(email=current_email)
    user_object.name = request.POST.get("name", user_object.name).strip()
    user_object.phone = request.POST.get("phone", user_object.phone).strip()
    new_email = request.POST.get("email", user_object.email).strip()

    if new_email and new_email != user_object.email:
        if UserDetail.objects.filter(email__iexact=new_email).exclude(email=user_object.email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("user_home_page")
        user_object.email = new_email
        request.session["session_key"] = new_email

    user_object.save()
    messages.success(request, "Profile updated successfully")
    return redirect("user_home_page")

def change_password(request):
    if request.method != "POST":
        return redirect("user_home_page")

    current_email = request.session.get("session_key")
    role = request.session.get("role")
    if not current_email or role not in {"user", "creator"}:
        return redirect("user_login page" if role != "creator" else "creator_login page")

    model = UserDetail if role == "user" else CreatorDetail
    login_url = "user_login page" if role == "user" else "creator_login page"
    home_url = "user_home_page" if role == "user" else "creator_home_page"
    account = model.objects.filter(email=current_email).first()
    if not account:
        return redirect(login_url)

    old_password = request.POST.get("old_password", "")
    new_password = request.POST.get("new_password", "")
    confirm_password = request.POST.get("confirm_password", "")
    if account.password != old_password:
        messages.error(request, "Your current password is incorrect.")
    elif len(new_password) < 6:
        messages.error(request, "New password must be at least 6 characters.")
    elif new_password != confirm_password:
        messages.error(request, "New password and confirmation do not match.")
    elif new_password == old_password:
        messages.error(request, "New password must be different from the current password.")
    else:
        account.password = new_password
        account.save(update_fields=["password"])
        messages.success(request, "Password changed successfully.")
    return redirect(home_url)

def user_feedback(request):
    email_id=request.session.get("session_key")
    if not email_id:
        messages.info(request, "Please login to submit feedback")
        return redirect("user_login page")

    if request.method=="GET":
        user_object=UserDetail.objects.get(email=email_id)
        context={
            "user_key":user_object,
            "logged_user_name":user_object.name,
            "logged_user_email":user_object.email,
        }
    
        return render(request,"user/user_feedback.html",context)
    if request.method=="POST":
        user_object=UserDetail.objects.get(email=email_id)
        nm=user_object.name
        em=user_object.email
        rw=request.POST["review"]
        rate=request.POST.get("rating") or request.POST.get("form-select")
        ##creating object of Feedback Model class
        f=Feedback(name=nm,email=em,review=rw,rating=rate)
        f.save()## it write insert data into feedback table
        messages.success(request,"Thank you for Feedback")
        return redirect("user_feedback page") #logical name of url
def creator_registration(request):
        if request.method=="GET":
              return render(request,"creator/creator_registration.html")
        if request.method=="POST":
            nm=request.POST["name"]
            em=request.POST.get("email", "").strip().lower()
            ps=request.POST["password"]
            ph=request.POST["phone"]
            ct=request.POST["city"]
            about_me=request.POST["about_me"]
            pic=request.FILES.get("profile_pic")
            print(pic,"erdxgfgvjhjlnk")
            if CreatorDetail.objects.filter(email__iexact=em).exists():
                messages.error(request, "An account with this email already exists.")
                return redirect("creator_registration page")
            c=CreatorDetail(name=nm,email=em,password=ps,phone=ph, city=ct,about_me=about_me,profile_pic=pic)
            c.save()
            return redirect("creator_registration page")
##user_logout
def user_logout(request):
    request.session.pop("session_key", None)
    request.session.pop("role", None)
    messages.info(request,"Successfully Logged out")
    return redirect("user_login page")
##creator view
def creator_login(request):
    if request.method == "GET":
        if request.session.get("role") == "creator" and _session_creator(request):
            return redirect("creator_home_page")
        return render(request, "creator/creator_login.html")

    if request.method == "POST":
        em = (request.POST.get("email") or "").strip().lower()
        ps = (request.POST.get("password") or "").strip()

        if not em or not ps:
            messages.error(request, "Email and password are required.")
            return redirect("creator_login page")

        creator_list = CreatorDetail.objects.filter(email__iexact=em, password=ps)
        if creator_list.exists():
            request.session["session_key"] = em
            request.session["role"] = "creator"
            request.session.set_expiry(None)
            return redirect("creator_home_page")

        messages.error(request, "Invalid Credentials")
        return redirect("creator_login page")
def creator_home(request):
    email_id = request.session.get("session_key")
    if not email_id:
        messages.info(request, "Please login to open your creator home page")
        return redirect("creator_login page")

    try:
        creator_object = CreatorDetail.objects.get(email=email_id)
    except CreatorDetail.DoesNotExist:
        request.session.flush()
        messages.error(request, "Your session expired. Please login again.")
        return redirect("creator_login page")

    context = {
        "creator_key": creator_object,
        "recipe_count": RecipeVideo.objects.filter(creator=creator_object, status="Published").count(),
        "review_count": creator_object.portfolio_reviews.count(),
        "average_rating": creator_object.portfolio_reviews.aggregate(value=Avg("rating"))["value"] or 0,
        "visitor_count": creator_object.profile_views,
    }
    return render(request, "creator/creator_home.html", context)

def creator_edit_profile(request):
    if request.method != "POST":
        return redirect("creator_home_page")

    current_email = request.session.get("session_key")
    if not current_email:
        return redirect("creator_login page")

    creator_object = CreatorDetail.objects.get(email=current_email)
    creator_object.name = request.POST.get("name", creator_object.name).strip()
    creator_object.phone = request.POST.get("phone", creator_object.phone).strip()
    creator_object.city = request.POST.get("city", creator_object.city).strip()
    creator_object.about_me = request.POST.get("about_me", creator_object.about_me).strip()
    creator_object.save()
    messages.success(request, "Creator profile updated successfully")
    return redirect("creator_home_page")

def creator_logout(request):
    request.session.pop("session_key", None)
    request.session.pop("role", None)
    messages.info(request,"Successfully Logged out")
    return redirect("creator_login page")
def recipe_video(request):
    if request.method == "GET":
        return render(request, "creator/recipe_video.html")

    if request.method == "POST":
        email_id = request.session.get("session_key")
        if not email_id:
            messages.error(request, "Please login first")
            return redirect("creator_login page")

        creator_object = CreatorDetail.objects.get(email=email_id)
        ph = request.POST.get("phone")
        nm = request.POST.get("name")
        rc = request.POST.get("recipe_category")
        ig = request.POST.get("Ingredient")
        rv = request.FILES.get("recipe_video")
        dc = request.POST.get("Description")

        c = RecipeVideo(
            creator=creator_object,
            phone=ph,
            name=nm,
            recipe_category=rc,
            ingredients=ig,
            recipe_video=rv,
            description=dc,
            cooking_time=request.POST.get("cooking_time", 30),
            difficulty=request.POST.get("difficulty", "Medium"),
            food_type=request.POST.get("food_type", "Vegetarian"),
            status=request.POST.get("status", "Published"),
        )
        c.save()
        messages.success(request, "Video Uploaded")
        return redirect("my_video page")

    return redirect("creator_login page")
        #    and write this code in views.py file

def reviews(request):

    feedbacks = Feedback.objects.filter(
        rating__in=["⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    ).order_by("-date")[:5]

    review_data = []

    for feedback in feedbacks:

        user = UserDetail.objects.filter(
            email=feedback.email
        ).first()

        review_data.append({
            "name": feedback.name,
            "rating": feedback.rating,
            "review": feedback.review,
            "date": feedback.date,
          "user":user})

    return render(request, "html/reviews.html", {
        "review_data": review_data
    })
def product(request):
    if request.method == "GET":
          email_id=request.session.get("session_key")
          creator_object=CreatorDetail.objects.get(email=email_id) if email_id else None
          recipe_video_list=RecipeVideo.objects.all()[:4]
          context={
              "r_key":recipe_video_list,
              "product_key": Product.objects.filter(creator=creator_object).order_by("-date") if creator_object else [],
              "gift_boxes": GiftBox.objects.filter(creator=creator_object, is_active=True).prefetch_related("products") if creator_object else [],
          }

          return render(request,"creator/product.html",context)
    if request.method == "POST":
        email_id=request.session.get("session_key")
        creator_object=CreatorDetail.objects.filter(email=email_id, is_blocked=False).first()
        if not creator_object or request.session.get("role") != "creator":
            messages.error(request, "Please login as a creator before adding a product.")
            return redirect("creator_login page")

        if request.POST.get("action") == "create_gift_box":
            selected_products = Product.objects.filter(
                id__in=request.POST.getlist("products"),
                creator=creator_object,
            )
            name = request.POST.get("gift_box_name", "").strip()
            description = request.POST.get("gift_box_description", "").strip()
            try:
                gift_box_price = Decimal(request.POST.get("gift_box_price", ""))
            except (TypeError, ValueError, ArithmeticError):
                gift_box_price = Decimal("-1")
            if not name or not selected_products.exists() or gift_box_price < 0:
                messages.error(request, "Add a name, valid price, and at least one of your products.")
                return redirect("product_page")
            gift_box = GiftBox.objects.create(
                creator=creator_object,
                name=name,
                description=description,
                price=gift_box_price,
            )
            gift_box.products.set(selected_products)
            messages.success(request, "Gift box offer created successfully.")
            return redirect("product_page")

        ph=request.POST.get("phone", "").strip()
        nm=request.POST.get("product_name", "").strip()
        c=request.POST.get("product_category", "").strip()
        pr=request.POST.get("price", "").strip()
        qn=request.POST.get("quantity", "").strip()
        product_pic=request.FILES.get("product_pic")
        dc=request.POST.get("description", "").strip()
        if not all([ph, nm, c, pr, qn, dc, product_pic]):
            messages.error(request, "Please complete every product field and upload a product photo.")
            return redirect("product_page")
        try:
            price = Decimal(pr)
            best_before_days = max(int(request.POST.get("best_before_days") or 30), 1)
        except (TypeError, ValueError, ArithmeticError):
            messages.error(request, "Enter a valid price and best-before duration.")
            return redirect("product_page")
        if price < 0:
            messages.error(request, "Product price cannot be negative.")
            return redirect("product_page")
        p=Product(
            creator=creator_object,
            phone=ph,
            product_name=nm,
            category=c,
            price=price,
            quantity=qn,
            product_pic=product_pic,
            description=dc,
            prepared_on=request.POST.get("prepared_on") or None,
            best_before_days=best_before_days,
            batch_code=request.POST.get("batch_code", "").strip(),
            is_homemade=request.POST.get("is_homemade") == "on",
            creator_choice=request.POST.get("creator_choice") == "on",
        )
        p.save()
        messages.success(request, "Product added successfully")
        return redirect("home_page")


def request_gift_box(request, gift_box_id):
    user = _session_user(request)
    if not user:
        return redirect("user_login page")
    gift_box = get_object_or_404(
        GiftBox.objects.prefetch_related("products"),
        id=gift_box_id,
        is_active=True,
        creator__is_blocked=False,
    )
    if request.method == "POST":
        address = request.POST.get("delivery_address", "").strip()
        if not address:
            messages.error(request, "Please enter your delivery address.")
        else:
            product_names = ", ".join(gift_box.products.values_list("product_name", flat=True))
            Enquiry.objects.create(
                user=user,
                creator=gift_box.creator,
                message=f"Gift box request: {gift_box.name}. Products: {product_names}. Delivery address: {address}",
            )
            messages.success(request, "Gift box request sent to the creator.")
    return redirect("creator_portfolio", email=gift_box.creator.email)


def request_custom_gift_box(request, email):
    user = _session_user(request)
    if not user:
        return redirect("user_login page")
    creator = get_object_or_404(CreatorDetail, email=email, is_blocked=False)
    if request.method == "POST":
        selected_products = Product.objects.filter(creator=creator, id__in=request.POST.getlist("products"))
        address = request.POST.get("delivery_address", "").strip()
        box_name = request.POST.get("box_name", "Homemade Gift Box").strip() or "Homemade Gift Box"
        if not selected_products.exists() or not address:
            messages.error(request, "Select at least one product and enter your delivery address.")
        else:
            product_names = ", ".join(selected_products.values_list("product_name", flat=True))
            Enquiry.objects.create(
                user=user,
                creator=creator,
                message=f"Custom gift box request: {box_name}. Products: {product_names}. Delivery address: {address}",
            )
            messages.success(request, "Your custom gift box request was sent to the creator.")
    return redirect("creator_portfolio", email=creator.email)


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("creator"), id=product_id)
    return render(request, "html/product_detail.html", {"product": product, "cart_count": sum(request.session.get("cart", {}).values())})

def delete_product(request, product_id):
    if request.method != "POST":
        return redirect("product_page")

    email_id=request.session.get("session_key")
    if not email_id:
        return redirect("creator_login page")

    creator_object=CreatorDetail.objects.get(email=email_id)
    product_object=Product.objects.get(id=product_id, creator=creator_object)
    if product_object.product_pic:
        product_object.product_pic.delete(save=False)
    product_object.delete()
    messages.success(request, "Product deleted successfully")
    return redirect("product_page")
def search_video(request):
    email_id = request.session.get("session_key")
    if not email_id:
        messages.info(request, "Please login to search recipe videos")
        return redirect("user_login page")

    user_object = UserDetail.objects.get(email=email_id)
    recipe_video_list = RecipeVideo.objects.all().order_by("-date")
    selected_category = ""

    if request.method == "POST":
        selected_category = (request.POST.get("recipe_category") or "").strip()
        if selected_category:
            recipe_video_list = recipe_video_list.filter(recipe_category=selected_category)

    return render(request, "user/search_video.html", {
        "r_key": recipe_video_list,
        "selected_category": selected_category,
        "user_key": user_object,
    })

def my_video(request):
    email_id = request.session.get("session_key")
    if not email_id:
        return redirect("creator_login page")

    creator_object = CreatorDetail.objects.get(email=email_id)
    recipe_queryset = RecipeVideo.objects.filter(creator=creator_object).order_by("-date")

    if request.method == "POST":
        cat = request.POST.get("recipe_category")
        if cat:
            recipe_queryset = recipe_queryset.filter(recipe_category=cat)

    context = {"r_key": recipe_queryset}
    return render(request, "creator/my_video.html", context)


def my_recipe(request):
    email_id = request.session.get("session_key")
    if not email_id:
        return redirect("creator_login page")

    creator_object = CreatorDetail.objects.get(email=email_id)
    recipe_queryset = RecipeVideo.objects.filter(creator=creator_object).order_by("-date")

    if request.method == "POST":
        cat = request.POST.get("recipe_category")
        if cat:
            recipe_queryset = recipe_queryset.filter(recipe_category=cat)

    context = {"r_key": recipe_queryset}
    return render(request, "creator/my_recipe.html", context)


def creator_portfolio(request, email):
    creator = get_object_or_404(CreatorDetail, email=email, is_blocked=False)
    user = _session_user(request)
    if request.method == "POST":
        if not user:
            return redirect("user_login page")
        review_text = request.POST.get("review", "").strip()
        try:
            rating = int(request.POST.get("rating", 0))
        except (TypeError, ValueError):
            rating = 0
        if not review_text or rating not in range(1, 6):
            messages.error(request, "Please add a review and choose a rating from 1 to 5.")
        else:
            CreatorReview.objects.create(creator=creator, user=user, rating=rating, text=review_text)
            messages.success(request, "Your review was added.")
        return redirect("creator_portfolio", email=creator.email)
    CreatorDetail.objects.filter(pk=creator.pk).update(profile_views=F("profile_views") + 1)
    creator.profile_views += 1
    products = Product.objects.filter(creator=creator).order_by("-creator_choice", "-date")
    recipes = RecipeVideo.objects.filter(creator=creator, status="Published").order_by("-views", "-likes")
    gift_boxes = creator.gift_boxes.filter(is_active=True).prefetch_related("products")
    reviews = creator.portfolio_reviews.select_related("user")[:6]
    average_rating = creator.portfolio_reviews.aggregate(value=Avg("rating"))["value"] or 0
    return render(request, "creator/creator_portfolio.html", {
        "creator": creator,
        "products": products,
        "recipes": recipes,
        "gift_boxes": gift_boxes,
        "reviews": reviews,
        "average_rating": round(float(average_rating), 1),
        "recipe_count": recipes.count(),
        "review_count": creator.portfolio_reviews.count(),
        "visitor_count": creator.profile_views,
    })


def _session_user(request):
    email = request.session.get("session_key")
    return UserDetail.objects.filter(email=email).first() if email else None


def _session_creator(request):
    email = request.session.get("session_key")
    return CreatorDetail.objects.filter(email=email, is_blocked=False).first() if email else None


def send_enquiry(request, email):
    user = _session_user(request)
    if not user:
        return redirect("user_login page")
    creator = get_object_or_404(CreatorDetail, email=email, is_blocked=False)
    product = Product.objects.filter(id=request.POST.get("product_id"), creator=creator).first()
    if request.method == "POST" and request.POST.get("message", "").strip():
        Enquiry.objects.create(user=user, creator=creator, product=product, message=request.POST["message"].strip())
        messages.success(request, "Your enquiry was sent to the creator.")
    return redirect("creator_portfolio", email=creator.email)


def creator_enquiries(request):
    creator = _session_creator(request)
    if not creator:
        return redirect("creator_login page")
    if request.method == "POST":
        enquiry = get_object_or_404(Enquiry, id=request.POST.get("enquiry_id"), creator=creator)
        action = request.POST.get("action")
        enquiry.status = {"reply": "Replied", "resolve": "Resolved", "archive": "Archived"}.get(action, enquiry.status)
        if action == "reply":
            enquiry.reply = request.POST.get("reply", "").strip()
        enquiry.save()
        return redirect("creator_enquiries")
    return render(request, "creator/enquiry_inbox.html", {"creator": creator, "enquiries": Enquiry.objects.filter(creator=creator).select_related("user", "product")})


def request_order(request, product_id):
    user = _session_user(request)
    if not user:
        return redirect("user_login page")
    product = get_object_or_404(Product.objects.select_related("creator"), id=product_id)
    if request.method == "POST":
        delivery_address = request.POST.get("delivery_address", "").strip()
        if not delivery_address:
            messages.error(request, "Please enter your delivery address.")
            return redirect("creator_portfolio", email=product.creator.email)
        quantity = max(int(request.POST.get("quantity", 1)), 1)
        OrderRequest.objects.create(user=user, creator=product.creator, product=product, quantity=quantity, delivery_address=delivery_address, delivery_note=request.POST.get("delivery_note", "").strip())
        messages.success(request, "Order request sent. The creator will respond shortly.")
    return redirect("home_page")


def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("home_page")

    get_object_or_404(Product, id=product_id)
    cart = request.session.get("cart", {})
    key = str(product_id)
    try:
        quantity = max(int(request.POST.get("quantity", 1) or 1), 1)
    except (TypeError, ValueError):
        quantity = 1
    cart[key] = int(cart.get(key, 0)) + quantity
    request.session["cart"] = cart
    request.session.modified = True
    messages.success(request, "Product added to your cart.")
    return redirect(request.POST.get("next") or "home_page")


def cart(request):
    cart_data = request.session.get("cart", {})
    product_ids = [int(product_id) for product_id in cart_data if str(product_id).isdigit()]
    products = Product.objects.filter(id__in=product_ids).select_related("creator")
    items = []
    grand_total = Decimal("0")
    for product in products:
        try:
            quantity = max(int(cart_data.get(str(product.id), 1)), 1)
        except (TypeError, ValueError):
            quantity = 1
        line_total = product.price * quantity
        grand_total += line_total
        items.append({"product": product, "quantity": quantity, "line_total": line_total})

    if request.method == "POST":
        action = request.POST.get("action")
        product_id = request.POST.get("product_id")
        if action == "remove" and product_id:
            cart_data.pop(str(product_id), None)
        elif action == "update" and product_id:
            try:
                quantity = max(int(request.POST.get("quantity", 1) or 1), 1)
            except (TypeError, ValueError):
                quantity = 1
            cart_data[str(product_id)] = quantity
        elif action == "checkout":
            user = _session_user(request)
            if not user:
                messages.info(request, "Please login to place your order.")
                return redirect("user_login page")
            delivery_address = request.POST.get("delivery_address", "").strip()
            if not delivery_address:
                messages.error(request, "Please enter your delivery address.")
                return redirect("cart")
            delivery_note = request.POST.get("delivery_note", "").strip()
            payment_method = request.POST.get("payment_method", "COD")
            payment_screenshot = request.FILES.get("payment_screenshot")
            if payment_method not in {"COD", "UPI"}:
                messages.error(request, "Please select a valid payment method.")
                return redirect("cart")
            if payment_method == "UPI" and not payment_screenshot:
                messages.error(request, "Please upload your UPI payment screenshot for verification.")
                return redirect("cart")
            for item in items:
                OrderRequest.objects.create(
                    user=user,
                    creator=item["product"].creator,
                    product=item["product"],
                    quantity=item["quantity"],
                    delivery_address=delivery_address,
                    delivery_note=delivery_note,
                    payment_method=payment_method,
                    payment_screenshot=payment_screenshot if payment_method == "UPI" else None,
                )
            request.session["cart"] = {}
            messages.success(request, "Your order request has been sent to the creators.")
            return redirect("user_orders")
        request.session["cart"] = cart_data
        request.session.modified = True
        return redirect("cart")

    return render(request, "user/cart.html", {"items": items, "grand_total": grand_total, "cart_count": sum(cart_data.values())})


def creator_orders(request):
    creator = _session_creator(request)
    if not creator:
        return redirect("creator_login page")
    if request.method == "POST":
        order = get_object_or_404(OrderRequest, id=request.POST.get("order_id"), creator=creator)
        if request.POST.get("status") in dict(OrderRequest.STATUS_CHOICES):
            order.status = request.POST["status"]
            order.save(update_fields=["status", "updated_at"])
        return redirect("creator_orders")
    return render(request, "creator/order_requests.html", {"creator": creator, "orders": OrderRequest.objects.filter(creator=creator, admin_approved=True).select_related("user", "product")})


def user_orders(request):
    user = _session_user(request)
    if not user:
        return redirect("user_login page")
    return render(request, "user/my_orders.html", {"orders": OrderRequest.objects.filter(user=user).select_related("creator", "product")})


def track_order(request):
    user = _session_user(request)
    if not user:
        return redirect("user_login page")

    order_code = (request.GET.get("order_id") or "").strip()
    tracked_order = None
    tracking_error = ""
    if order_code:
        tracked_order = OrderRequest.objects.filter(
            user=user,
            order_code__iexact=order_code,
        ).select_related("creator", "product").first()
        if not tracked_order:
            tracking_error = "No order was found for that Order ID."

    return render(request, "user/my_orders.html", {
        "orders": OrderRequest.objects.filter(user=user).select_related("creator", "product"),
        "tracked_order": tracked_order,
        "searched_order_id": order_code,
        "tracking_error": tracking_error,
    })


def order_receipt(request, order_id):
    order = get_object_or_404(OrderRequest.objects.select_related("user", "creator", "product"), id=order_id)
    allowed = request.session.get("session_key") in {order.user.email, order.creator.email}
    if not allowed:
        return redirect("user_login page")
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="flavorcraft-order-{order.id}.pdf"'
    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setTitle("FlavorCraft Order Receipt")
    pdf.setFillColorRGB(0.09, 0.24, 0.23)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(60, 770, "FlavorCraft Order Receipt")
    pdf.setFillColorRGB(0.35, 0.42, 0.42)
    pdf.setFont("Helvetica", 11)
    rows = [("Order ID", order.order_code), ("Product", order.product.product_name), ("Creator", order.creator.name), ("Quantity", str(order.quantity)), ("Total", f"Rs. {order.total}"), ("Address", order.delivery_address), ("Payment", order.payment_method), ("Payment status", order.payment_status), ("Status", order.status), ("Date", order.created_at.strftime("%d %b %Y"))]
    y = 710
    for label, value in rows:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(70, y, f"{label}")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(190, y, str(value))
        y -= 34
    pdf.setFillColorRGB(0.18, 0.62, 0.47)
    pdf.drawString(70, y - 10, "Thank you for supporting local home chefs.")
    pdf.save()
    return response


def advanced_search(request):
    query = (request.GET.get("q") or "").strip()
    tab = request.GET.get("tab", "all")
    city = (request.GET.get("city") or "").strip()
    category = (request.GET.get("category") or "").strip()
    difficulty = (request.GET.get("difficulty") or "").strip()
    veg = request.GET.get("veg") == "1"
    min_price = request.GET.get("min_price") or ""
    max_price = request.GET.get("max_price") or ""
    creators = CreatorDetail.objects.filter(Q(name__icontains=query) | Q(city__icontains=query) | Q(speciality__icontains=query), is_blocked=False) if query else CreatorDetail.objects.filter(is_blocked=False)
    products = Product.objects.filter(Q(product_name__icontains=query) | Q(category__icontains=query) | Q(description__icontains=query)) if query else Product.objects.all()
    recipes = RecipeVideo.objects.filter(Q(name__icontains=query) | Q(recipe_category__icontains=query) | Q(description__icontains=query), status="Published") if query else RecipeVideo.objects.filter(status="Published")
    if city:
        creators = creators.filter(city__icontains=city)
        products = products.filter(creator__city__icontains=city)
        recipes = recipes.filter(creator__city__icontains=city)
    if category:
        products = products.filter(category__icontains=category)
        recipes = recipes.filter(recipe_category__icontains=category)
    if difficulty:
        recipes = recipes.filter(difficulty__iexact=difficulty)
    if veg:
        recipes = recipes.filter(food_type__icontains="vegetarian")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    return render(request, "user/advanced_search_results.html", {"query": query, "tab": tab, "city": city, "category": category, "difficulty": difficulty, "veg": veg, "min_price": min_price, "max_price": max_price, "creators": creators[:20], "products": products.select_related("creator")[:20], "recipes": recipes.select_related("creator")[:20]})


def budget_recipes(request):
    budget_text = (request.GET.get("budget") or "").strip()
    budget = None
    budget_error = ""
    if budget_text:
        try:
            budget = Decimal(budget_text)
            if budget < 0:
                raise ValueError
        except (TypeError, ValueError, ArithmeticError):
            budget_error = "Enter a valid positive budget."
            budget = None

    recipes = []
    for recipe in RecipeVideo.objects.filter(status="Published").select_related("creator"):
        recipe.estimated_cost = estimate_recipe_cost(recipe.ingredients)
        if budget is None or recipe.estimated_cost <= budget:
            recipes.append(recipe)
    recipes.sort(key=lambda recipe: recipe.estimated_cost)
    return render(request, "user/budget_recipes.html", {
        "recipes": recipes,
        "budget": budget_text,
        "budget_error": budget_error,
    })


def compare_recipes(request):
    ids = [value for value in request.GET.getlist("recipe") if value.isdigit()][:3]
    recipes = RecipeVideo.objects.filter(id__in=ids, status="Published")
    return render(request, "user/compare_recipes.html", {"recipes": recipes})


def recipe_calculator(request, recipe_id):
    recipe = get_object_or_404(RecipeVideo, id=recipe_id)
    servings = max(int(request.GET.get("serves", recipe.servings)), 1)
    ratio = servings / max(recipe.servings, 1)
    ingredients = []
    for line in recipe.ingredients.splitlines():
        def scale(match):
            return f"{float(match.group(0)) * ratio:g}"
        scaled = re.sub(r"\d+(?:\.\d+)?", scale, line)
        ingredients.append({"text": line, "scaled": scaled})
    if request.GET.get("format") == "json":
        return JsonResponse({"recipe": recipe.name, "serves": servings, "ingredients": ingredients})
    return render(request, "user/recipe_calculator.html", {"recipe": recipe, "servings": servings, "ingredients": ingredients})


def shopping_list(request):
    user = _session_user(request)
    if not user:
        return redirect("user_login page")
    if request.method == "POST":
        action = request.POST.get("action")
        item = ShoppingListItem.objects.filter(id=request.POST.get("item_id"), user=user).first()
        if action == "add" and request.POST.get("ingredient", "").strip():
            ShoppingListItem.objects.create(user=user, ingredient=request.POST["ingredient"].strip(), quantity=request.POST.get("quantity", "").strip())
        elif item and action == "toggle":
            item.is_purchased = not item.is_purchased
            item.save(update_fields=["is_purchased"])
        elif item and action == "delete":
            item.delete()
        elif action == "add_recipe":
            recipe = RecipeVideo.objects.filter(id=request.POST.get("recipe_id")).first()
            if recipe:
                for line in recipe.ingredients.splitlines():
                    parts = line.strip().split(" ", 1)
                    ShoppingListItem.objects.create(user=user, quantity=parts[0] if len(parts) == 2 else "", ingredient=parts[1] if len(parts) == 2 else parts[0], recipe=recipe)
        return redirect("shopping_list")
    return render(request, "user/shopping_list.html", {"items": ShoppingListItem.objects.filter(user=user)})
    
   