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
from apps.app.request_processing import process_request_parameters, searchFor, \
    get_taxonomies_based_on_request, NAVIGATION_KEY, TAXONOMIES_KEY, TAXONOMIES, NON_TAXONOMIES

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

        start, end = 1, min(step, len(records))
        first, last = 1, min(step, (len(records)//step)+1)
        current, next_, previous = 1, min(2, len(records)//step), 1
        pages_ = range(1, min(last, first+step+1))

        context = {
            'user': request.user,
            'results': records[:step],
            'start': start,
            'end': min(step, len(records)),
            'first': first,
            'last': last,
            'current': current,
            'previous': previous,
            'next': next_,
            'total_records': len(records),
            'summary': summary,
            'form': form,
            'search_type': search_type,
            'search_query': search_query,
            'pages': pages_
        }
        request.session[NAVIGATION_KEY + search_query.lower()+search_type] = {
            'results': records,
            'summary': summary,
        }
        results_template = results_template_map[search_type]

    if request.method == "GET":
        request_input = process_request_parameters(request)
        search_query, search_type = request_input['search_query'], request_input['search_type']
        page_id = int(request_input['page_id'])
        key = TAXONOMIES_KEY + search_query.lower() + search_type.lower()
        session_output = request.session.get(key)
        form = CompleteForm(session_output[TAXONOMIES], session_output[NON_TAXONOMIES], search_query, search_type)
        navigation_session_data = request.session[NAVIGATION_KEY + search_query.lower()+search_type]
        records, summary = navigation_session_data['results'], navigation_session_data['summary']

        start, end = ((page_id-1)*step)+1 if page_id else 1, min(page_id*step, len(records)) \
            if page_id else min(step, len(records))
        first, last = 1, min(page_id+step, (len(records)//step)+1)
        current = page_id if page_id else 1
        next_ = min(page_id+1, len(records) // step) if page_id else min(2, len(records)//step)
        previous = page_id-1 if page_id else 1
        pages_ = range(1, min(last, page_id + step if page_id else 11))

        context = {
            'user': request.user,
            'results': records[(page_id-1)*step:page_id*step-1] if page_id else records[:step],
            'start': start,
            'end': end,
            'first': 1,
            'last': min(page_id+step, (len(records)//step)+1),
            'current': current,
            'previous': previous,
            'next': next_,
            'total_records': len(records),
            'summary': summary,
            'form': form,
            'search_type': search_type,
            'search_query': search_query,
            'pages': pages_
        }
        results_template = results_template_map[search_type]
    html_template = loader.get_template(results_template)
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):
    if request.user.is_authenticated:
        context = {"search_types": searchFor}
        html_template = loader.get_template('home.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def landing(request):
    context = {}
    if request.user.is_authenticated and request.user.is_superuser:
        html_template = loader.get_template('landing.html')
        return HttpResponse(html_template.render(context, request))
    else:
        html_template = loader.get_template('page-404.html')
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
