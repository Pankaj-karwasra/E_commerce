from django.shortcuts import render, redirect, HttpResponse,get_object_or_404,redirect
from .forms import CustomerRegistrationForm,LoginForm,ContactForm,CheckOutForm,CustomerForm
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q,Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.contrib.auth import views as auth_views
from django.db.models import F
from .models import Customer,Category,Product,Review,Size,Color,CompanyAddress,Discount,Wishlist,CartItem,CheckOut, Order, OrderItem
from django.db.models import Avg
from django.db.models import Q
import json



# Create your views here.
def home(request):
    data = CompanyAddress.objects.all()
    featured_products = Product.objects.filter(is_featured=True)
    categories = Category.objects.all()
    discounted_product_1 = Product.objects.filter(discounted_price__isnull=False).first()
    discounted_product_2 = Product.objects.filter(discounted_price__isnull=False).last()


    recent_products = Product.objects.order_by('-created_at')[:4] 

       # Get categories with active discounts
    categories_with_discount = Category.objects.filter(
        discounts__is_active=True, 
        discounts__percentage__gt=0
    ).distinct()

    return render(request, 'app/index.html', {
        'data':data,
        'featured_products': featured_products,
        'categories': categories,
       'categories_with_discount': categories_with_discount,
        'discounted_product_1': discounted_product_1,
        'discounted_product_2': discounted_product_2,
        'recent_products': recent_products 
    })

# Featured Products
def featured(request):
    featured_products = Product.objects.filter(is_featured=True)
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'app/featured.html', {'featured_products': featured_products,'wishlist_items':wishlist})

# Women Products
def women(request):
   women_products = Product.objects.all()
   return render(request,'app/women.html',{'women':women_products})

# Category
def category_products(request, category_id):
 
    category = get_object_or_404(Category, id=category_id)
   
    categories = category.get_descendants(include_self=True)

    products = Product.objects.filter(category__in=categories)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'app/shop.html', context)


# Contact
def contact(request):
    data = CompanyAddress.objects.all()
    if request.method == 'POST':
        fm = ContactForm(request.POST)
        if fm.is_valid():
            fm.save()
            
            fm = ContactForm()
            return render(request, 'app/contact.html', {'form': fm, 'message': 'Thank you for contacting us!','data':data})
    else:
        fm = ContactForm() 

    return render(request, 'app/contact.html', {'form': fm,'data':data})


# Shop View
def shop(request):
    data = CompanyAddress.objects.all()
    products = Product.objects.all()

    # Get filter parameters from request
    selected_price = request.GET.get('price')
    selected_color = request.GET.get('color')
    selected_size = request.GET.get('size')

    # Apply price filter
    if selected_price and selected_price != 'price-all':
        min_price, max_price = map(int, selected_price.split('-'))
        products = products.filter(discounted_price__gte=min_price, discounted_price__lte=max_price)

    # Apply color filter
    if selected_color and selected_color != 'color-all':
        products = products.filter(colors__id=selected_color)

    # Define valid sizes for filtering
    valid_sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']

    # Apply size filter
    if selected_size and selected_size != 'size-all':
        if selected_size in valid_sizes:  # Check if the selected size is valid
            products = products.filter(sizes__name=selected_size)

    # Get counts for filters (for display in the filter options)
    color_counts = Color.objects.annotate(product_count=Count('product'))
    size_counts = Size.objects.filter(name__in=valid_sizes).annotate(product_count=Count('product'))

    # Pass filtered products and filter counts to template
    context = {
        'data': data,
        'products': products,
        'color_counts': color_counts,
        'size_counts': size_counts,
    }
    return render(request, 'app/shop.html', context)


# Shop Detail View
def shopDetail(request, id):
    data = CompanyAddress.objects.all()
    show = get_object_or_404(Product, id=id)
    star_range = range(1, 6)
   

    # Calculate the final price based on product or category discount
    product_discount = show.discounts.filter(discount_type='product', is_active=True).first()
    category_discount = show.category.discounts.filter(discount_type='category', is_active=True).first()

    if product_discount:
        final_price = show.selling_price * (1 - product_discount.percentage / 100)
        discount_percentage = product_discount.percentage
    elif category_discount:
        final_price = show.selling_price * (1 - category_discount.percentage / 100)
        discount_percentage = category_discount.percentage
    else:
        final_price = show.selling_price
        discount_percentage = 0

    reviews = show.reviews.select_related('size', 'color').all()

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        size_id = request.POST.get('size')
        color_id = request.POST.get('color')

        # Validate that rating and comment are provided
        if not rating or not comment:
            return render(request, 'app/detail.html', {
                'data': data,
                'detail': show,
                'star_range': star_range,
                'reviews': reviews,
                'final_price': final_price,
                'discount_percentage': discount_percentage,
                'error': 'Please provide a rating and comment.'
            })

        # Fetch size and color objects if they are selected
        size = Size.objects.filter(id=size_id).first()
        color = Color.objects.filter(id=color_id).first()
        
        if not size or not color:
            return render(request, 'app/detail.html', {
                'data': data,
                'detail': show,
                'star_range': star_range,
                'reviews': reviews,
                'final_price': final_price,
                'discount_percentage': discount_percentage,
                'error': 'Selected size or color is not available.'
            })

        # Check if the user has already submitted a review for this product
        if Review.objects.filter(product=show, user=request.user).exists():
            return render(request, 'app/detail.html', {
                'data': data,
                'detail': show,
                'star_range': star_range,
                'reviews': reviews,
                'final_price': final_price,
                'discount_percentage': discount_percentage,
                'error': 'You have already reviewed this product.'
            })

        # Create the review object and save it
        try:
            Review.objects.create(
                product=show,
                user=request.user,
                rating=rating,
                comment=comment,
                size=size,
                color=color,
            )
            # Redirect after successfully saving the review
            return redirect('shopDetail', id=show.id)
        except Exception as e:
            return render(request, 'app/detail.html', {
                'data': data,
                'detail': show,
                'star_range': star_range,
                'reviews': reviews,
                'final_price': final_price,
                'discount_percentage': discount_percentage,
                'error': 'There was an error creating the review: ' + str(e)
            })

    # Render the detail page with existing reviews and discounted price
    return render(request, 'app/detail.html', {
        'data': data,
        'detail': show,
        'star_range': star_range,
        'reviews': reviews,
        'final_price': final_price,
        'discount_percentage': discount_percentage,
         
    })

# Checkout
@login_required
def checkout(request):
    if request.method == 'POST':
        form = CheckOutForm(request.POST)
        if form.is_valid():
            checkout_info = form.save()

            # Check if the cart is not empty
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items.exists():
                return redirect('cart')

            # Calculate the total price and subtotal
            subtotal = sum(item.product.selling_price * item.quantity for item in cart_items)
            shipping_cost = 10  # Example shipping cost; adjust as needed
            total = subtotal + shipping_cost

            # Create the order
            order = Order.objects.create(
                user=request.user,
                checkout=checkout_info,
                total_price=total
            )

            # Add items to the order
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.selling_price * item.quantity
                )
            cart_items.delete()

            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckOutForm()

    # Fetch cart items for display and calculation
    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(item.product.selling_price * item.quantity for item in cart_items)
    shipping_cost = 10  # Adjust or calculate dynamically
    total = subtotal + shipping_cost

    data = CompanyAddress.objects.all()
    return render(request, 'app/checkout.html', {
        'form': form,
        'data': data,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total
    })


@login_required
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return redirect('home') 
    
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'app/order_confirmation.html', {'order': order, 'order_items': order_items})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    order_items = {order.id: OrderItem.objects.filter(order=order) for order in orders}
    data = CompanyAddress.objects.all()

    return render(request, 'app/order_history.html', {
        'orders': orders,
        'order_items': order_items,
        'data':data
    })



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = 0
    for item in cart_items:
        item.total_price = item.product.selling_price * item.quantity  
        total += item.total_price
    return render(request, 'app/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def update_cart(request, cart_item_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            quantity = data.get('quantity')
            cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)

            if quantity and str(quantity).isdigit():
                cart_item.quantity = int(quantity)
                cart_item.save()
                
                total_price = cart_item.quantity * cart_item.product.selling_price
                cart_total = sum(item.quantity * item.product.selling_price for item in CartItem.objects.filter(user=request.user))
                
                return JsonResponse({
                    'success': True,
                    'quantity': cart_item.quantity,
                    'total_price': total_price,
                    'cart_total': cart_total
                })
        except (ValueError, CartItem.DoesNotExist):
            return JsonResponse({'success': False}, status=400)

    return JsonResponse({'success': False}, status=400)

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

# Wish list
@login_required
def wishlist(request):
    data = CompanyAddress.objects.all()
    wishlist_items = Wishlist.objects.filter(user=request.user)

    return render(request, 'app/wishlist.html', {'wishlist_items': wishlist_items,'data':data})


# Wish list
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')  

# Wish list
@login_required
def remove_from_wishlist(request, wishlist_item_id):
    # Get the wishlist item using its ID
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id, user=request.user)
    wishlist_item.delete()  # Remove the item
    return redirect('wishlist')


# Search
def product_search(request):
    query = request.GET.get('q', '')

    # Get all categories for the dropdown
    categories = Category.objects.all()

    # Start with all products
    products = Product.objects.all()
    data = CompanyAddress.objects.all()

    # If the query is not empty, filter products based on the query
    if query:
      
        products = products.filter(title__icontains=query)

    context = {
        'products': products,
        'categories': categories,
        'query': query,  
        'data':data
    }

    return render(request, 'app/search.html', context)


# Signup
class CustomerRegistrationView(View):
 def get(self, request):
  form = CustomerRegistrationForm()
  return render(request, 'app/signup.html', {'form':form})
  
 def post(self, request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request, 'Congratulations!! Registered Successfully.')
   form.save()
  return render(request, 'app/signup.html', {'form':form})


# Login
class CustomLoginView(auth_views.LoginView):
    template_name = 'app/login.html' 
    authentication_form = LoginForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        return redirect('home')


# Logout Page
def logout_view(request):
    request.session.flush()
    messages.success(request, "You have successfully logged out.")
    return redirect('login')


# Delete Account
def delete_account(request):
    if request.method == 'POST':
        user = request.user  
        user.delete() 
        logout(request)  
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')  
    return render(request, 'app/delete_account.html')


# Update Profile
@login_required
def update_profile(request):
    # Get the Customer instance related to the current user
    customer = get_object_or_404(Customer, user=request.user)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to a page after successful form submission
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'app/update_profile.html', {'form': form})


# Footer
def footer(request):
    data = CompanyAddress.objects.all()
    return render(request,'app/footer.html',{'data':data})


# Discounted Products View
def discounted_products_view(request, discount_percentage):
    # Get the active discounts with the given percentage for products
    product_discounts = Discount.objects.filter(
        discount_type='product', percentage=discount_percentage, is_active=True
    )
   
    
    # Filter products with a matching discount percentage
    products = Product.objects.filter(
        Q(discounts__in=product_discounts) |
        Q(category__discounts__percentage=discount_percentage, category__discounts__is_active=True)
    ).distinct()

    context = {
        'discount_percentage': discount_percentage,
        'products': products,
        
    }
    return render(request, 'app/discounted_products.html', context)


# Discounted Categories View
def discounted_categories_view(request, category_id):
    # Get the specific category
    category = Category.objects.get(id=category_id)

    # Filter products belonging to the selected category with an active discount
    products = Product.objects.filter(
        Q(category=category) &
        (Q(discounts__is_active=True) | Q(category__discounts__is_active=True))
    ).distinct()
    

    context = {
        'category': category,
        'products': products,
        
    }
    return render(request, 'app/discounted_categories.html', context)
