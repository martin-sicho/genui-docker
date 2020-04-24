# Generated by Django 2.2.8 on 2020-02-27 12:38

import commons.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modelling', '0003_auto_20200213_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelparameter',
            name='defaultValue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='modelling.ModelParameterValue'),
        ),
        migrations.AlterField(
            model_name='modelparametervalue',
            name='strategy',
            field=models.ForeignKey(null=True, on_delete=commons.models.NON_POLYMORPHIC_CASCADE, related_name='parameters', to='modelling.TrainingStrategy'),
        ),
    ]