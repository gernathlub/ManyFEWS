# Generated by Django 4.0.2 on 2022-03-17 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("calculations", "0008_aggregateddepthprediction"),
    ]

    operations = [
        migrations.RenameField(
            model_name="aggregateddepthprediction",
            old_name="centile_25",
            new_name="lower_centile",
        ),
        migrations.RenameField(
            model_name="aggregateddepthprediction",
            old_name="centile_75",
            new_name="upper_centile",
        ),
    ]
