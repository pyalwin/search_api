# from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from collections import Counter
import json
import requests

preprocessed_item = {}
unprocessed_item = {}
preprocessed_word_item = {}
author_dict = {}



def search_func(request):
    # file_data = json.loads(open('/static/data.json').read())
    # term_to_search = input('Input a term to search: ')
    # no_of_results = input('Number of results : ')
    term_to_search = request.GET.get('term', None)
    no_of_results = request.GET.get('no_of_results', None)

    result_list = search_summary(term_to_search, no_of_results)

    return JsonResponse(result_list, safe=False)

def search_summary(term_to_search, no_of_results):

    if not preprocessed_word_item:
        try:
            r = requests.get('http://localhost:8000/static/data.json')
            file_data = r.json()
        except Exception as e:
            return JsonResponse({'message': 'Error'},status=500)
        summary_data = file_data['summaries']

        for item in summary_data:
            unprocessed_item[item['id']] = item
            temp_counter = dict(Counter(item['summary'].split()))
            preprocessed_item[item['id']] = temp_counter
            for word in temp_counter.keys():
                if word in preprocessed_word_item.keys():
                    preprocessed_word_item[word][item['id']] = temp_counter[word]
                else:
                    preprocessed_word_item[word] = {}
                    temp_dict = {}
                    temp_dict[item['id']] = temp_counter[word]
                    preprocessed_word_item[word] = temp_dict

    cumulative_count = Counter()

    # (preprocessed_item, preprocessed_word_item, unprocessed_item) = search_summary(term_to_search, no_of_results)

    for terms in term_to_search.split():
        try:
            cumulative_count += Counter(preprocessed_word_item[terms])
        except:
            pass

    counter_list = cumulative_count.most_common(int(no_of_results))

    result_list = []

    for item_id in counter_list:
        result_list.append(unprocessed_item[item_id[0]])

    # return (preprocessed_item, preprocessed_word_item,unprocessed_item)
    return result_list


def search_with_author_info(request):
    input_queries = request.GET.getlist('terms[]', None)
    no_of_results = request.GET.get('no_of_results', None)

    return_list = []

    for item in input_queries:
        search_result = search_summary(item,no_of_results)
        for res in search_result:
            if res['id'] not in author_dict.keys():
                try:
                    data = {'book_id': res['id']}
                    req = requests.post('https://ie4djxzt8j.execute-api.eu-west-1.amazonaws.com/coding', json=data)
                    author = req.json()['author']
                    res['author'] = author
                    author_dict[res['id']] = author
                except Exception as e:
                    print (req)
            else:
                res['author'] = author_dict[res['id']]
        return_list.append(search_result)
    
    return JsonResponse(return_list, safe=False)




