from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_pressure'),
    ]

    operations = [
        migrations.AddField(
            model_name='pressure',
            name='wind_direction',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
