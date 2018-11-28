# Generated by Django 2.1.1 on 2018-10-31 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dining', '0004_restaurant_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foodImage', models.ImageField(upload_to='')),
            ],
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='photo',
        ),
        migrations.AddField(
            model_name='foodimage',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dining.Restaurant'),
        ),
    ]