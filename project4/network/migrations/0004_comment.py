# Generated by Django 5.0 on 2024-02-12 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("network", "0003_delete_follow_profile_followers_profile_following"),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
    ]
