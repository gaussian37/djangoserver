# Generated by Django 2.1.1 on 2018-10-31 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dining', '0003_auto_20181029_0502'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='photo',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]