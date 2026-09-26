from django.db import migrations, models
import django.db.models.deletion


def copy_existing_cart_items(apps, schema_editor):
    database = schema_editor.connection.alias
    Cart = apps.get_model('delivery', 'Cart')
    CartItem = apps.get_model('delivery', 'CartItem')
    through_model = Cart._meta.get_field('items').remote_field.through
    existing_items = through_model.objects.using(database).all().values_list('cart_id', 'item_id')
    CartItem.objects.using(database).bulk_create([
        CartItem(cart_id=cart_id, item_id=item_id, quantity=1)
        for cart_id, item_id in existing_items
    ])


def restore_cart_items(apps, schema_editor):
    database = schema_editor.connection.alias
    Cart = apps.get_model('delivery', 'Cart')
    CartItem = apps.get_model('delivery', 'CartItem')
    through_model = Cart._meta.get_field('items').remote_field.through
    cart_items = CartItem.objects.using(database).all().values_list('cart_id', 'item_id')
    through_model.objects.using(database).bulk_create([
        through_model(cart_id=cart_id, item_id=item_id)
        for cart_id, item_id in cart_items
    ], ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0004_cart'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_lines', to='delivery.cart')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_lines', to='delivery.item')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('cart', 'item'), name='unique_cart_item')],
            },
        ),
        migrations.RunPython(copy_existing_cart_items, restore_cart_items),
        migrations.RemoveField(
            model_name='cart',
            name='items',
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.CharField(max_length=250),
        ),
    ]