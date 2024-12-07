from django.urls import path
from app import views
from django.contrib.auth import views as auth_views
from .forms import  MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm
from app.views import CustomLoginView,wishlist,add_to_wishlist,remove_from_wishlist,add_to_cart, update_cart,remove_from_cart

urlpatterns = [
    path("",views.home,name='home'),
    path('contact/',views.contact,name='contact'),
    path('shop/',views.shop,name='shop'),
    path('detail/<int:id>/', views.shopDetail, name='detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('update-cart/<int:cart_item_id>/', update_cart, name='update_cart'),
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
     
    path('featured/',views.featured,name='featured'),
    path('women/',views.women,name='women'),
    path('category/<int:category_id>/',views.category_products, name='category_products'),
   
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_item_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('footer',views.footer,name='footer'),
    path('discount/products/<int:discount_percentage>/', views.discounted_products_view, name='discounted_products'),
    path('discount/categories/<int:category_id>/', views.discounted_categories_view, name='discounted_categories'),
    path('search/', views.product_search, name='product_search'),






    # authentication
  
    path('delete-account/', views.delete_account, name='delete_account'),
    path('accounts/login/', CustomLoginView.as_view(template_name='app/login.html'), name='login'),
    path('registration/', views.CustomerRegistrationView.as_view(), name='signup'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('logout/',auth_views.LogoutView.as_view(next_page='login'),name='logout'),


    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name='app/passwordchange.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone/'), name='passwordchange'),
    path('passwordchangedone/', auth_views.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'), name='passwordchangedone'),    

    path("password-reset/", auth_views.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=MyPasswordResetForm), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html', form_class=MySetPasswordForm), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name="password_reset_complete"),

]