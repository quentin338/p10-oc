# Generated by Django 2.2.5 on 2019-09-19 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('code', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('image_url', models.CharField(max_length=200)),
                ('nutriscore', models.SmallIntegerField()),
                ('ingredients_image', models.CharField(max_length=200)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.Category')),
            ],
        ),
    ]
