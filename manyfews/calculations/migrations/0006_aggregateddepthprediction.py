# Generated by Django 4.0.2 on 2022-03-11 12:44

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.polygon
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculations", "0005_riverflowcalculationoutput_riverflowprediction"),
    ]

    operations = [
        migrations.CreateModel(
            name="AggregatedDepthPrediction",
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
                ("prediction_date", models.DateTimeField()),
                (
                    "bounding_box",
                    django.contrib.gis.db.models.fields.PolygonField(
                        default=django.contrib.gis.geos.polygon.Polygon(
                            ((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))
                        ),
                        srid=4326,
                    ),
                ),
                ("median_depth", models.FloatField()),
                ("centile_25", models.FloatField()),
                ("centile_75", models.FloatField()),
            ],
        ),
    ]
