from collections import OrderedDict
from django.shortcuts import render,redirect
from django.http import HttpResponse,response,JsonResponse
import requests
from django.conf import settings
from .models import Banner,Category,Brand,Product,ProductAttribute,CartOrder,CartOrderItems,ProductReview,Wishlist,UserAddressBook
from django.db.models import Max,Min,Count,Avg
from django.db.models.functions import ExtractMonth
from django.template.loader import render_to_string
from .forms import SignupForm,ReviewAdd,AddressBookForm,ProfileForm
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
#paypal
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
#mpesa
from django.shortcuts import render, HttpResponse, redirect
from .models import STKPushRequest
#from .stk_push import initiate_stk_push  # Import your STK push logic
from django.contrib import messages
from dotenv import load_dotenv


# Home Page
def home(request):
	banners=Banner.objects.all().order_by('-id')
	data=Product.objects.filter(is_featured=True).order_by('-id')
	return render(request,'index.html',{'data':data,'banners':banners})

# Category
def category_list(request):
    data=Category.objects.all().order_by('-id')
    return render(request,'category_list.html',{'data':data})

# Brand
def brand_list(request):
    data=Brand.objects.all().order_by('-id')
    return render(request,'brand_list.html',{'data':data})

# Product List
def product_list(request):
	total_data=Product.objects.count()
	data=Product.objects.all().order_by('-id')[:3]
	min_price=ProductAttribute.objects.aggregate(Min('price'))
	max_price=ProductAttribute.objects.aggregate(Max('price'))
	return render(request,'product_list.html',
		{
			'data':data,
			'total_data':total_data,
			'min_price':min_price,
			'max_price':max_price,
		}
		)

# Product List According to Category
def category_product_list(request,cat_id):
	category=Category.objects.get(id=cat_id)
	data=Product.objects.filter(category=category).order_by('-id')
	return render(request,'category_product_list.html',{
			'data':data,
			})

# Product List According to Brand
def brand_product_list(request,brand_id):
	brand=Brand.objects.get(id=brand_id)
	data=Product.objects.filter(brand=brand).order_by('-id')
	return render(request,'category_product_list.html',{
			'data':data,
			})

# Product Detail
#def product_detail(request,slug,id):
#	product=Product.objects.get(id=id)
#	related_products=Product.objects.filter(category=product.category).exclude(id=id)[:4]
#	colors=ProductAttribute.objects.filter(product=product).values('color__id','color__title','color__color_code').distinct()
#	sizes=ProductAttribute.objects.filter(product=product).values('size__id','size__title','price','color__id').distinct()
#	reviewForm=ReviewAdd()

	# Check
#	canAdd=True
#	reviewCheck=ProductReview.objects.filter(user=request.user,product=product).count()
#	if request.user.is_authenticated:
#		if reviewCheck > 0:
#			canAdd=False
	# End

	# Fetch reviews
#	reviews=ProductReview.objects.filter(product=product)
	# End

	# Fetch avg rating for reviews
#	avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
	# End

#	return render(request, 'product_detail.html',{'data':product,'related':related_products,'colors':colors,'sizes':sizes,'reviewForm':reviewForm,'canAdd':canAdd,'reviews':reviews,'avg_reviews':avg_reviews})




from django.shortcuts import get_object_or_404  # Import the get_object_or_404 function

def product_detail(request, slug, id):
    # Check if the provided 'id' parameter is a valid integer
    try:
        product_id = int(id)
    except ValueError:
        # Handle the case where 'id' is not a valid integer
        # You can raise an Http404 exception or provide an appropriate error message
        return render(request, 'error_page.html', {'error_message': 'Invalid product ID'})

    # Use get_object_or_404 to retrieve the product, which will raise a 404 error if not found
    product = get_object_or_404(Product, id=product_id)

    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    colors = ProductAttribute.objects.filter(product=product).values('color__id', 'color__title', 'color__color_code').distinct()
    sizes = ProductAttribute.objects.filter(product=product).values('size__id', 'size__title', 'price', 'color__id').distinct()
    reviewForm = ReviewAdd()

    # Check if the user can add a review
    canAdd = True
    if request.user.is_authenticated:
        reviewCheck = ProductReview.objects.filter(user=request.user, product=product).count()
        if reviewCheck > 0:
            canAdd = False

    # Fetch reviews
    reviews = ProductReview.objects.filter(product=product)

    # Fetch average rating for reviews
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))

    return render(request, 'product_detail.html', {
        'data': product,
        'related': related_products,
        'colors': colors,
        'sizes': sizes,
        'reviewForm': reviewForm,
        'canAdd': canAdd,
        'reviews': reviews,
        'avg_reviews': avg_reviews,
    })


# Search
def search(request):
	q=request.GET['q']
	data=Product.objects.filter(title__icontains=q).order_by('-id')
	return render(request,'search.html',{'data':data})

# Filter Data
def filter_data(request):
	colors=request.GET.getlist('color[]')
	categories=request.GET.getlist('category[]')
	brands=request.GET.getlist('brand[]')
	sizes=request.GET.getlist('size[]')
	minPrice=request.GET['minPrice']
	maxPrice=request.GET['maxPrice']
	allProducts=Product.objects.all().order_by('-id').distinct()
	allProducts=allProducts.filter(productattribute__price__gte=minPrice)
	allProducts=allProducts.filter(productattribute__price__lte=maxPrice)
	if len(colors)>0:
		allProducts=allProducts.filter(productattribute__color__id__in=colors).distinct()
	if len(categories)>0:
		allProducts=allProducts.filter(category__id__in=categories).distinct()
	if len(brands)>0:
		allProducts=allProducts.filter(brand__id__in=brands).distinct()
	if len(sizes)>0:
		allProducts=allProducts.filter(productattribute__size__id__in=sizes).distinct()
	t=render_to_string('ajax/product-list.html',{'data':allProducts})
	return JsonResponse({'data':t})

# Load More
def load_more_data(request):
	offset=int(request.GET['offset'])
	limit=int(request.GET['limit'])
	data=Product.objects.all().order_by('-id')[offset:offset+limit]
	t=render_to_string('ajax/product-list.html',{'data':data})
	return JsonResponse({'data':t}
)

# Add to cart
def add_to_cart(request):
	# del request.session['cartdata']
	cart_p={}
	cart_p[str(request.GET['id'])]={
		'image':request.GET['image'],
		'title':request.GET['title'],
		'qty':request.GET['qty'],
		'price':request.GET['price'],
	}
	if 'cartdata' in request.session:
		if str(request.GET['id']) in request.session['cartdata']:
			cart_data=request.session['cartdata']
			cart_data[str(request.GET['id'])]['qty']=int(cart_p[str(request.GET['id'])]['qty'])
			cart_data.update(cart_data)
			request.session['cartdata']=cart_data
		else:
			cart_data=request.session['cartdata']
			cart_data.update(cart_p)
			request.session['cartdata']=cart_data
	else:
		request.session['cartdata']=cart_p
	return JsonResponse({'data':request.session['cartdata'],'totalitems':len(request.session['cartdata'])})

# Cart List Page
def cart_list(request):
    total_amt = 0.0  # Initialize total_amt as a float
    if 'cartdata' in request.session:
        for p_id, item in request.session['cartdata'].items():
            try:
                item_price = float(item['price'])
                item_qty = int(item['qty'])
                total_amt += item_qty * item_price
            except ValueError:
                # Handle the case where 'price' or 'qty' cannot be converted to float or int
                # You can log an error message or take appropriate action here
                pass

        return render(request, 'cart.html', {'cart_data': request.session['cartdata'], 'totalitems': len(request.session['cartdata']), 'total_amt': total_amt})
    else:
        return render(request, 'cart.html', {'cart_data': '', 'totalitems': 0, 'total_amt': total_amt})




# Delete Cart Item
def delete_cart_item(request):
	p_id=str(request.GET['id'])
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			del request.session['cartdata'][p_id]
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id,item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
	return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})

# Delete Cart Item
def update_cart_item(request):
	p_id=str(request.GET['id'])
	p_qty=request.GET['qty']
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			cart_data[str(request.GET['id'])]['qty']=p_qty
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id,item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
	return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})

# Signup Form
def signup(request):
	if request.method=='POST':
		form=SignupForm(request.POST)
		if form.is_valid():
			form.save()
			username=form.cleaned_data.get('username')
			pwd=form.cleaned_data.get('password1')
			user=authenticate(username=username,password=pwd)
			login(request, user)
			return redirect('home')
	form=SignupForm
	return render(request, 'registration/signup.html',{'form':form})


# Checkout
@login_required
def checkout(request):
	total_amt=0
	totalAmt=0
	if 'cartdata' in request.session:
		for p_id,item in request.session['cartdata'].items():
			totalAmt+=int(item['qty'])*float(item['price'])
		# Order
		order=CartOrder.objects.create(
				user=request.user,
				total_amt=totalAmt
			)
		# End
		for p_id,item in request.session['cartdata'].items():
			total_amt+=int(item['qty'])*float(item['price'])
			# OrderItems
			items=CartOrderItems.objects.create(
				order=order,
				invoice_no='INV-'+str(order.id),
				item=item['title'],
				image=item['image'],
				qty=item['qty'],
				price=item['price'],
				total=float(item['qty'])*float(item['price'])
				)
			# End
		# Process Payment
		host = request.get_host()
		paypal_dict = {
		    'business': settings.PAYPAL_RECEIVER_EMAIL,
		    'amount': total_amt,
		    'item_name': 'OrderNo-'+str(order.id),
		    'invoice': 'INV-'+str(order.id),
		    'currency_code': 'USD',
		    'notify_url': 'http://{}{}'.format(host,reverse('paypal-ipn')),
		    'return_url': 'http://{}{}'.format(host,reverse('payment_done')),
		    'cancel_return': 'http://{}{}'.format(host,reverse('payment_cancelled')),
		}
		form = PayPalPaymentsForm(initial=paypal_dict)
		address=UserAddressBook.objects.filter(user=request.user,status=True).first()
		return render(request, 'checkout.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt,'form':form,'address':address})

@csrf_exempt
def payment_done(request):
	returnData=request.POST
	return render(request, 'payment-success.html',{'data':returnData})


@csrf_exempt
def payment_canceled(request):
	return render(request, 'payment-fail.html')


# Save Review
def save_review(request,pid):
	product=Product.objects.get(pk=pid)
	user=request.user
	review=ProductReview.objects.create(
		user=user,
		product=product,
		review_text=request.POST['review_text'],
		review_rating=request.POST['review_rating'],
		)
	data={
		'user':user.username,
		'review_text':request.POST['review_text'],
		'review_rating':request.POST['review_rating']
	}

	# Fetch avg rating for reviews
	avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
	# End

	return JsonResponse({'bool':True,'data':data,'avg_reviews':avg_reviews})

# User Dashboard
import calendar
def my_dashboard(request):
	orders=CartOrder.objects.annotate(month=ExtractMonth('order_dt')).values('month').annotate(count=Count('id')).values('month','count')
	monthNumber=[]
	totalOrders=[]
	for d in orders:
		monthNumber.append(calendar.month_name[d['month']])
		totalOrders.append(d['count'])
	return render(request, 'user/dashboard.html',{'monthNumber':monthNumber,'totalOrders':totalOrders})

# My Orders
def my_orders(request):
	orders=CartOrder.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/orders.html',{'orders':orders})

# Order Detail
def my_order_items(request,id):
	order=CartOrder.objects.get(pk=id)
	orderitems=CartOrderItems.objects.filter(order=order).order_by('-id')
	return render(request, 'user/order-items.html',{'orderitems':orderitems})

# Wishlist
def add_wishlist(request):
	pid=request.GET['product']
	product=Product.objects.get(pk=pid)
	data={}
	checkw=Wishlist.objects.filter(product=product,user=request.user).count()
	if checkw > 0:
		data={
			'bool':False
		}
	else:
		wishlist=Wishlist.objects.create(
			product=product,
			user=request.user
		)
		data={
			'bool':True
		}
	return JsonResponse(data)

# My Wishlist
def my_wishlist(request):
	wlist=Wishlist.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/wishlist.html',{'wlist':wlist})

# My Reviews
def my_reviews(request):
	reviews=ProductReview.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/reviews.html',{'reviews':reviews})

# My AddressBook
def my_addressbook(request):
	addbook=UserAddressBook.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/addressbook.html',{'addbook':addbook})

# Save addressbook
def save_address(request):
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm
	return render(request, 'user/add-address.html',{'form':form,'msg':msg})

# Activate address
def activate_address(request):
	a_id=str(request.GET['id'])
	UserAddressBook.objects.update(status=False)
	UserAddressBook.objects.filter(id=a_id).update(status=True)
	return JsonResponse({'bool':True})

# Edit Profile
def edit_profile(request):
	msg=None
	if request.method=='POST':
		form=ProfileForm(request.POST,instance=request.user)
		if form.is_valid():
			form.save()
			msg='Data has been saved'
	form=ProfileForm(instance=request.user)
	return render(request, 'user/edit-profile.html',{'form':form,'msg':msg})

# Update addressbook
def update_address(request,id):
	address=UserAddressBook.objects.get(pk=id)
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST,instance=address)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm(instance=address)
	return render(request, 'user/update-address.html',{'form':form,'msg':msg})





#faqs
def faq_view(request):
    return render(request, 'faq.html')

#delivery 
def delivery_view(request):
    return render(request, 'delivery.html')

#payment guidelines 
def guideline_view(request):
    return render(request, 'guideline.html')


#privacy
def privacy_view(request):
    return render(request, 'privacy.html')




from django.shortcuts import render
import base64
import re
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import CartOrder, CartOrderItems
from .forms import PhoneNumberForm  # Create a Django form for the phone number
from datetime import datetime
import os


# Your existing code for the checkout view

# M-Pesa Payment Integration
@csrf_exempt
def mpesa_payment(request):
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)  # Create a form to capture the phone number
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            # Validate phone number
            phone_number = re.sub(r"^0", "254", phone_number) if phone_number.startswith(('01', '07')) else phone_number

            if 'cartdata' in request.session:
                cart_data = request.session['cartdata']
                total_amt = 0.0  # Initialize total amount as a float

                for p_id, item in cart_data.items():
                    try:
                        item_price = float(item['price'])
                        item_qty = int(item['qty'])
                        total_amt += item_qty * item_price
                    except (ValueError, KeyError):
                        # Handle errors if 'price' or 'qty' are missing or cannot be be converted
                        pass

                # Create an order
                order = CartOrder.objects.create(
                    user=request.user,
                    total_amt=total_amt
                )
                print("order", order)

                # Your existing code to create order items

                # Generate an M-Pesa payment request
                consumer_key =os.environ.get("consumer_key")				
                consumer_secret = os.environ.get("consumer_secret")
                lipa_na_mpesa_online_passkey = os.environ.get("lipa_na_mpesa_online_passkey")
                lipa_na_mpesa_online_shortcode = os.environ.get("lipa_na_mpesa_online_shortcode")
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

                payload = {
                    "BusinessShortCode": '174379',
                    "Password": __base64encode(lipa_na_mpesa_online_shortcode + lipa_na_mpesa_online_passkey + timestamp),
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": total_amt,
                    "PartyA": phone_number,
                    "PartyB": '174379',
                    "PhoneNumber": phone_number,
                    "CallBackURL": 'https://demo.requestcatcher.com/test',
                    "AccountReference": 'OrderNo-' + str(order.id),
                    "TransactionDesc": 'E-commerce purchase'
                }

                headers = {
                    "Authorization": 'Bearer'  + generate_mpesa_token(consumer_key, consumer_secret),
                    "Content-Type": "application/json"
                }

                # Send the payment request to M-Pesa
                response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                                         json=payload, headers=headers,)
                print("response", response.text)
                print(payload)
                print('header', headers)
                # Process the response and handle any errors
                if response.status_code == 200:
                    payment_data = response.text
                    # Save payment details in your database

                    # Check if the payment data is None
                    if payment_data is not None:
                        return render(request, 'mpesa-payment.html', {'payment_data': payment_data})
                    else:
                        return render(request, 'mpesa-payment-fail.html')
                else:
                    # Handle payment error
                    return render(request, 'mpesa-payment-fail.html')
            else:
                # Handle no items in the cart
                return render(request, 'empty-cart.html')
    else:
        form = PhoneNumberForm()  # Initialize an empty form
    return render(request, 'mpesa-payment-form.html', {'form': form})



# mpesa callback
@csrf_exempt
def mpesa_callback(request):
    pass
    # print(request)


#BASE64 encodning of string
def __base64encode(data):
    return base64.b64encode(data.encode("ascii")).decode("ascii")

# Generate M-Pesa token
def generate_mpesa_token(consumer_key, consumer_secret):
    password=__base64encode(consumer_key+':'+consumer_secret)
    response = requests.request("GET",
                                'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
                                headers={
                                    'Authorization': 'Basic '+password})
    if response.status_code == 200:
        print("Bearer "+response.json().get('access_token'))
        return response.json().get('access_token')
    return {"code":400}











import requests
import base64
import re
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import CartOrder, CartOrderItems
from .forms import PhoneNumberForm
from datetime import datetime

# Function to send an order confirmation SMS
def send_order_confirmation_sms(customer_phone_number, order_number):
    # You can use a third-party SMS gateway or service to send the SMS
    # Make an API request to send an SMS with the order confirmation message
    sms_api_url = 'https://api.safaricomsms.com/sms/send'
    sms_api_headers = {
        'Authorization': 'O22vJy6rnN2nRAnOPqZ8dkyGxmXG',
        'Content-Type': 'application/json',
    }
    sms_payload = {
        'to': customer_phone_number,
        'message': f'Order Confirmation: Your order with order number {order_number} has been confirmed. Thank you for shopping with us.'
    }
    sms_response = requests.post(sms_api_url, json=sms_payload, headers=sms_api_headers)

    if sms_response.status_code == 200:
        return True  # SMS sent successfully
    else:
        return False  # Handle SMS sending error

# M-Pesa Payment Integration
            
# M-Pesa callback
@csrf_exempt
def mpesa_callback(request):
    # Process the callback request from M-Pesa
    # Check the payment status and get customer_phone_number and order_number from the request

    payment_successful = False

    # Get the payment status code from the response (make sure response is defined)
    payment_status_code = response.json().get('ResultCode')

    if payment_status_code == '0':
        payment_successful = True

    if payment_successful:
        customer_phone_number = request.POST.get('phoneNumber')
        order_number = request.POST.get('accountReference')
        if send_order_confirmation_sms(customer_phone_number, order_number):
            # Handle successful payment and order confirmation
            return render(request, 'payment-success.html')
        else:
            # Handle successful payment but SMS sending failure
            return render(request, 'sms-failure.html')
    else:
        # Handle payment failure
        return render(request, 'payment-failure.html')









from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings

def index(request):
    if request.method == 'POST':
        message = request.POST['message']
        email = request.POST['email']
        name = request.POST['name']
        send_mail(
            name,               # title
            message,            # message
            settings.EMAIL_HOST_USER,   # sender email address
            [email, 'felixwandera055@gmail.com'],   # receiver email
            fail_silently=False
        )
    return render(request, 'email.html')

























