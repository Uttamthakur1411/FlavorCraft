from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("project_app", "0016_creatordetail_profile_views"),
    ]

    operations = [
        migrations.CreateModel(
            name="GiftBox",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("description", models.TextField(blank=True, default="")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("creator", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="gift_boxes", to="project_app.creatordetail")),
                ("products", models.ManyToManyField(related_name="gift_boxes", to="project_app.product")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
