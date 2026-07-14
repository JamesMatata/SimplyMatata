from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0010_add_advertising_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='homepage_slot',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(1, 'Homepage slot 1'), (2, 'Homepage slot 2'), (3, 'Homepage slot 3')],
                help_text='Pin this project to a homepage slot. Each slot can only hold one project.',
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(
                condition=models.Q(('homepage_slot__isnull', False)),
                fields=('homepage_slot',),
                name='unique_homepage_slot',
            ),
        ),
    ]
