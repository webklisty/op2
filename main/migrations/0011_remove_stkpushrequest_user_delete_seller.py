# Generated by Django 4.2.5 on 2023-10-11 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_remove_stkpushrequest_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stkpushrequest',
            name='user',
        ),
        migrations.DeleteModel(
            name='Seller',
        ),
    ]
