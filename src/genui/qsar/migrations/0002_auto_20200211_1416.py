# Generated by Django 2.2.8 on 2020-02-11 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qsar', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qsarmodel',
            name='molset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='models', to='compounds.MolSet'),
        ),
    ]