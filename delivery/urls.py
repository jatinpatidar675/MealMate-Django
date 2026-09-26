from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('open_signup', views.open_signup, name = 'open_signup'),
    path('open_signin', views.open_signin, name = 'open_signin'),
    path('signup', views.signup, name = 'signup'),
    path('signin', views.signin, name = 'signin'),
    path('open_add_restaurant', views.open_add_restaurant, name = 'open_add_restaurant'),
    path('add_restaurant', views.add_restaurant, name = 'add_restaurant'),
    path('open_show_restaurant', views.open_show_restaurant, name = 'open_show_restaurant'),
    path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name = 'open_update_restaurant'),
    path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name = 'update_restaurant'),
    path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name = 'delete_restaurant'),
    path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name = 'open_update_menu'),
    path('update_menu/<int:restaurant_id>', views.update_menu, name = 'update_menu'),
    path('view_menu/<int:restaurant_id>/<str:username>', views.view_menu, name='view_menu'),
    path('customer_home/<str:username>', views.customer_home, name='customer_home'),
    path('add_to_cart/<int:item_id>/<str:username>', views.add_to_cart, name='add_to_cart'),
    path('show_cart/<str:username>', views.show_cart, name='show_cart'),
    path('adjust_cart_item/<str:username>/<int:item_id>', views.adjust_cart_item, name='adjust_cart_item'),
    path('save_delivery_address/<str:username>', views.save_delivery_address, name='save_delivery_address'),
    path('checkout/<str:username>/', views.checkout, name='checkout'),
    path('orders/<str:username>/', views.orders, name='orders'),
    path('my_orders/<str:username>', views.order_history, name='order_history'),
    path('order/<str:username>/<int:order_id>', views.order_detail, name='order_detail'),
]