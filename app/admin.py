from django.contrib import admin
from .models import Category, Product, Size, Color, Review, Contact, CompanyAddress, Discount,Wishlist,CheckOut, Order, OrderItem

# Discount Admin
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'percentage', 'product', 'category', 'is_active']
    search_fields = ['name', 'product__title', 'category__category']
    list_filter = ['discount_type', 'is_active']
    ordering = ['discount_type']


# Inline admin for ProductImage
'''class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 '''

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'selling_price', 'final_price', 'is_featured', 'is_active']
    search_fields = ['title', 'category__category']
    list_filter = ['category', 'is_featured', 'is_active']
    readonly_fields = ['final_price']
 #   inlines = [ProductImageInline]

    def final_price(self, obj):
        return obj.final_price()
    final_price.short_description = 'Final Price After Discount'

# Size Admin
@admin.register(Size)
class SizeModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

# Color Admin
@admin.register(Color)
class ColorModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

# Review Admin
@admin.register(Review)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['product', 'user', 'rating']
    search_fields = ['product__title', 'user__username']

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'parent_category']
    search_fields = ['category']
    list_filter = ['parent_category']

# Contact Admin
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'subject', 'message']

# Company Address Admin
@admin.register(CompanyAddress)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'des', 'street', 'email', 'phone']


# Wishlist
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__title')


@admin.register(CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'mobile', 'city', 'country')

# Inline model admin for OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra empty fields
    fields = ('product', 'quantity', 'price')
    readonly_fields = ('product', 'quantity', 'price')  # Make sure the fields are non-editable

# Register the Order model with the inline for OrderItem
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'checkout', 'total_price', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'checkout__first_name')
    
    # Add the OrderItem inline to the Order model
    inlines = [OrderItemInline]
    
    # Make the status field editable in the admin
    list_editable = ('status',)

# Register the OrderItem model
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order',)
    search_fields = ('order__id', 'product__title')

