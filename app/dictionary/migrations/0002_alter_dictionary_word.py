# Generated by Django 4.0 on 2023-02-27 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dictionary',
            name='word',
            field=models.ManyToManyField(to='dictionary.Word'),
        ),
    ]
