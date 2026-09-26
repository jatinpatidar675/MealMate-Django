from unittest.mock import patch
from io import StringIO

from django.contrib.auth.hashers import check_password
from django.core.management import call_command
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from .models import CartItem, Customer, Item, Order, Restaurant


class AddToCartMessageTests(TestCase):
	def setUp(self):
		self.customer = Customer.objects.create(
			username='taste_tester',
			password='password',
			email='taste@example.com',
			mobile='1234567890',
			address='12 Sample Street',
		)
		restaurant = Restaurant.objects.create(
			name='Test Kitchen',
			cuisine='Modern comfort',
			rating=4.5,
		)
		self.item = Item.objects.create(
			restaurant=restaurant,
			name='Test dish',
			description='A freshly made test dish',
			price=12.5,
			vegeterian=True,
		)

	def test_add_to_cart_shows_one_time_success_toast(self):
		add_url = reverse('add_to_cart', args=(self.item.pk, self.customer.username))
		cart_url = reverse('show_cart', args=(self.customer.username,))

		response = self.client.get(add_url)

		self.assertRedirects(response, cart_url, fetch_redirect_response=False)
		cart_response = self.client.get(cart_url)
		self.assertContains(cart_response, 'Item added successfully.')
		self.assertContains(cart_response, 'class="toast toast--success"')
		self.assertEqual(CartItem.objects.get(item=self.item).quantity, 1)

		next_response = self.client.get(cart_url)
		self.assertNotContains(next_response, 'Item added successfully.')

	def test_quantity_controls_update_totals_and_remove_zero_quantity_lines(self):
		add_url = reverse('add_to_cart', args=(self.item.pk, self.customer.username))
		adjust_url = reverse('adjust_cart_item', args=(self.customer.username, self.item.pk))
		self.client.get(add_url)

		self.client.post(adjust_url, {'action': 'increase'})
		cart_item = CartItem.objects.get(item=self.item)
		self.assertEqual(cart_item.quantity, 2)
		self.assertEqual(cart_item.cart.total_price(), 25)

		self.client.post(adjust_url, {'action': 'decrease'})
		cart_item.refresh_from_db()
		self.assertEqual(cart_item.quantity, 1)
		self.assertEqual(cart_item.cart.total_price(), 12.5)

		self.client.post(adjust_url, {'action': 'decrease'})
		self.assertFalse(CartItem.objects.filter(item=self.item).exists())

	def test_customer_can_update_saved_delivery_address(self):
		address_url = reverse('save_delivery_address', args=(self.customer.username,))
		self.client.get(reverse('add_to_cart', args=(self.item.pk, self.customer.username)))
		response = self.client.post(address_url, {'address': '48 New Street, Apartment 12, Springfield'})

		self.assertRedirects(response, reverse('show_cart', args=(self.customer.username,)), fetch_redirect_response=False)
		self.customer.refresh_from_db()
		self.assertEqual(self.customer.address, '48 New Street, Apartment 12, Springfield')
		self.assertEqual(CartItem.objects.get(item=self.item).quantity, 1)

	def test_keep_browsing_returns_to_customer_restaurant_list(self):
		home_url = reverse('customer_home', args=(self.customer.username,))
		home_response = self.client.get(home_url)
		cart_response = self.client.get(reverse('show_cart', args=(self.customer.username,)))

		self.assertContains(home_response, 'Test Kitchen')
		self.assertContains(cart_response, f'href="{home_url}"')

	def test_signin_upgrades_legacy_plaintext_password(self):
		response = self.client.post(reverse('signin'), {
			'username': self.customer.username,
			'password': 'password',
		})

		self.assertRedirects(
			response,
			reverse('customer_home', args=(self.customer.username,)),
			fetch_redirect_response=False,
		)
		self.customer.refresh_from_db()
		self.assertTrue(check_password('password', self.customer.password))

	def test_signup_stores_hashed_password(self):
		self.client.post(reverse('signup'), {
			'username': 'new_taster',
			'password': 'another-password',
			'email': 'new@example.com',
			'mobile': '9876543210',
			'address': '8 New Street',
		})

		new_customer = Customer.objects.get(username='new_taster')
		self.assertTrue(check_password('another-password', new_customer.password))

	@override_settings(RAZORPAY_KEY_ID='', RAZORPAY_KEY_SECRET='')
	def test_checkout_keeps_cod_available_without_razorpay_credentials(self):
		self.client.get(reverse('add_to_cart', args=(self.item.pk, self.customer.username)))
		response = self.client.get(reverse('checkout', args=(self.customer.username,)))

		self.assertContains(response, 'RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET')
		self.assertContains(response, 'Place COD order')
		self.assertContains(response, 'Test dish')

	def test_cash_on_delivery_places_order_and_clears_cart(self):
		self.client.get(reverse('add_to_cart', args=(self.item.pk, self.customer.username)))
		response = self.client.post(reverse('orders', args=(self.customer.username,)), {'payment_method': 'cod'})

		order = Order.objects.get(customer=self.customer)
		detail_url = reverse('order_detail', args=(self.customer.username, order.pk))
		self.assertRedirects(response, detail_url, fetch_redirect_response=False)
		detail_response = self.client.get(detail_url)
		self.assertContains(detail_response, 'Order placed! Pay cash when it arrives.')
		self.assertContains(detail_response, 'Test dish')
		self.assertContains(detail_response, '12.50')
		self.assertEqual(order.lines.get().quantity, 1)
		self.assertFalse(CartItem.objects.filter(item=self.item).exists())

	@override_settings(RAZORPAY_KEY_ID='rzp_test_id', RAZORPAY_KEY_SECRET='test-secret')
	def test_failed_gateway_verification_preserves_cart(self):
		self.client.get(reverse('add_to_cart', args=(self.item.pk, self.customer.username)))
		response = self.client.post(reverse('orders', args=(self.customer.username,)), {
			'payment_method': 'razorpay',
		})

		self.assertRedirects(response, reverse('checkout', args=(self.customer.username,)), fetch_redirect_response=False)
		self.assertEqual(CartItem.objects.get(item=self.item).quantity, 1)

	@override_settings(RAZORPAY_KEY_ID='rzp_test_id', RAZORPAY_KEY_SECRET='test-secret')
	@patch('delivery.views.razorpay.Client')
	def test_razorpay_receives_the_same_paise_amount_as_checkout(self, razorpay_client):
		self.client.get(reverse('add_to_cart', args=(self.item.pk, self.customer.username)))
		razorpay_client.return_value.order.create.return_value = {'id': 'order_test'}

		response = self.client.get(reverse('checkout', args=(self.customer.username,)))

		self.assertContains(response, '"amount": "1250"')
		order_data = razorpay_client.return_value.order.create.call_args.kwargs['data']
		self.assertEqual(order_data['amount'], 1250)

	def test_seed_demo_data_creates_five_restaurants_with_six_images_each(self):
		subway = Restaurant.objects.create(
			name='Subway',
			picture='https://images.unsplash.com/photo-1553909489-cd47e0ef937f?auto=format&fit=crop&w=1000&q=85',
			cuisine='Sandwiches, Salads',
			rating=4.2,
		)
		Item.objects.create(
			restaurant=subway,
			name='Chicken Teriyaki Sub',
			description='Legacy non-vegetarian menu item.',
			price=289,
			vegeterian=False,
		)
		Item.objects.create(
			restaurant=subway,
			name='Veggie Delight Sub',
			description='Legacy Subway item with a broken photo.',
			price=199,
			vegeterian=True,
			picture='https://images.unsplash.com/photo-1553909489-cd47e0ef937f?auto=format&fit=crop&w=1000&q=85',
		)
		pizza_hut = Restaurant.objects.create(
			name='Pizza Hut',
			picture='https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1000&q=85',
			cuisine='Pizza, Italian',
			rating=4.4,
		)
		Item.objects.create(
			restaurant=pizza_hut,
			name='Classic Lemonade',
			description='Legacy lemonade with a broken image URL.',
			price=99,
			vegeterian=True,
			picture='https://images.unsplash.com/photo-1513558161293-cdaf765edfd7?auto=format&fit=crop&w=1000&q=85',
		)
		Item.objects.create(
			restaurant=pizza_hut,
			name='Garlic Bread',
			description='Legacy garlic bread with an incorrect image.',
			price=149,
			vegeterian=True,
			picture='https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?auto=format&fit=crop&w=1000&q=85',
		)
		call_command('seed_demo_data', stdout=StringIO())
		seeded_names = ['Pizza Hut', 'Starbucks', 'KFC', 'Subway', 'Burger King']
		seeded_restaurants = Restaurant.objects.filter(name__in=seeded_names)

		self.assertEqual(seeded_restaurants.count(), 5)
		self.assertFalse(Item.objects.filter(vegeterian=False).exists())
		self.assertGreater(
			max(len(item.name) for item in Item.objects.filter(restaurant__in=seeded_restaurants)),
			20,
		)
		for restaurant in seeded_restaurants:
			items = restaurant.items.all()
			self.assertEqual(items.count(), 6)
			self.assertTrue(all(item.vegeterian for item in items))
			self.assertTrue(restaurant.picture.startswith('https://images.unsplash.com/'))
			self.assertTrue(all(item.picture.startswith('https://images.unsplash.com/') for item in items))
		subway.refresh_from_db()
		self.assertIn('photo-1528735602780-2552fd46c7af', subway.picture)
		subway_image_urls = list(subway.items.values_list('picture', flat=True))
		self.assertEqual(len(set(subway_image_urls)), 6)
		self.assertIn('photo-1540713434306-58505cf1b6fc', subway.items.get(name='Paneer Tikka Sub').picture)
		self.assertIn('photo-1528735602780-2552fd46c7af', subway.items.get(name='Corn & Peppers Sub').picture)
		lemonade = Restaurant.objects.get(name='Pizza Hut').items.get(name='Classic Lemonade')
		self.assertIn('photo-1523371054106-bbf80586c38c', lemonade.picture)
		garlic_bread = Restaurant.objects.get(name='Pizza Hut').items.get(name='Garlic Bread')
		self.assertIn('photo-1509440159596-0249088772ff', garlic_bread.picture)
		self.assertFalse(
			Restaurant.objects.filter(name='Subway', picture__contains='photo-1553909489-cd47e0ef937f').exists()
		)
		self.assertFalse(Item.objects.filter(picture__contains='photo-1553909489-cd47e0ef937f').exists())

	def test_admin_menu_additions_are_forced_vegetarian(self):
		self.client.post(reverse('update_menu', args=(self.item.restaurant_id,)), {
			'name': 'Garden wrap',
			'description': 'A vegetarian garden wrap.',
			'price': '180',
			'picture': 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af',
		})

		garden_wrap = Item.objects.get(name='Garden wrap')
		self.assertTrue(garden_wrap.vegeterian)

	@override_settings(RAZORPAY_KEY_ID='rzp_test_id', RAZORPAY_KEY_SECRET='test-secret')
	@patch('delivery.views.razorpay.Client')
	def test_verified_online_payment_returns_to_customer_home(self, razorpay_client):
		self.client.get(reverse('add_to_cart', args=(self.item.pk, self.customer.username)))
		client = razorpay_client.return_value
		client.order.fetch.return_value = {'amount': 1250, 'currency': 'INR'}
		client.payment.fetch.return_value = {
			'order_id': 'order_test',
			'amount': 1250,
			'status': 'captured',
		}
		response = self.client.post(reverse('orders', args=(self.customer.username,)), {
			'payment_method': 'razorpay',
			'razorpay_order_id': 'order_test',
			'razorpay_payment_id': 'payment_test',
			'razorpay_signature': 'signed-test',
		})

		order = Order.objects.get(customer=self.customer)
		detail_url = reverse('order_detail', args=(self.customer.username, order.pk))
		self.assertRedirects(response, detail_url, fetch_redirect_response=False)
		detail_response = self.client.get(detail_url)
		self.assertContains(detail_response, 'Payment successful! Your order has been placed.')
		client.utility.verify_payment_signature.assert_called_once()
		self.assertFalse(CartItem.objects.filter(item=self.item).exists())

	def test_customer_can_view_history_but_cannot_view_another_customers_order(self):
		self.client.get(reverse('add_to_cart', args=(self.item.pk, self.customer.username)))
		self.client.post(reverse('orders', args=(self.customer.username,)), {'payment_method': 'cod'})
		order = Order.objects.get(customer=self.customer)

		history = self.client.get(reverse('order_history', args=(self.customer.username,)))
		detail_url = reverse('order_detail', args=(self.customer.username, order.pk))
		detail = self.client.get(detail_url)
		self.assertContains(history, f'Order #{order.pk}')
		self.assertContains(detail, 'read-only receipt')
		self.assertEqual(self.client.post(detail_url).status_code, 405)

		other_customer = Customer.objects.create(
			username='other_customer',
			password='password',
			email='other@example.com',
			mobile='1111111111',
			address='9 Other Road',
		)
		other_detail_url = reverse('order_detail', args=(other_customer.username, order.pk))
		self.assertEqual(self.client.get(other_detail_url).status_code, 404)
