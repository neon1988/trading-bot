# Generated by Django 4.0.3 on 2022-03-23 10:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('trading', '0005_alter_candlestick_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='candlestick',
            unique_together={('pair', 'interval', 'datetime')},
        ),
    ]
