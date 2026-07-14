from django.db import migrations, models

import works.validators


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0011_project_homepage_slot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='featured_image',
            field=models.ImageField(
                blank=True,
                help_text='Optional detail-page cover. Use 16:9 (1920×1080) for film and advertising; 4:5 for comics.',
                upload_to='projects/featured/',
                validators=[works.validators.validate_image_upload],
            ),
        ),
        migrations.AlterField(
            model_name='project',
            name='thumbnail',
            field=models.ImageField(
                blank=True,
                help_text='Optional 4:5 card cover (1080×1350). Used on works cards and homepage.',
                upload_to='projects/thumbnails/',
                validators=[works.validators.validate_image_upload],
            ),
        ),
        migrations.AlterField(
            model_name='seriesepisode',
            name='featured_image',
            field=models.ImageField(
                blank=True,
                help_text='Optional detail cover. Use 16:9 for film/ad episodes; 4:5 for comics.',
                upload_to='projects/episodes/featured/',
                validators=[works.validators.validate_image_upload],
            ),
        ),
    ]
