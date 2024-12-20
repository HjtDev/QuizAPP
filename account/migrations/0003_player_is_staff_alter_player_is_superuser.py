# Generated by Django 5.1.4 on 2024-12-07 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_player_created_at_player_is_active_player_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='is_staff',
            field=models.BooleanField(default=False, verbose_name='Staff Status'),
        ),
        migrations.AlterField(
            model_name='player',
            name='is_superuser',
            field=models.BooleanField(default=False, verbose_name='Superuser Status'),
        ),
    ]
