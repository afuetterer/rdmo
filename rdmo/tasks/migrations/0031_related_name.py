# Generated by Django 2.2.13 on 2020-08-24 11:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0030_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='conditions',
            field=models.ManyToManyField(blank=True, help_text='The list of conditions evaluated for this task.', related_name='tasks', to='conditions.Condition', verbose_name='Conditions'),
        ),
        migrations.AlterField(
            model_name='task',
            name='end_attribute',
            field=models.ForeignKey(blank=True, help_text='The attribute that is setting the end date for this task (optional, if no end date attribute is given, the start date attribute sets also the end date).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_as_end', to='domain.Attribute', verbose_name='End date attribute'),
        ),
        migrations.AlterField(
            model_name='task',
            name='start_attribute',
            field=models.ForeignKey(blank=True, help_text='The attribute that is setting the start date for this task.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_as_start', to='domain.Attribute', verbose_name='Start date attribute'),
        ),
    ]