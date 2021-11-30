# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from apps.app.cmai_taxonomies import get_taxonomies
from apps.app.searchapi import *
from apps.app.forms import CompleteForm


@login_required(login_url="/login/")
def search_results(request):
    context = {}
    if request.method == "POST":
        publications = [
            {'name': "A case study on self-configuring systems in IoT based on a model-driven prototyping approach",
             'year': 2016,
             'authors': 'Fabian Kneer, Erik Kamsties',
             'doi': '10.1007/978-3-319-46254-7_59'},
            {'name': "A case study on self-configuring systems in IoT based on a model-driven prototyping approach",
             'year': 2016,
             'authors': 'Fabian Kneer, Erik Kamsties',
             'doi': '10.1007/978-3-319-46254-7_59'},
            {'name': "A case study on self-configuring systems in IoT based on a model-driven prototyping approach",
             'year': 2016,
             'authors': 'Fabian Kneer, Erik Kamsties',
             'doi': '10.1007/978-3-319-46254-7_59'},
            {'name': "A case study on self-configuring systems in IoT based on a model-driven prototyping approach",
             'year': 2016,
             'authors': 'Fabian Kneer, Erik Kamsties',
             'doi': '10.1007/978-3-319-46254-7_59'}
        ]
        context = {'publications': publications}
    html_template = loader.get_template('search_results.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):

    search_types = ["Publications", "Authors", "Conferences", "Journals", "Institutions"]
    taxonomies = get_taxonomies()
    form = CompleteForm(taxonomies, search_types)
    context = {'segment': 'index', 'form': form, "search_types": search_types}

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
