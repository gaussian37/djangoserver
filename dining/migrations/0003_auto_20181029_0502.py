# Generated by Django 2.1.1 on 2018-10-28 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dining', '0002_auto_20181029_0457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='operatingHours',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]