# Generated by Django 4.2.8 on 2024-07-18 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0060_alter_issue_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='value',
            name='value_type',
            field=models.CharField(choices=[('text', 'Text'), ('url', 'URL'), ('integer', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean'), ('date', 'Date'), ('datetime', 'Datetime'), ('email', 'E-mail'), ('phone', 'Phone'), ('option', 'Option'), ('file', 'File')], default='text', help_text='Type of this value.', max_length=8, verbose_name='Value type'),
        ),
    ]
