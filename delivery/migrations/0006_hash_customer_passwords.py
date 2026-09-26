from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0005_cart_quantities_and_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='password',
            field=models.CharField(max_length=128),
        ),
    ]