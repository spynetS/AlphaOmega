# Generated by Django 5.1.2 on 2024-10-18 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_alter_account_watch_later_delete_playlist'),
        ('playlist', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlists', to='account.account'),
        ),
    ]
