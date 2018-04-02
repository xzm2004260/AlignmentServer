# Generated by Django 2.0.3 on 2018-04-02 17:07

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
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Designates when the alignment is created.', verbose_name='created at')),
                ('compositions', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compose', to='composition.Composition', unique=True)),
            ],
            options={
                'verbose_name': 'alignment',
                'verbose_name_plural': 'alignments',
                'db_table': 'alignment',
            },
        ),
    ]
