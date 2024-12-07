from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime
from django.conf import settings
from django.core.validators import MinValueValidator
# Create your models here.

STATE_CHOICES = (
  ('Andaman & Nicobar Islands','Andaman & Nicobar Islands'),
  ('Andhra Pradesh','Andhra Pradesh'),
  ('Arunachal Pradesh','Arunachal Pradesh'),
  ('Assam','Assam'),
  ('Bihar','Bihar'),
  ('Chandigarh','Chandigarh'),
  ('Chhattisgarh','Chhattisgarh'),
  ('Dadra & Nagar Haveli','Dadra & Nagar Haveli'),
  ('Daman and Diu','Daman and Diu'),
  ('Delhi','Delhi'),
  ('Goa','Goa'),
  ('Gujarat','Gujarat'),
  ('Haryana','Haryana'),
  ('Himachal Pradesh','Himachal Pradesh'),
  ('Jammu & Kashmir','Jammu & Kashmir'),
  ('Jharkhand','Jharkhand'),
  ('Karnataka','Karnataka'),
  ('Kerala','Kerala'),
  ('Lakshadweep','Lakshadweep'),
  ('Madhya Pradesh','Madhya Pradesh'),
  ('Maharashtra','Maharashtra'),
  ('Manipur','Manipur'),
  ('Meghalaya','Meghalaya'),
  ('Mizoram','Mizoram'),
  ('Nagaland','Nagaland'),
  ('Odisha','Odisha'),
  ('Puducherry','Puducherry'),
  ('Punjab','Punjab'),
  ('Rajasthan','Rajasthan'),
  ('Sikkim','Sikkim'),
  ('Tamil Nadu','Tamil Nadu'),
  ('Telangana','Telangana'),
  ('Tripura','Tripura'),
  ('Uttarakhand','Uttarakhand'),
  ('Uttar Pradesh','Uttar Pradesh'),
  ('West Bengal','West Bengal'),
)

# Customer
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES,max_length=50)

    def __str__(self):
        return str(self.id)


# Discount
class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('product', 'Product'),
        ('category', 'Category'),
    )

    name = models.CharField(max_length=100, help_text="Name of the discount (e.g., 'Summer Sale', 'T-shirt Discount')")
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    percentage = models.PositiveIntegerField(help_text="Discount percentage (e.g., 10 for 10%)")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True, related_name='discounts', help_text="Link to product for product-specific discount")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True, related_name='discounts', help_text="Link to category for category-specific discount")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.percentage}% ({self.discount_type})"

# Categories
class Category(models.Model):
    category = models.CharField(max_length=100)
    categories_image = models.ImageField(upload_to='categories_images/')
    products_count = models.PositiveIntegerField(default=0)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.category

    def get_descendants(self, include_self=False):
        """
        Recursively fetch all subcategories (children, grandchildren, etc.) of this category.
        """
        descendants = []
        if include_self:
            descendants.append(self)
        for subcategory in self.subcategories.all():
            descendants.extend(subcategory.get_descendants(include_self=True))
        return descendants


# Size
class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

# Color
class Color(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# Product 
class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='productimg')
    stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sizes = models.ManyToManyField('Size')
    colors = models.ManyToManyField('Color')

    def __str__(self):
        return self.title

   
    def save(self, *args, **kwargs):
        if self.discounted_price and self.discounted_price > self.selling_price:
            raise ValidationError('Discounted price cannot be greater than the selling price.')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def final_price(self):
        """Calculate final price after applying discounts."""
        if self.discounted_price and self.discounted_price < self.selling_price:
            return self.discounted_price
        elif self.category.discount_percentage:
            return self.selling_price * (1 - self.category.discount_percentage / 100)
        return self.selling_price

    def average_rating(self):
        ratings = self.reviews.aggregate(models.Avg('rating'))
        return ratings['rating__avg'] or 0

    def reviews_count(self):
        return self.reviews.count()


# Image Proudct
'''class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')'''

# Wish list
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.title}"

# Review
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True) 
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True) 

    def __str__(self):
        return f'{self.user.username} review on {self.product.title}'


# Contact
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=70)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=500)


#  Company Address
class CompanyAddress(models.Model):
    des = models.CharField(max_length=150)
    street = models.CharField(max_length=200)
    email = models.EmailField(max_length=70)
    phone = models.CharField(max_length=13)


# Cart
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"
    

# Check Out
class CheckOut(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    mobile = models.CharField(max_length=15)
    address_1 = models.CharField(max_length=300)
    address_2 = models.CharField(max_length=300, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checkout = models.ForeignKey(CheckOut, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"Order {self.id} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('app.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} x {self.quantity}"