# Generated by Django 4.0.4 on 2022-05-16 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0007_candlestick_volume'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pair', models.CharField(max_length=20)),
                ('datetime', models.DateTimeField(verbose_name='datetime')),
                ('asks', models.FloatField()),
                ('bids', models.FloatField()),
            ],
            options={
                'unique_together': {('pair', 'datetime')},
            },
        ),
    ]