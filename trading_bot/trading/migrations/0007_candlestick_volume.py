# Generated by Django 4.0.3 on 2022-03-23 13:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('trading', '0006_alter_candlestick_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='candlestick',
            name='volume',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
