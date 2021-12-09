# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from apps.app.searchapi import *
from apps.app.forms import CompleteForm
from apps.app.request_processing import process_request_parameters, searchFor, get_taxonomies_based_on_request

results_template_map = {
    "Publications": "publications_results.html",
    "Venues": "venue_results.html",
    "Authors": "authors_results.html"
}

step = 10


@login_required(login_url="/login/")
def search_results(request):
    context = {}
    results_template = "publications_results.html"
    if request.method == "POST":
        request_input = process_request_parameters(request)
        search_type, search_query = request_input['search_type'], request_input['search_query']
        request_input['taxonomies'], request_input['non_taxonomies'] = \
            get_taxonomies_based_on_request(request, search_query, search_type)
        records, summary, taxonomy_count, non_taxonomy_count = search_records(request_input)
        form = CompleteForm(taxonomy_count, non_taxonomy_count, search_query, searchFor)
        context = {
            'results': records[:step],
            'start': 1,
            'end': min(step, len(records)),
            'first': 1,
            'last': (len(records)//step)+1,
            'current': 1,
            'previous': 1,
            'next': min(2, len(records)//step),
            'total_records': len(records),
            'summary': summary,
            'form': form,
            'search_type': search_type,
            'search_query': search_query,
            'pages': range(1, (len(records)//step)+2)
        }
        request.session["navigation:"+search_query.lower()+search_type] = {
            'results': records,
            'summary': summary
        }
        results_template = results_template_map[search_type]

    if request.method == "GET":
        search_query, search_type, page_id = request.GET['query'], request.GET['search_type'], int(request.GET['page_index'])
        session_output = request.session.get(search_query.lower()+search_type)
        form = CompleteForm(session_output['taxonomies'], session_output['non-taxonomies'], search_query, search_type)
        records, summary = session_output['results'], session_output['summary']
        context = {
            'results': records[(page_id-1)*step:page_id*step-1],
            'start': ((page_id-1)*step)+1,
            'end': min(page_id*step, len(records)),
            'first': 1,
            'last': (len(records)//step)+1,
            'current': page_id,
            'previous': page_id-1,
            'next': min(page_id+1, len(records) // step),
            'total_records': len(records),
            'summary': summary,
            'form': form,
            'search_type': search_type,
            'search_query': search_query,
            'pages': range(1, (len(records)//step)+2)
        }
        results_template = results_template_map[search_type]
    html_template = loader.get_template(results_template)
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):
    context = {"search_types": searchFor}
    html_template = loader.get_template('home.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
