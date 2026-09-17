from django.db import migrations, models


def create_default_picks(apps, schema_editor):
    HomepagePick = apps.get_model("project_app", "HomepagePick")
    HomepagePick.objects.bulk_create([
        HomepagePick(title="Homemade Mango Pickle", creator="Divya's Kitchen", city="Lucknow", tag="Available Today", sort_order=1),
        HomepagePick(title="Mathri", creator="Asha's Homemade", city="Delhi", tag="Freshly Baked", sort_order=2),
        HomepagePick(title="Besan Ladoo", creator="Shivani Sweets", city="Mumbai", tag="Made This Morning", sort_order=3),
        HomepagePick(title="Homemade Masala", creator="Naina's Pantry", city="Vanaras", tag="Chef's Choice", sort_order=4),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ("project_app", "0009_remove_enquiry_creator_remove_enquiry_product_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipevideo",
            name="thumbnail",
            field=models.ImageField(blank=True, null=True, upload_to="recipe_thumbnails/"),
        ),
        migrations.CreateModel(
            name="HomepagePick",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("creator", models.CharField(max_length=120)),
                ("city", models.CharField(max_length=60)),
                ("tag", models.CharField(default="Available Today", max_length=60)),
                ("image", models.ImageField(blank=True, null=True, upload_to="homepage_picks/")),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order", "title"]},
        ),
        migrations.RunPython(create_default_picks, migrations.RunPython.noop),
    ]