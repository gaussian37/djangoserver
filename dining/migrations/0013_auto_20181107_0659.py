# Generated by Django 2.1.1 on 2018-11-06 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dining', '0012_auto_20181107_0656'),
    ]

    operations = [
        migrations.RenameField(
            model_name='restaurant',
            old_name='representative_image',
            new_name='representativeImage',
        ),
    ]