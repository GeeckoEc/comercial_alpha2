# Generated by Django 5.1 on 2024-09-05 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0021_kardex_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kardex',
            name='fecha',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
