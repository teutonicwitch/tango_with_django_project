from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from django.shortcuts import redirect
from django.urls import reverse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import datetime


def index(request):

    


    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}

    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list 
    context_dict['othermessage'] = 'Top 5 most viewed pages:'
    context_dict['pages'] = page_list


    
    response = render(request, 'rango/index.html', context=context_dict)

    visitor_cookie_handler(request)

    #context_dict['visits'] = request.session['visits']

    return response


def about(request):


 visitor_cookie_handler(request)

 visits= {'visits' :request.session['visits']}

 print(request.method)

 print(request.user)
 return render(request, 'rango/about.html', visits)

def show_category(request, category_name_slug):

    context_dict = {}

    try:

        category = Category.objects.get(slug=category_name_slug)

        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages


        context_dict['category'] = category
    except Category.DoesNotExist:

        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

    if form.is_valid():

        form.save(commit=True)

        return redirect('/rango/')
    else:

     print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
 try:
  category = Category.objects.get(slug=category_name_slug)
 except Category.DoesNotExist:
  category = None
# You cannot add a page to a Category that does not exist...
 if category is None:
  return redirect('/rango/')
 form = PageForm()
 if request.method == 'POST':
  form = PageForm(request.POST)
 if form.is_valid():
  if category:
   page = form.save(commit=False)
   page.category = category
   page.views = 0
   page.save()
   return redirect(reverse('rango:show_category',
kwargs={'category_name_slug':
category_name_slug}))
  else:
   print(form.errors)
 context_dict = {'form': form, 'category': category}
 return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
 # A boolean value for telling the template
 # whether the registration was successful.
 # Set to False initially. Code changes value to
 # True when registration succeeds.
 registered = False

 # If it's a HTTP POST, we're interested in processing form data.
 if request.method == 'POST':
 # Attempt to grab information from the raw form information.
 # Note that we make use of both UserForm and UserProfileForm.
  user_form = UserForm(request.POST)
  profile_form = UserProfileForm(request.POST)

 # If the two forms are valid...
  if user_form.is_valid() and profile_form.is_valid():
 # Save the user's form data to the database.
   user = user_form.save()

 # Now we hash the password with the set_password method.
 # Once hashed, we can update the user object.
   user.set_password(user.password)
   user.save()

   profile = profile_form.save(commit=False)
   profile.user = user

 # Did the user provide a profile picture?
 # If so, we need to get it from the input form and
 #put it in the UserProfile model.
   if 'picture' in request.FILES:
    profile.picture = request.FILES['picture']

 # Now we save the UserProfile model instance.
   profile.save()

 # Update our variable to indicate that the template
 # registration was successful.
   registered = True

  else:
 # Invalid form or forms - mistakes or something else?
 # Print problems to the terminal.
   print(user_form.errors, profile_form.errors)
 else:
 # Not a HTTP POST, so we render our form using two ModelForm instances.
 # These forms will be blank, ready for user input.
  user_form = UserForm()
  profile_form = UserProfileForm()

 # Render the template depending on the context.
 return render(request,
 'rango/register.html',
 context = {'user_form': user_form,
 'profile_form': profile_form,
 'registered': registered})

def user_login(request):
# If the request is a HTTP POST, try to pull out the relevant information.
 if request.method == 'POST':

  username = request.POST.get('username')
  password = request.POST.get('password')

  user = authenticate(username=username, password=password)

  if user:

   if user.is_active:

    login(request, user)
    return redirect(reverse('rango:index'))
   else:

    return render(request, 'rango/restricted.html')
  else:

   print(f"Invalid login details: {username}, {password}")
   return HttpResponse("Invalid login details supplied.")
  
 else:
   
   return render(request, 'rango/login.html')

   
@login_required
def restricted(request):
 return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):

 logout(request)

 return redirect(reverse('rango:index'))

def visitor_cookie_handler(request):
 visits = int(get_server_side_cookie(request, 'visits', '1'))
 last_visit_cookie = get_server_side_cookie(request,
 'last_visit',
 str(datetime.now()))
 last_visit_time = datetime.strptime(last_visit_cookie[:-7],
 '%Y-%m-%d %H:%M:%S')
# If it's been more than a day since the last visit...
 if (datetime.now() - last_visit_time).days > 0:
  visits = visits + 1
# Update the last visit cookie now that we have updated the count
  request.session['last_visit'] = str(datetime.now())
 else:
# Set the last visit cookie
  request.session['last_visit'] = last_visit_cookie
# Update/set the visits cookie
 request.session['visits'] = visits

def get_server_side_cookie(request, cookie, default_val=None):
 val = request.session.get(cookie)
 if not val:
  val = default_val
 return val

 
 
