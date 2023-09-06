# Generated by Django 4.2.5 on 2023-09-06 04:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('questions', '0090_add_editors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='editors',
            field=models.ManyToManyField(
                blank=True,
                help_text='The sites that can edit this catalog (in a multi site setup).',
                related_name='%(class)s_editors',
                to='sites.site',
                verbose_name='Editors',
            ),
        ),
        migrations.AlterField(
            model_name='page',
            name='editors',
            field=models.ManyToManyField(
                blank=True,
                help_text='The sites that can edit this page (in a multi site setup).',
                related_name='%(class)s_editors',
                to='sites.site',
                verbose_name='Editors',
            ),
        ),
        migrations.AlterField(
            model_name='question',
            name='editors',
            field=models.ManyToManyField(
                blank=True,
                help_text='The sites that can edit this question (in a multi site setup).',
                related_name='%(class)s_editors',
                to='sites.site',
                verbose_name='Editors',
            ),
        ),
        migrations.AlterField(
            model_name='questionset',
            name='editors',
            field=models.ManyToManyField(
                blank=True,
                help_text='The sites that can edit this questionset (in a multi site setup).',
                related_name='%(class)s_editors',
                to='sites.site',
                verbose_name='Editors',
            ),
        ),
        migrations.AlterField(
            model_name='section',
            name='editors',
            field=models.ManyToManyField(
                blank=True,
                help_text='The sites that can edit this section (in a multi site setup).',
                related_name='%(class)s_editors',
                to='sites.site',
                verbose_name='Editors',
            ),
        ),
    ]
