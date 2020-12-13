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
        fields = Fields()
        tag = request.POST.get('tagged')
        todate = request.POST.get('todate')
        fromdate = request.POST.get('fromdate')
        order = request.POST.get('orderby')
        q_field = request.POST.get('q')

        body_fields = {'q_field':q_field, 'order':order, 'fromdate':fromdate,
            'todate':todate, 'tag':tag} 
        # Check if data is already cached
        # Data is cached
        try: 
            print('inside')
            is_cached = Fields.objects.get(q=q_field, tag=tag,
                fromdate=fromdate, todate=todate,orderby=order)
            print('data already present!')
            cached_data = Cached_Data.objects.all().filter(fields=is_cached)
            print('hi')
            if(cached_data):
                print('hello1')
                data, paginator, page_number = get_page(request, cached_data)
                print('hello2', data)
                print('line 33', page_number)
                return render(request, 'api_integration/show_data.html',
                    {'data':data.object_list, 'previous_page_number': data.previous_page_number,
                    'next_page_number':data.next_page_number, 'has_previous':data.has_previous,
                    'body_fields':body_fields, 'page_number':page_number, 'has_next':data.has_next})  
            else:
                data, paginator, page_number = store_data(request,
                    q_field, tag, fromdate, todate, order)
                print('line 39:', data)
                return render(request, 'api_integration/show_data.html',
                    {'data':data.object_list,'previous_page_number': data.previous_page_number,
                    'next_page_number':data.next_page_number, 'has_previous':data.has_previous,
                    'body_fields':body_fields, 'page_number':page_number, 'has_next':data.has_next})  
        # Data is NOT cached
        except ObjectDoesNotExist: 
            data, paginator, page_number = store_data(request,
                q_field, tag, fromdate, todate, order)
            print('line 46:', data)
            return render(request, 'api_integration/show_data.html',
                {'data':data.object_list,'previous_page_number': data.previous_page_number,
                'next_page_number':data.next_page_number, 'has_previous':data.has_previous,
                'body_fields':body_fields, 'page_number':page_number, 'has_next':data.has_next})  
    elif request.method == 'GET':
        page_number = request.GET.get('page', 1)
        q = request.GET.get('q', '')
        # print('line 63:', q)
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
        print('line 58', cached_data)
        paginator = Paginator(cached_data, 3)
        # page_number = request.GET.get('page', 1)
        # print('page number: ',page_number)
        page_obj = paginator.get_page(page_number)
        
        print('line 63 ', page_obj)
        return render(request, 'api_integration/show_data.html',
            {'data':page_obj.object_list, 'page_number':page_number,
            'previous_page_number': page_obj.previous_page_number,
            'next_page_number':page_obj.next_page_number, 'body_fields':body_fields,
            'has_previous':page_obj.has_previous,'has_next':page_obj.has_next})    

    else:
        # print(request.user.id)
        return render(request, 'api_integration/home.html')

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
        data, paginator, page_number = get_page(request, cached_data)
        print('line 88:', data)
        return data, paginator, page_number

# Get data via pagination
def get_page(request, data):
    print('in paginator')
    paginator = Paginator(data,3)
    page_number = request.GET.get('page', 1)
    print('page number: ',page_number)
    
    page_obj = paginator.get_page(page_number)
    print('page object: ', page_obj)
    return page_obj, paginator, int(page_number)


# Fetch the data from stackoverflow API
def fetch_api_data(q_field, tag, fromdate, todate, order):
    url = str('https://api.stackexchange.com/search/advanced?'+
    'site=stackoverflow.com&tagged='+str(tag)+'&order='+str(order)+
    '&fromdate='+str(fromdate)+'&todate='+str(todate)+'&q='+str(q_field))
    api_data = requests.get(url)
    # print(api_data.json())
    print(api_data.content)
    print('\n\n')
    fields = Fields.objects.get(q=q_field, tag=tag,fromdate=fromdate,
        todate=todate,orderby=order)
    print(fields)
    print('\n')
    # print(cached_data)
    # print('\n')
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
    
