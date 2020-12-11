from django.shortcuts import render, redirect
from .models import Fields, Cached_Data
import requests
import json
# Create your views here.

def home(request):
    return render(request, 'api_integration/home.html')

def get_data(request):
    if request.method == 'POST':
        fields = Fields()
        tag = request.POST.get('tagged')
        todate = request.POST.get('todate')
        fromdate = request.POST.get('fromdate')
        order = fields.validate_order(request.POST.get('orderby'))
        # Check if data is already cached
        is_cached = Fields.objects.get(tag=tag,fromdate=fromdate,
            todate=todate,orderby=order)
        if(is_cached):
            print('data already present!')
            cached_data = Cached_Data.objects.filter(fields=is_cached)
            return render(request, 'api_integration/show_data.html',
                {'data':cached_data})
        else:
            fields.tag = tag
            fields.fromdate = fromdate
            fields.todate = todate
            fields.orderby = order
            fields.save()
            if(fetch_api_data(tag, fromdate, todate, order)):
                field = Fields.objects.get(tag=tag,fromdate=fromdate,
                    todate=todate,orderby=order)
                cached_data = Cached_Data.objects.filter(fields_id=field.id)

                print('successful')

                return render(request, 'api_integration/show_data.html',
                    {'data':cached_data})
            else:
                print('failure')
                error_message = "Couldn't fetch the data. Try other Tags."
                return render(request, 'api_integration/show_data.html',
                    {'error':error_message})
    else:
        # print(request.user.id)
        return render(request, 'api_integration/home.html')

# Fetch the data from stackoverflow API
def fetch_api_data(tag, fromdate, todate, order):
    url = str('https://api.stackexchange.com/search/advanced?'+
    'site=stackoverflow.com&tagged='+str(tag)+'&order='+str(order)+
    '&fromdate='+str(fromdate)+'&todate='+str(todate)+'&pagesize=10')
    api_data = requests.get(url)
    # print(api_data.json())
    print(api_data.content)
    print('\n\n')
    fields = Fields.objects.get(tag=tag,fromdate=fromdate,
        todate=todate,orderby=order)
    print(fields)
    print('\n')
    # print(cached_data)
    # print('\n')
    api_data = api_data.content
    api_data = json.loads(api_data)
    try:
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
        return True
    except Exception as e:
        return False
    
