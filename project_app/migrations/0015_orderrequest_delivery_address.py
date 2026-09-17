from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("project_app", "0014_remove_orderrequest_project_app_order_code_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderrequest",
            name="delivery_address",
            field=models.TextField(blank=True, default=""),
        ),
    ]
