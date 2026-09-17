from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project_app", "0010_homepagepick_recipevideo_thumbnail"),
    ]

    operations = [
        migrations.AddField(
            model_name="creatordetail",
            name="speciality",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="creatordetail",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="creatordetail",
            name="is_blocked",
            field=models.BooleanField(default=False),
        ),
    ]