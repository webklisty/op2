from .views import custom_404_view
from django.urls import path,include
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


#urlpatterns = [
    # Other URL patterns...

    # Login view
    

    # Logout view
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Sign-up view
    
#]


urlpatterns=[
    path('',views.home,name='home'),
    path('search',views.search,name='search'),
    path('category-list',views.category_list,name='category-list'),
    path('brand-list',views.brand_list,name='brand-list'),
    path('product-list',views.product_list,name='product-list'),
    path('category-product-list/<int:cat_id>',views.category_product_list,name='category-product-list'),
    #path('category-product-list/products.php', views.category_product_list, name='category_product_list'),

    path('brand-product-list/<int:brand_id>',views.brand_product_list,name='brand-product-list'),
    path('product/<str:slug>/<int:id>',views.product_detail,name='product_detail'),
    path('filter-data',views.filter_data,name='filter_data'),
    path('load-more-data',views.load_more_data,name='load_more_data'),
    path('add-to-cart',views.add_to_cart,name='add_to_cart'),
    path('cart',views.cart_list,name='cart'),
    path('delete-from-cart',views.delete_cart_item,name='delete-from-cart'),
    path('update-cart',views.update_cart_item,name='update-cart'),
    path('signup/',views.signup,name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LoginView.as_view(), name='logout'),
    path('checkout',views.checkout,name='checkout'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_canceled, name='payment_cancelled'),
    path('save-review/<int:pid>',views.save_review, name='save-review'),
    path('faqs/', views.faq_view, name='faqs'),
    path('delivery/', views.delivery_view, name='delivery'),
    path('guideline/', views.guideline_view, name='guideline'),
    path('privacy/', views.privacy_view, name='privacy'),

    # User Section Start
    path('my-dashboard',views.my_dashboard, name='my_dashboard'),
    path('my-orders',views.my_orders, name='my_orders'),
    path('my-orders-items/<int:id>',views.my_order_items, name='my_order_items'),
    

    # End

    #Mpesa
    #path('lipa-na-mpesa/', views.lipa_na_mpesa, name='lipa_na_mpesa'),
    #path('checkout/', views.checkout, name='checkout'),
    path('mpesa-payment/', views.mpesa_payment, name='mpesa_payment'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa-callback'),  # Add this if needed

    
    #path('initiate-stk-push/', views.initiate_stk_push, name='initiate_stk_push'),
    path('index/', views.index, name='index'),


    # Wishlist
    path('add-wishlist',views.add_wishlist, name='add_wishlist'),
    path('my-wishlist',views.my_wishlist, name='my_wishlist'),
    # My Reviews
    path('my-reviews',views.my_reviews, name='my-reviews'),
    # My AddressBook
    path('my-addressbook',views.my_addressbook, name='my-addressbook'),
    path('add-address',views.save_address, name='add-address'),
    path('activate-address',views.activate_address, name='activate-address'),
    path('update-address/<int:id>',views.update_address, name='update-address'),
    path('edit-profile',views.edit_profile, name='edit-profile'),
    path('404/', custom_404_view, name='custom_404'),


    
 

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



handler404 = custom_404_view






