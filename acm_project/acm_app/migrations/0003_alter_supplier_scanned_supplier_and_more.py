# Generated by Django 4.1.7 on 2023-03-06 13:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('acm_app', '0002_rename_logo_path_scannedsupplier_logo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='scanned_supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='acm_app.scannedsupplier'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='status',
            field=models.CharField(choices=[('GRANTED', 'GRANTED'), ('REVOKED', 'REVOKED'), ('NAME_CHANGE', 'NAME_CHANGE'), ('UNKNOWN', 'UNKNOWN')], max_length=11),
        ),
    ]
