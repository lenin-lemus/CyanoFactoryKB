"""
Copyright (c) 2014 Gabriel Kind <gkind@hs-mittweida.de>
Hochschule Mittweida, University of Applied Sciences

Released under the MIT license
"""

from django.conf.urls import patterns, url

pk_str = r"(?P<pk>[0-9]+)/$"

urlpatterns = patterns('cyanodesign.views',
    url(r'^$', 'index', name="cyano-design-index"),
    url(r'^upload/' + pk_str, 'upload', name="cyano-design-save-upload-form"),
    url(r'^edit/' + pk_str, 'design', name="cyano-design-design"),
    url(r'^history/' + pk_str, 'history', name="cyano-design-history"),
    url(r'^get_reactions/' + pk_str, 'get_reactions', name="cyano-design-get-reactions"),
    url(r'^simulate/' + pk_str, 'simulate', name="cyano-design-simulate"),
    url(r'^export/' + pk_str, 'export', name="cyano-design-export"),
    url(r'^save/' + pk_str, 'save', name="cyano-design-save"),
    url(r'^save_as/' + pk_str, 'save_as', name="cyano-design-saveas"),
    url(r'^delete/$', 'delete', name="cyano-design-delete")
)
