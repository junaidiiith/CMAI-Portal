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
from apps.app.request_processing import process_request_parameters, searchFor


@login_required(login_url="/login/")
def search_results(request):
    context = {}
    if request.method == "POST":
        request_input = process_request_parameters(request)
        search_type, search_query = request_input['search_type'], request_input['search_query']
        records, summary, taxonomy_count = search_records(request_input)
        form = CompleteForm(taxonomy_count, search_query, searchFor)
        context = {
            'results': records,
            'summary': summary,
            'form': form,
            'search_type': search_type,
            'search_query': search_query
        }
    html_template = loader.get_template('search_results.html')
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
