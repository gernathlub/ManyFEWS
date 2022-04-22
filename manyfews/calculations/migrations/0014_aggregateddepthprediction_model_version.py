# Generated by Django 4.0.3 on 2022-04-01 11:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("calculations", "0013_modelversion_floodmodelparameters"),
    ]

    operations = [
        migrations.AddField(
            model_name="aggregateddepthprediction",
            name="model_version",
            field=models.ForeignKey(
                default=36,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculations.modelversion",
            ),
            preserve_default=False,
        ),
    ]