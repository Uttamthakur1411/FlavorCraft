

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.EmailField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('review', models.TextField()),
                ('rating', models.CharField(max_length=5)),
                ('date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
    ]
