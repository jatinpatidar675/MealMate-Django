from django.db import models

# Create your models here.
class Customer(models.Model):
    username = models.CharField(max_length = 20)
    password = models.CharField(max_length = 128)
    email = models.CharField(max_length = 254)
    mobile = models.CharField(max_length = 32)
    address = models.CharField(max_length = 250)

class Restaurant(models.Model):
    name = models.CharField(max_length = 20)
    picture = models.URLField(max_length = 200, default = "https://www.meesho.com/uday-galleries-french-fries-burger-wall-frame-set-food-poster-for-kitchen-cafe-restaurant-decor-set-of-2-8x12-inch/p/aa8ssa")
    cuisine = models.CharField(max_length = 200)
    rating = models.FloatField()
    
class Item(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = "items")
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 200)
    price = models.FloatField()
    vegeterian = models.BooleanField(default=False)
    picture = models.URLField(max_length = 400, default='https://www.indiafilings.com/learn/wp-content/uploads/2024/08/How-to-Start-Food-Business.jpg')    
    
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = "cart")

    def total_price(self):
        return sum(line.item.price * line.quantity for line in self.cart_lines.select_related("item"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, related_name = "cart_lines")
    item = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = "cart_lines")
    quantity = models.PositiveIntegerField(default = 1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ["cart", "item"], name = "unique_cart_item"),
        ]


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.CharField(max_length=250)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=30, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL, related_name='order_lines')
    item_name = models.CharField(max_length=100)
    item_picture = models.URLField(max_length=400, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.unit_price * self.quantity