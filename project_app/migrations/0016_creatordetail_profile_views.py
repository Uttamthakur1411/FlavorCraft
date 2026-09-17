from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("project_app", "0015_orderrequest_delivery_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="creatordetail",
            name="profile_views",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
