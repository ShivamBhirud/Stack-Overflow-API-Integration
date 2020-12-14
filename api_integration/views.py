from django.shortcuts import render, redirect
from .models import Fields, Cached_Data
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
import requests
import json


def home(request):
    return render(request, 'api_integration/home.html')

def get_data(request):
    if request.method == 'POST':
        data, body_fields = handle_post_request(request)
        return render(request, 'api_integration/show_data.html',
            {'data':data, 'body_fields':body_fields})

    # Accept GET request from the template
    elif request.method == 'GET':
        data, body_fields = handle_get_request(request)
        return render(request, 'api_integration/show_data.html',
            {'data':data, 'body_fields':body_fields})    

    else:
        # print(request.user.id)
        return render(request, 'api_integration/home.html')

def handle_post_request(request):
    fields = Fields()
    tag = request.POST.get('tagged')
    todate = request.POST.get('todate')
    fromdate = request.POST.get('fromdate')
    order = request.POST.get('orderby')
    q_field = request.POST.get('q')
    body_fields = {'q_field':q_field, 'order':order, 'fromdate':fromdate,
        'todate':todate, 'tag':tag} 
    
    # If Data is cached
    try: 
        print('inside')
        is_cached = Fields.objects.get(q=q_field, tag=tag,
            fromdate=fromdate, todate=todate,orderby=order)
        print('data already present!')
        cached_data = Cached_Data.objects.all().filter(fields=is_cached)
        print('hi')
        data = pagination(request, cached_data)
        print('hello2', data)
        return data, body_fields  
    # Data is NOT cached
    except ObjectDoesNotExist: 
        data = store_data(request,
            q_field, tag, fromdate, todate, order)
        print('line 46:', data)
        return data, body_fields


def handle_get_request(request):
    q = request.GET.get('q', '')
    tag = request.GET.get('tag', '')
    fromdate = request.GET.get('fromdate', '')
    todate = request.GET.get('todate', '')
    order = request.GET.get('order', '')
    body_fields = {'q_field':q, 'order':order, 'fromdate':fromdate,
        'todate':todate, 'tag':tag} 
    field = Fields.objects.get(q=q, tag=tag,
        fromdate=fromdate, todate=todate, orderby=order)
    print('line 56',field)
    cached_data = Cached_Data.objects.all().filter(fields_id=field.id)
    print('cached data len: ',len(cached_data))
    print('line 58', cached_data)
    page_obj = pagination(request, cached_data)
    print('obj list len:',len(page_obj.object_list))
    print('line 63 ', page_obj.number)
    return page_obj, body_fields

# Store data in DB and return
def store_data(request, q_field, tag, fromdate, todate, order):
    fields = Fields()
    fields.tag = tag
    fields.fromdate = fromdate
    fields.todate = todate
    fields.orderby = order
    fields.q = q_field
    fields.save()
    # Check if Data is fetched from the API
    if(fetch_api_data(q_field, tag, fromdate, todate, order)):
        field = Fields.objects.get(q=q_field, tag=tag,
            fromdate=fromdate, todate=todate, orderby=order)
        cached_data = Cached_Data.objects.all().filter(fields_id=field.id)
        print('successful')
        data = pagination(request, cached_data)
        print('line 88:', data)
        return data

# Get data via pagination
def pagination(request, data):
    print('in paginator')
    paginator = Paginator(data,3)
    page_number = request.GET.get('page', 1)
    print('page number: ',page_number)
    page_obj = paginator.get_page(page_number)
    print('page object: ', page_obj)
    return page_obj


# Fetch the data from stackoverflow API
def fetch_api_data(q_field, tag, fromdate, todate, order):
    url = str('https://api.stackexchange.com/search/advanced?'+
    'site=stackoverflow.com&pagesize=100&tagged='+str(tag)+'&order='+str(order)+
    '&fromdate='+str(fromdate)+'&todate='+str(todate)+'&q='+str(q_field))
    api_data = requests.get(url)
    print(api_data.content)
    print('\n\n')
    fields = Fields.objects.get(q=q_field, tag=tag,fromdate=fromdate,
        todate=todate,orderby=order)
    api_data = api_data.content
    api_data = json.loads(api_data)
    try:
        count = 0
        for data in api_data['items']:
            cached_data = Cached_Data(fields=fields)
            print(data['title'])
            print(data['score'])
            print(data['link'])
            print('\n')
            cached_data.title = data['title']
            cached_data.score = data['score']
            cached_data.link = data['link']
            cached_data.save()
            count += 1
        print('count is: ',count)
        return True
    except Exception as e:
        return False
    
