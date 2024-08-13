# Generated by Django 5.1 on 2024-08-12 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Adquiscion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("factura", models.CharField(max_length=50)),
                ("fecha", models.DateField()),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name="Cliente",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("apellido", models.CharField(max_length=100)),
                (
                    "tipo_identificacion",
                    models.CharField(
                        choices=[("cedula", "Cédula"), ("ruc", "RUC")], max_length=20
                    ),
                ),
                ("identificacion", models.CharField(max_length=20)),
                ("direccion", models.CharField(max_length=200)),
                ("ciudad", models.CharField(max_length=100)),
                ("telefono", models.CharField(max_length=20)),
                ("celular", models.CharField(max_length=20)),
                ("correo", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="Producto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("descripcion", models.TextField()),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                ("cantidad", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Proveedor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("identificacion", models.CharField(max_length=20)),
                ("descripcion", models.TextField()),
                ("direccion", models.CharField(max_length=200)),
                ("ciudad", models.CharField(max_length=100)),
                ("telefono", models.CharField(max_length=20)),
                ("celular", models.CharField(max_length=20)),
                ("correo", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="Kardex",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha", models.DateField()),
                ("cantidad", models.IntegerField()),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="comercial.producto",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Item_Adquiscion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cantidad", models.IntegerField()),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "adquiscion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="comercial.adquiscion",
                    ),
                ),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="comercial.producto",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="adquiscion",
            name="proveedor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="comercial.proveedor"
            ),
        ),
        migrations.CreateModel(
            name="Venta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha", models.DateField()),
                ("factura", models.CharField(max_length=50)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="comercial.cliente",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Item_Venta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cantidad", models.IntegerField()),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="comercial.producto",
                    ),
                ),
                (
                    "venta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="comercial.venta",
                    ),
                ),
            ],
        ),
    ]
