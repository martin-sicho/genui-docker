# Generated by Django 2.2.8 on 2020-05-03 18:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('qsar', '0001_initial'),
        ('modelling', '0001_initial'),
        ('compounds', '0002_auto_20200427_2039'),
        ('generators', '0002_auto_20200503_1825'),
    ]

    operations = [
        migrations.CreateModel(
            name='DrugExAgentTrainingStrategy',
            fields=[
                ('trainingstrategy_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.TrainingStrategy')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('modelling.trainingstrategy',),
        ),
        migrations.CreateModel(
            name='DrugExAgentValidationStrategy',
            fields=[
                ('validationstrategy_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.ValidationStrategy')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('modelling.validationstrategy',),
        ),
        migrations.CreateModel(
            name='DrugExNetTrainingStrategy',
            fields=[
                ('trainingstrategy_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.TrainingStrategy')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('modelling.trainingstrategy',),
        ),
        migrations.CreateModel(
            name='DrugExValidationStrategy',
            fields=[
                ('validationstrategy_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.ValidationStrategy')),
                ('validSetSize', models.IntegerField(default=512, null=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('modelling.validationstrategy',),
        ),
        migrations.CreateModel(
            name='ModelPerformanceDrugEx',
            fields=[
                ('modelperfomancenn_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.ModelPerfomanceNN')),
                ('isOnValidationSet', models.BooleanField(default=False)),
                ('note', models.CharField(blank=True, max_length=128)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('modelling.modelperfomancenn',),
        ),
        migrations.CreateModel(
            name='ModelPerformanceDrugExAgent',
            fields=[
                ('modelperformance_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.ModelPerformance')),
                ('epoch', models.IntegerField()),
                ('note', models.CharField(blank=True, max_length=128)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('modelling.modelperformance',),
        ),
        migrations.CreateModel(
            name='DrugExNet',
            fields=[
                ('model_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.Model')),
                ('molset', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='compounds.MolSet')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genuidrugex.DrugExNet')),
            ],
            options={
                'abstract': False,
            },
            bases=('modelling.model',),
        ),
        migrations.CreateModel(
            name='DrugExAgent',
            fields=[
                ('model_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modelling.Model')),
                ('environment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drugexEnviron', to='qsar.QSARModel')),
                ('exploitationNet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drugexExploit', to='genuidrugex.DrugExNet')),
                ('explorationNet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drugexExplore', to='genuidrugex.DrugExNet')),
            ],
            options={
                'abstract': False,
            },
            bases=('modelling.model',),
        ),
        migrations.CreateModel(
            name='DrugEx',
            fields=[
                ('generator_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='generators.Generator')),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generator', to='modelling.Model')),
            ],
            options={
                'abstract': False,
            },
            bases=('generators.generator',),
        ),
    ]