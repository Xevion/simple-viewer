# Generated by Django 3.1.2 on 2020-11-01 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0002_auto_20201031_0526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serveddirectory',
            name='regex_pattern',
            field=models.CharField(default='', max_length=100, verbose_name='RegEx Matching Pattern'),
        ),
    ]
