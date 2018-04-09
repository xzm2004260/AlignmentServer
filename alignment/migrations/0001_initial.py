# Generated by Django 2.0.3 on 2018-04-09 18:07

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('composition', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accompaniment', models.IntegerField(choices=[(1, 'ACAPELLA'), (2, 'MULTIINTRUSMENTAL')], verbose_name='accompaniment')),
                ('level', models.IntegerField(blank=True, choices=[(1, 'WORDS'), (2, 'LINES')], default=1, null=True, verbose_name='level')),
                ('status', models.IntegerField(blank=True, choices=[(1, 'NOTSTARTED'), (2, 'ONQUEUE'), (3, 'DONE')], default=1, null=True, verbose_name='status')),
                ('timestamps', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20, null=True), size=2), size=None)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Designates when the alignment is created.', verbose_name='created at')),
                ('composition', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='compose', to='composition.Composition')),
            ],
            options={
                'verbose_name': 'alignment',
                'verbose_name_plural': 'alignments',
                'db_table': 'alignment',
            },
        ),
    ]
