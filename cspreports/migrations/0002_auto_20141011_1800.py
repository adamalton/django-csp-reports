from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cspreports', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cspreport',
            options={'ordering': ('-created',)},
        ),
    ]
