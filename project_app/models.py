import uuid

from django.db import models
from django.utils import timezone


def generate_order_code():
    return f"FC-{uuid.uuid4().hex[:10].upper()}"

class Contact(models.Model):
    name=models.CharField(max_length=45)
    email=models.EmailField(max_length=45)
    phone=models.CharField(max_length=13)
    question=models.TextField()
    date=models.DateField(default=timezone.now)

class  Feedback(models.Model):
    name=models.EmailField(max_length=45)
    email=models.CharField(max_length=45)
    review=models.TextField()
    rating=models.CharField(max_length=5)
    date=models.DateField(default=timezone.now)

class UserDetail(models.Model):
    name=models.CharField(max_length=45)
    email=models.EmailField(max_length=45,primary_key=True)
    password=models.CharField(max_length=45)
    phone=models.CharField(max_length=13)
    profile_pic=models.ImageField(default="",upload_to="user_pic")
    date=models.DateField(default=timezone.now)
class CreatorDetail(models.Model):
    name=models.CharField(max_length=45)
    email=models.EmailField(max_length=55,primary_key=True)
    password=models.CharField(max_length=55)
    phone=models.CharField(max_length=13)
    city=models.CharField(max_length=60)
    about_me=models.TextField()
    profile_pic=models.ImageField(default="",upload_to="creatorpic")
    speciality=models.CharField(max_length=120, blank=True, default="")
    is_verified=models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)
    delivery_radius_km = models.PositiveIntegerField(default=10)
    response_time_minutes = models.PositiveIntegerField(default=60)
    profile_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class HomepagePick(models.Model):
    title = models.CharField(max_length=150)
    creator = models.CharField(max_length=120)
    city = models.CharField(max_length=60)
    tag = models.CharField(max_length=60, default="Available Today")
    image = models.ImageField(upload_to="homepage_picks/", blank=True, null=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

class RecipeVideo(models.Model):

    creator=models.ForeignKey(CreatorDetail,on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    name = models.CharField(max_length=150)

    recipe_category = models.CharField(
        max_length=100

    )

    ingredients = models.TextField()

    recipe_video = models.FileField(
        upload_to='recipe_videos/'

    )
    thumbnail = models.ImageField(upload_to="recipe_thumbnails/", blank=True, null=True)

    description = models.TextField()
    cooking_time = models.PositiveIntegerField(default=30)
    difficulty = models.CharField(max_length=30, default='Medium')
    food_type = models.CharField(max_length=20, default='Vegetarian')
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default='Published')
    servings = models.PositiveIntegerField(default=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
class Product(models.Model):

    
    creator=models.ForeignKey(CreatorDetail,on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    product_name = models.CharField(max_length=150)

    category = models.CharField(
        max_length=100,
       
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.CharField(max_length=20)

    product_pic = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )

    description = models.TextField()
    prepared_on = models.DateField(null=True, blank=True)
    best_before_days = models.PositiveIntegerField(default=30)
    batch_code = models.CharField(max_length=30, blank=True, default="")
    is_homemade = models.BooleanField(default=True)
    creator_choice = models.BooleanField(default=False)

    

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product_name   


class Enquiry(models.Model):
    STATUS_CHOICES = [("New", "New"), ("Replied", "Replied"), ("Resolved", "Resolved"), ("Archived", "Archived")]

    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="enquiries_sent")
    creator = models.ForeignKey(CreatorDetail, on_delete=models.CASCADE, related_name="enquiries_received")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="enquiries")
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="New")
    reply = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class GiftBox(models.Model):
    creator = models.ForeignKey(CreatorDetail, on_delete=models.CASCADE, related_name="gift_boxes")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product, related_name="gift_boxes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class OrderRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"), ("Accepted", "Accepted"), ("Rejected", "Rejected"),
        ("Preparing", "Preparing"), ("Ready", "Ready"), ("Completed", "Completed"),
    ]

    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="order_requests")
    creator = models.ForeignKey(CreatorDetail, on_delete=models.CASCADE, related_name="order_requests_received")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_requests")
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_address = models.TextField(blank=True, default="")
    delivery_note = models.CharField(max_length=250, blank=True, default="")
    PAYMENT_CHOICES = [("COD", "Cash on Delivery"), ("UPI", "UPI")]
    PAYMENT_STATUS_CHOICES = [("Submitted", "Submitted"), ("Verified", "Verified"), ("Rejected", "Rejected")]
    order_code = models.CharField(max_length=18, unique=True, default=generate_order_code, editable=False)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="COD")
    payment_status = models.CharField(max_length=12, choices=PAYMENT_STATUS_CHOICES, default="Submitted")
    payment_screenshot = models.ImageField(upload_to="payment_screenshots/", null=True, blank=True)
    admin_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = generate_order_code()
        while OrderRequest.objects.filter(order_code=self.order_code).exclude(pk=self.pk).exists():
            self.order_code = generate_order_code()
        self.total = self.product.price * self.quantity
        super().save(*args, **kwargs)


class CreatorReview(models.Model):
    creator = models.ForeignKey(CreatorDetail, on_delete=models.CASCADE, related_name="portfolio_reviews")
    user = models.ForeignKey(UserDetail, on_delete=models.SET_NULL, null=True, blank=True, related_name="creator_reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ShoppingListItem(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="shopping_items")
    ingredient = models.CharField(max_length=150)
    quantity = models.CharField(max_length=80, blank=True, default="")
    recipe = models.ForeignKey(RecipeVideo, on_delete=models.SET_NULL, null=True, blank=True, related_name="shopping_items")
    is_purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_purchased", "ingredient"]
    






