# Generated by Django 2.2.8 on 2020-01-30 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelling', '0003_auto_20200127_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='modelFile',
            field=models.FileField(blank=True, null=True, upload_to='models/'),
        ),
    ]
