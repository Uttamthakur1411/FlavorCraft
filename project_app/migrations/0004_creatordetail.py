

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_app', '0003_userdetail'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreatorDetail',
            fields=[
                ('name', models.CharField(max_length=45)),
                ('email', models.EmailField(max_length=55, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=55)),
                ('phone', models.CharField(max_length=13)),
                ('city', models.CharField(max_length=60)),
                ('about_me', models.TextField()),
                ('profile_pic', models.ImageField(default='', upload_to='creatorpic')),
            ],
        ),
    ]
