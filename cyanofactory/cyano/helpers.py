'''
Created on 18.01.2013

@author: Gabriel
'''

import datetime
import os
import settings
import math

from django.db.models.query import EmptyQuerySet
from django.shortcuts import render_to_response
from django.template import Context, RequestContext, loader
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from cyano.models import Species

#__database_name = "cyano"

def get_queryset_object_or_404(queryset):
    try:
        return queryset.get()
    except MultipleObjectsReturned:
        raise Http404
    except ObjectDoesNotExist:
        raise Http404

def render_queryset_to_response(request = [], queryset = EmptyQuerySet(), model = None, template = '', data = {}, species=None):
    
    _format = request.GET.get('format', 'html')
    
    data['species'] = species
    data['queryset'] = queryset
    data['request'] = request
    data['queryargs'] = {}
    data['email'] = "roebbe.wuenschiers@hs-mittweida.de"
    data['model'] = model
    for key, val in request.GET.iterlists():
        data['queryargs'][key] = val

    if _format == 'html':
        data['is_pdf'] = False
        data['pdfstyles'] = ''
        data['species_list'] = Species.objects.all()
        #data['modelmetadatas'] = getModelsMetadata(SpeciesComponent)
        #data['modelnames'] = getObjectTypes(SpeciesComponent)
        data['last_updated_date'] = datetime.datetime.fromtimestamp(os.path.getmtime(settings.TEMPLATE_DIRS[0] + '/' + template))
        
        return render_to_response(template, data, context_instance = RequestContext(request))

#===============================================================================
#    elif _format == 'bib':
#        response = HttpResponse(
#            write_bibtex(species, queryset),
#            mimetype = "application/x-bibtex; charset=UTF-8",
#            content_type = "application/x-bibtex; charset=UTF-8")
#        response['Content-Disposition'] = "attachment; filename=data.bib"
#    elif _format == 'json':
#        objects = []
#        for obj in queryset:
#            objDict = convert_modelobject_to_stdobject(obj, request.user.is_anonymous())
#            objDict['model'] = obj.__class__.__name__
#            objects.append(objDict)
#        
#        now = datetime.datetime.now(tzlocal())        
#        json = odict()
#        json['title'] = '%s WholeCellKB' % species.name
#        json['comments'] = 'Generated by %s on %s at %s' % ('WholeCellKB', now.isoformat(), settings.ROOT_URL + reverse('cyano.views.exportData', kwargs={'species_wid': species.wid}))
#        json['copyright'] = '%s %s' % (now.year, 'Covert Lab, Department of Bioengineering, Stanford University')
#        json['data'] = objects
#        response = HttpResponse(
#            simplejson.dumps(json, indent=2, ensure_ascii=False, encoding='utf-8'),
#            mimetype = "application/json; charset=UTF-8",
#            content_type = "application/json; charset=UTF-8")
#        response['Content-Disposition'] = "attachment; filename=data.json"
#    elif _format == 'pdf':
#        data['is_pdf'] = True
#        data['pdfstyles'] = ''
#        data['species_list'] = Species.objects.all()
#        data['modelmetadatas'] = getModelsMetadata(SpeciesComponent)
#        data['modelnames'] = getObjectTypes(SpeciesComponent)
# 
#        for fileName in ['styles', 'styles.print', 'styles.pdf']:
#            f = open(settings.STATICFILES_DIRS[0] + '/public/css/' + fileName + '.css', 'r')
#            data['pdfstyles'] += f.read()
#            f.close()
# 
#        response = HttpResponse(
#            mimetype = 'application/pdf',
#            content_type = 'application/pdf')
#        response['Content-Disposition'] = "attachment; filename=data.pdf"
# 
#        template = get_template(template)
# 
#        pdf = pisa.CreatePDF(
#            src = template.render(Context(data)),
#            dest = response)
# 
#        if not pdf.err:
#            return response
#        return Http404
#    elif _format == 'xlsx':
#        #write work book
#        wb = writeExcel(species, queryset, models, request.user.is_anonymous())
# 
#        #save to string
#        result = StringIO()
#        wb.save(filename = result)
# 
#        #generate HttpResponse
#        response = HttpResponse(
#            result.getvalue(),
#            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#        response['Content-Disposition'] = "attachment; filename=data.xlsx"
#    elif _format == 'xml':
#        doc = Document()
#        
#        now = datetime.datetime.now(tzlocal())
#        comment = doc.createComment('\n%s WholeCellKB\nGenerated by %s on %s at %s\n%s %s %s\n' % (
#            species.name, 
#            'WholeCellKB', now.isoformat(), 
#            settings.ROOT_URL + reverse('cyano.views.exportData', kwargs={'species_wid': species.wid}),
#            html_to_ascii('&copy;'), now.year, 'Covert Lab, Department of Bioengineering, Stanford University',
#            ))
#        doc.appendChild(comment)
#        
#        objects = doc.createElement('objects')
#        doc.appendChild(objects)
# 
#        for obj in queryset:
#            objects.appendChild(convert_modelobject_to_xml(obj, doc, request.user.is_anonymous()))
# 
#        response = HttpResponse(
#            doc.toprettyxml(indent=" "*2, encoding = 'utf-8'),
#            mimetype = "application/xml; charset=UTF-8",
#            content_type = "application/xml; charset=UTF-8")
#        response['Content-Disposition'] = "attachment; filename=data.xml"
#===============================================================================
    else:
        import django.http as http
        t = loader.get_template('cyano/error.html')
        data['type'] = 500
        data['message'] = '"%s" is not a supported export format.' % format
        c = Context(data)
        response = http.HttpResponseBadRequest(
            t.render(c),
            mimetype = 'text/html; charset=UTF-8',
            content_type = 'text/html; charset=UTF-8')

    return response

def render_queryset_to_response_error(request = [], queryset = EmptyQuerySet(), model = None, data = {}, species=None, error = 403, msg = "", msg_debug = ""):
    import django.http as http
    
    _format = request.GET.get('format', 'html')
    
    data['species'] = species
    data['queryset'] = queryset
    data['request'] = request
    data['email'] = "roebbe.wuenschiers@hs-mittweida.de"
    data['model'] = model
    data['queryargs'] = {}

    data['is_pdf'] = False
    data['pdfstyles'] = ''
    data['species_list'] = Species.objects.all()
    data['last_updated_date'] = datetime.datetime.fromtimestamp(os.path.getmtime(settings.TEMPLATE_DIRS[0] + '/cyano/error.html'))
    
    if error == 404:
        data['type'] = "Not Found"
        response = http.HttpResponseNotFound
    else:
        data['type'] = "Forbidden"
        response = http.HttpResponseBadRequest
    
    t = loader.get_template('cyano/error.html')
    data['message'] = msg
    data['message_extra'] = msg_debug

    c = Context(data)
    return response(
        t.render(c),
        mimetype = 'text/html; charset=UTF-8',
        content_type = 'text/html; charset=UTF-8')

def format_sequence_as_html(sequence, lineLen=50):
    htmlL = ''
    htmlC = ''
    htmlR = ''
    
    for i in range(int(math.ceil(float(len(sequence)) / float(lineLen)))):
        htmlL += '%s<br/>' % (i * lineLen + 1, )
        htmlC += '%s<br/>' % sequence.seq[i*lineLen:(i + 1) * lineLen]
        htmlR += '%s<br/>' % (min(len(sequence), (i + 1) * lineLen), )
    
    return '<div class="sequence"><div>%s</div><div>%s</div><div>%s</div></div>' % (htmlL, htmlC, htmlR)


def get_column_index(column):
    """Returns the columns index by name (table name is auto detected via the field)
    A db_xref identifier consists of two strings delimited by a **:**.
    
    :param column: Column in the table
    :type column: Django Model Field

    :returns: int -- Column index
    """
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT ordinal_position FROM information_schema.columns WHERE table_name = %s AND column_name = %s", [column.model._meta.db_table, column.column])
    row = cursor.fetchone()
    return row[0]

def get_verbose_name_for_field_by_name(model, field_name):
    return model._meta.get_field_by_name(field_name)[0].verbose_name