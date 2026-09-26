from django.core.management.base import BaseCommand

from delivery.models import Item, Restaurant


def image(photo_id):
    return f'https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1000&q=85'


BROKEN_SUBWAY_PHOTO_ID = 'photo-1553909489-cd47e0ef937f'
BROKEN_LEMONADE_PHOTO_ID = 'photo-1513558161293-cdaf765edfd7'
LEMONADE_PHOTO_ID = 'photo-1523371054106-bbf80586c38c'
BROKEN_GARLIC_BREAD_PHOTO_ID = 'photo-1573140247632-f8fd74997d5c'
GARLIC_BREAD_PHOTO_ID = 'photo-1509440159596-0249088772ff'
LEGACY_SUBWAY_MENU_PHOTOS = {
    'photo-1528735602780-2552fd46c7af',
    'photo-1512621776951-a57141f2eefd',
    'photo-1540420773420-3366772f4999',
}
LEGACY_RESTAURANT_PHOTOS = {
    'Subway': BROKEN_SUBWAY_PHOTO_ID,
    'KFC': 'photo-1626082927389-6cd097cdc6ec',
}


RESTAURANTS = [
    {
        'name': 'Pizza Hut',
        'picture': image('photo-1513104890138-7c749659a591'),
        'cuisine': 'Pizza, Italian',
        'rating': 4.4,
        'items': [
            ('Margherita Pizza', 'Classic mozzarella, basil, and tomato sauce.', 299, True, 'photo-1579751626657-72bc17010498'),
            ('Farmhouse Pizza', 'Roasted peppers, onion, mushrooms, and cheese.', 399, True, 'photo-1513104890138-7c749659a591'),
            ('Paneer Tikka Pizza', 'Tandoori paneer with peppers and a spiced base.', 429, True, 'photo-1579751626657-72bc17010498'),
            ('Garlic Bread', 'Toasted bread with garlic butter and herbs.', 149, True, GARLIC_BREAD_PHOTO_ID),
            ('Choco Volcano', 'Warm chocolate cake with a molten center.', 129, True, 'photo-1606313564200-e75d5e30476c'),
            ('Classic Lemonade', 'Chilled lemonade with a bright citrus finish.', 99, True, LEMONADE_PHOTO_ID),
        ],
    },
    {
        'name': 'Starbucks',
        'picture': image('photo-1461023058943-07fcbe16d735'),
        'cuisine': 'Coffee, Bakery',
        'rating': 4.5,
        'items': [
            ('Caffe Latte', 'Espresso softened with steamed milk.', 245, True, 'photo-1461023058943-07fcbe16d735'),
            ('Cappuccino', 'Espresso with velvety milk and a cocoa finish.', 235, True, 'photo-1570968915860-54d5c301fa9f'),
            ('Cafe Mocha', 'Rich espresso, chocolate, and steamed milk.', 275, True, 'photo-1512568400610-62da28bc8a13'),
            ('Caramel Frappuccino', 'Blended coffee with caramel and cream.', 325, True, 'photo-1461023058943-07fcbe16d735'),
            ('Blueberry Muffin', 'Soft-baked muffin with juicy blueberries.', 195, True, 'photo-1607958996333-41aef7caefaa'),
            ('Chocolate Croissant', 'Buttery pastry filled with dark chocolate.', 210, True, 'photo-1555507036-ab1f4038808a'),
        ],
    },
    {
        'name': 'KFC',
        'picture': image('photo-1476224203421-9ac39bcb3327'),
        'cuisine': 'Vegetarian, Fast food',
        'rating': 4.3,
        'items': [
            ('Veg Zinger Burger', 'Crispy veggie patty, lettuce, and creamy sauce.', 219, True, 'photo-1520072959219-c595dc870360'),
            ('Paneer Rice Bowl', 'Seasoned paneer with rice and fresh greens.', 269, True, 'photo-1512621776951-a57141f2eefd'),
            ('Spicy Paneer Wrap', 'Grilled paneer and peppers in a soft wrap.', 229, True, 'photo-1528735602780-2552fd46c7af'),
            ('Veg Popcorn Bites', 'Crunchy, seasoned vegetable bites.', 169, True, 'photo-1573080496219-bb080dd4f877'),
            ('French Fries', 'Crisp, salted fries served hot.', 119, True, 'photo-1573080496219-bb080dd4f877'),
            ('Chocolate Brownie', 'Fudgy chocolate brownie baked in-house.', 139, True, 'photo-1606313564200-e75d5e30476c'),
        ],
    },
    {
        'name': 'Subway',
        'picture': image('photo-1528735602780-2552fd46c7af'),
        'cuisine': 'Sandwiches, Salads',
        'rating': 4.2,
        'items': [
            ('Veggie Delight Sub', 'Fresh vegetables with your choice of sauces.', 199, True, 'photo-1512621776951-a57141f2eefd'),
            ('Paneer Tikka Sub', 'Grilled paneer, peppers, and mint sauce.', 249, True, 'photo-1540713434306-58505cf1b6fc'),
            ('Corn & Peppers Sub', 'Sweet corn, peppers, greens, and herbed sauce.', 219, True, 'photo-1528735602780-2552fd46c7af'),
            ('Aloo Patty Sub', 'Spiced potato patty with crunchy salad.', 189, True, 'photo-1520072959219-c595dc870360'),
            ('Chocolate Chip Cookie', 'Soft cookie with dark chocolate chunks.', 79, True, 'photo-1499636136210-6f4ee915583e'),
            ('Lemon Iced Tea', 'Refreshing black tea with lemon.', 99, True, 'photo-1556679343-c7306c1976bc'),
        ],
    },
    {
        'name': 'Burger King',
        'picture': image('photo-1568901346375-23c9450c58cd'),
        'cuisine': 'Burgers, Fast food',
        'rating': 4.1,
        'items': [
            ('Crispy Paneer Burger', 'Crispy paneer with lettuce and house sauce.', 269, True, 'photo-1520072959219-c595dc870360'),
            ('Veggie Whopper', 'A hearty veggie patty with classic toppings.', 249, True, 'photo-1520072959219-c595dc870360'),
            ('Aloo Tikki Burger', 'Spiced potato patty with crisp vegetables.', 199, True, 'photo-1520072959219-c595dc870360'),
            ('Loaded Fries', 'Crisp fries topped with cheese and seasoning.', 169, True, 'photo-1573080496219-bb080dd4f877'),
            ('Onion Rings', 'Crunchy golden onion rings.', 139, True, 'photo-1639024471283-03518883512d'),
            ('Chocolate Shake', 'Cold, creamy chocolate milkshake.', 179, True, 'photo-1572490122747-3968b75cc699'),
        ],
    },
]


class Command(BaseCommand):
    help = 'Create or update five demo restaurants and their sample menus.'

    def handle(self, *args, **options):
        Item.objects.filter(vegeterian=False).delete()
        item_count = 0
        for restaurant_data in RESTAURANTS:
            restaurant, _ = Restaurant.objects.get_or_create(
                name=restaurant_data['name'],
                defaults={
                    'picture': restaurant_data['picture'],
                    'cuisine': restaurant_data['cuisine'],
                    'rating': restaurant_data['rating'],
                },
            )
            legacy_photo_id = LEGACY_RESTAURANT_PHOTOS.get(restaurant.name)
            if legacy_photo_id and legacy_photo_id in restaurant.picture:
                restaurant.picture = restaurant_data['picture']
                update_fields = ['picture']
                if restaurant.name == 'KFC':
                    restaurant.cuisine = restaurant_data['cuisine']
                    update_fields.append('cuisine')
                restaurant.save(update_fields=update_fields)
            for name, description, price, vegetarian, picture_id in restaurant_data['items']:
                item, _ = Item.objects.get_or_create(
                    restaurant=restaurant,
                    name=name,
                    defaults={
                        'description': description,
                        'price': price,
                        'vegeterian': vegetarian,
                        'picture': image(picture_id),
                    },
                )
                needs_subway_image_refresh = (
                    restaurant.name == 'Subway'
                    and any(photo_id in item.picture for photo_id in LEGACY_SUBWAY_MENU_PHOTOS)
                    and picture_id not in item.picture
                )
                if BROKEN_SUBWAY_PHOTO_ID in item.picture or needs_subway_image_refresh:
                    item.picture = image(picture_id)
                    item.save(update_fields=['picture'])
                if item.name == 'Classic Lemonade' and BROKEN_LEMONADE_PHOTO_ID in item.picture:
                    item.picture = image(LEMONADE_PHOTO_ID)
                    item.save(update_fields=['picture'])
                if item.name == 'Garlic Bread' and BROKEN_GARLIC_BREAD_PHOTO_ID in item.picture:
                    item.picture = image(GARLIC_BREAD_PHOTO_ID)
                    item.save(update_fields=['picture'])
                item_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(RESTAURANTS)} restaurants and {item_count} menu items.'
        ))