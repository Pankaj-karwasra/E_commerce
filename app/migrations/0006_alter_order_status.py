# Generated by Django 5.1.2 on 2024-11-11 06:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0005_checkout_order_orderitem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Shipped", "Shipped"),
                    ("Delivered", "Delivered"),
                    ("Cancelled", "Cancelled"),
                ],
                default="Pending",
                max_length=20,
            ),
        ),
    ]
