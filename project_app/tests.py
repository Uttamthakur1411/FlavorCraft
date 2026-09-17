from decimal import Decimal

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import CreatorDetail, OrderRequest, Product, UserDetail


class UserProfileDisplayTests(TestCase):
    def test_logged_in_user_name_and_image_are_shown_in_header(self):
        user = UserDetail.objects.create(
            name="Ayesha Khan",
            email="ayesha@example.com",
            password="secret123",
            phone="9876543210",
            profile_pic=SimpleUploadedFile(
                "profile.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            ),
        )

        session = self.client.session
        session["session_key"] = user.email
        session["role"] = "user"
        session.save()

        response = self.client.get("/search_video/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ayesha Khan")
        self.assertContains(response, user.profile_pic.url)


class CartFlowTests(TestCase):
    def setUp(self):
        self.user = UserDetail.objects.create(
            name="Ayesha Khan",
            email="cart@example.com",
            password="secret123",
            phone="9876543210",
        )
        self.creator = CreatorDetail.objects.create(
            name="Divya's Kitchen",
            email="creator@example.com",
            password="secret123",
            phone="9876543211",
            city="Lucknow",
            about_me="Homemade food creator",
        )
        self.product = Product.objects.create(
            creator=self.creator,
            phone="9876543211",
            product_name="Mango Pickle",
            category="Pickles",
            price="240.00",
            quantity="1 kg",
            description="Fresh homemade pickle",
        )

    def test_cart_checkout_creates_order_request(self):
        add_response = self.client.post(
            f"/cart/add/{self.product.id}/",
            {"quantity": "2", "next": "/"},
        )
        self.assertEqual(add_response.status_code, 302)

        session = self.client.session
        session["session_key"] = self.user.email
        session["role"] = "user"
        session.save()

        checkout_response = self.client.post("/cart/", {"action": "checkout", "delivery_address": "12 Market Road, Lucknow"})
        self.assertRedirects(checkout_response, "/orders/")
        order = OrderRequest.objects.get()
        self.assertEqual(order.product, self.product)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.total, Decimal("480.00"))
        self.assertTrue(order.order_code.startswith("FC-"))
        self.assertEqual(order.payment_method, "COD")
        self.assertEqual(order.delivery_address, "12 Market Road, Lucknow")

    def test_upi_checkout_requires_and_stores_screenshot(self):
        session = self.client.session
        session["session_key"] = self.user.email
        session["role"] = "user"
        session.save()
        self.client.post(f"/cart/add/{self.product.id}/", {"quantity": "1"})

        missing_proof = self.client.post("/cart/", {"action": "checkout", "payment_method": "UPI"})
        self.assertRedirects(missing_proof, "/cart/")
        self.assertEqual(OrderRequest.objects.count(), 0)

        valid_proof = self.client.post(
            "/cart/",
            {
                "action": "checkout",
            "delivery_address": "12 Market Road, Lucknow",
                "payment_method": "UPI",
                "payment_screenshot": SimpleUploadedFile("upi.jpg", b"proof", content_type="image/jpeg"),
            },
        )
        self.assertRedirects(valid_proof, "/orders/")
        order = OrderRequest.objects.get()
        self.assertEqual(order.payment_method, "UPI")
        self.assertTrue(order.payment_screenshot.name.startswith("payment_screenshots/"))

    def test_order_id_search_shows_matching_status(self):
        order = OrderRequest.objects.create(
            user=self.user,
            creator=self.creator,
            product=self.product,
            quantity=1,
            status="Preparing",
        )
        session = self.client.session
        session["session_key"] = self.user.email
        session["role"] = "user"
        session.save()

        response = self.client.get("/orders/track/", {"order_id": order.order_code.lower()})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_code)
        self.assertContains(response, "Preparing")
        self.assertEqual(response.context["tracked_order"], order)

    def test_order_id_search_does_not_expose_another_users_order(self):
        other_user = UserDetail.objects.create(
            name="Other User",
            email="other@example.com",
            password="secret123",
            phone="9876543212",
        )
        order = OrderRequest.objects.create(
            user=other_user,
            creator=self.creator,
            product=self.product,
        )
        session = self.client.session
        session["session_key"] = self.user.email
        session["role"] = "user"
        session.save()

        response = self.client.get("/orders/track/", {"order_id": order.order_code})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["tracked_order"])
        self.assertContains(response, "No order was found for that Order ID.")

    def test_creator_profile_stats_are_live_and_visits_increment(self):
        response = self.client.get(f"/creator/{self.creator.email}/")
        self.assertEqual(response.status_code, 200)
        self.creator.refresh_from_db()
        self.assertEqual(self.creator.profile_views, 1)
        self.assertEqual(response.context["recipe_count"], 0)
        self.assertEqual(response.context["review_count"], 0)
        self.assertEqual(response.context["average_rating"], 0)
        self.assertEqual(response.context["visitor_count"], 1)

        self.client.get(f"/creator/{self.creator.email}/")
        self.creator.refresh_from_db()
        self.assertEqual(self.creator.profile_views, 2)

    def test_logged_in_user_can_add_creator_review(self):
        session = self.client.session
        session["session_key"] = self.user.email
        session["role"] = "user"
        session.save()

        response = self.client.post(
            f"/creator/{self.creator.email}/",
            {"rating": "5", "review": "Fresh and delicious."},
        )

        self.assertRedirects(response, f"/creator/{self.creator.email}/")
        review = self.creator.portfolio_reviews.get()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "Fresh and delicious.")

    def test_user_can_change_password_with_current_password(self):
        session = self.client.session
        session["session_key"] = self.user.email
        session["role"] = "user"
        session.save()

        response = self.client.post(
            "/change_password/",
            {"old_password": "secret123", "new_password": "newpass456", "confirm_password": "newpass456"},
        )

        self.assertRedirects(response, "/user_home/")
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, "newpass456")

    def test_password_change_rejects_wrong_current_password(self):
        session = self.client.session
        session["session_key"] = self.user.email
        session["role"] = "user"
        session.save()

        self.client.post(
            "/change_password/",
            {"old_password": "wrongpass", "new_password": "newpass456", "confirm_password": "newpass456"},
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.password, "secret123")

    def test_duplicate_user_email_is_rejected(self):
        response = self.client.post(
            "/user_registration/",
            {"name": "Duplicate", "email": self.user.email.upper(), "password": "secret456", "phone": "9876543215"},
        )

        self.assertRedirects(response, "/user_registration/")
        self.assertEqual(UserDetail.objects.filter(email__iexact=self.user.email).count(), 1)

    def test_creator_product_submit_requires_valid_data(self):
        session = self.client.session
        session["session_key"] = self.creator.email
        session["role"] = "creator"
        session.save()

        invalid_response = self.client.post("/product/", {"product_name": "Incomplete"})
        self.assertRedirects(invalid_response, "/product/")
        self.assertEqual(Product.objects.count(), 1)

        valid_response = self.client.post(
            "/product/",
            {
                "phone": "9876543211",
                "product_name": "Fresh Pickle",
                "product_category": "Pickles",
                "price": "180.00",
                "quantity": "500g",
                "description": "A fresh batch",
                "best_before_days": "30",
                "is_homemade": "on",
                "product_pic": SimpleUploadedFile("pickle.jpg", b"image", content_type="image/jpeg"),
            },
            format="multipart",
        )
        self.assertRedirects(valid_response, "/")
        self.assertEqual(Product.objects.filter(product_name="Fresh Pickle").count(), 1)
