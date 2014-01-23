#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
    flask.ext.paginate
    ~~~~~~~~~~~~~~

    Adds pagination support to your application.

    :copyright: (c) 2013 by Lix Xu.
    :license: BSD, see LICENSE for more details
"""

from __future__ import unicode_literals
from flask import request, url_for

_bs_prev_page = '<li class="previous"><a href="{0}">{1}</a></li>'
PREV_PAGES = dict(bootstrap=_bs_prev_page,
    bootstrap2=_bs_prev_page,
    bootstrap3=_bs_prev_page,
    foundation='<li class="arrow"><a href="{0}">{1}</a></li>',
    )

_bs_next_page = '<li class="next"><a href="{0}">{1}</a></li>'
NEXT_PAGES = dict(bootstrap=_bs_next_page,
    bootstrap2=_bs_next_page,
    bootstrap3=_bs_next_page,
    foundation='<li class="arrow"><a href="{0}">{1}</a></li>',
    )

CURRENT_PAGES = dict(bootstrap='<li class="active"><a href="#">{0}</a></li>',
    bootstrap3='<li class="active"><a href="#">{0}</a></li>',
    foundation='<li class="current"><a href="#">{0}</a></li>',
    )
CURRENT_PAGES.update(bootstrap2=CURRENT_PAGES['bootstrap'])

LINK = '<li><a href="{0}">{1}</a></li>'
GAP_MARKERS = dict(bootstrap='<li class="disabled"><a href="#">...</a></li>',
    foundation='<li class="unavailable"><a href="#">...</a></li>',
    )
GAP_MARKERS.update(bootstrap2=GAP_MARKERS['bootstrap'],
    bootstrap3=GAP_MARKERS['bootstrap'],
    )

_bs_prev_disabled_page = '<li class="previous disabled unavailable">\
<a href="#"> {0} </a></li>'
PREV_DISABLED_PAGES = dict(bootstrap=_bs_prev_disabled_page,
    bootstrap2=_bs_prev_disabled_page,
    bootstrap3=_bs_prev_disabled_page,
    foundation='<li class="unavailable"><a href="#">{0}</a></li>',
    )

_bs_next_disabled_page = '<li class="next disabled">\
<a href="#"> {0} </a></li>'
NEXT_DISABLED_PAGES = dict(bootstrap=_bs_next_disabled_page,
    bootstrap2=_bs_next_disabled_page,
    bootstrap3=_bs_next_disabled_page,
    foundation='<li class="unavailable"><a href="#">{0}</a></li>',
    )

PREV_LABEL = '&laquo;'
NEXT_LABEL = '&raquo;'
RECORD_NAME = 'records'

DISPLAY_MSG = '''displaying <b>{start} - {end}</b> {record_name} in
total <b>{total}</b>'''

SEARCH_MSG = '''found <b>{found}</b> {record_name},
displaying <b>{start} - {end}</b>'''

CSS_LINKS = dict(bootstrap='<div class="pagination{0}{1}"><ul>',
    bootstrap2='<div class="pagination{0}{1}"><ul>',
    bootstrap3='<ul class="pagination{0}{1}">',
    foundation='<ul class="pagination{0}{1}">',
    )
CSS_LINKS_END = dict(bootstrap='</ul></div>',
    bootstrap2='</ul></div>',
    bootstrap3='</ul>',
    foundation='</ul>',
    )

# foundation aligment
F_ALIGNMENT = '<div class="pagination-{0}">'


class Pagination(object):
    '''A simple pagination extension for flask
    '''
    def __init__(self, found=0, **kwargs):
        '''provides the params:

            **found**: used when searching

            **page**: current page

            **per_page**: how many records displayed on one page

            **inner_window**: how many links arround current page

            **outer_window**: how many links near first/last link

            **prev_label**: text for previous page, default is **&laquo;**

            **next_label**: text for next page, default is **&raquo;**

            **search**: search or not?

            **total**: total records for pagination

            **display_msg**: text for pagation information

            **search_msg**: text for search information

            **record_name**: record name showed in pagination information

            **link_size**: font size of page links

            **alignment**: the alignment of pagination links

            **bs_version**: the version of bootstrap, default is **2**

            **css_framework**: the css framework, default is **bootstrap**
        '''
        self.found = found
        self.page = kwargs.get('page', 1)
        self.per_page = kwargs.get('per_page', 10)
        self.inner_window = kwargs.get('inner_window', 2)
        self.outer_window = kwargs.get('outer_window', 1)
        self.prev_label = kwargs.get('prev_label') or PREV_LABEL
        self.next_label = kwargs.get('next_label') or NEXT_LABEL
        self.search = kwargs.get('search', False)
        self.total = kwargs.get('total', 0)
        self.display_msg = kwargs.get('display_msg') or DISPLAY_MSG
        self.search_msg = kwargs.get('search_msg') or SEARCH_MSG
        self.record_name = kwargs.get('record_name') or RECORD_NAME
        self.css_framework = kwargs.get('css_framework', 'bootstrap').lower()
        if self.css_framework not in CURRENT_PAGES:
            self.css_framework = 'bootstrap'

        self.bs_version = kwargs.get('bs_version') or 2
        if self.css_framework.startswith('bootstrap'):
            if self.bs_version in (3, '3'):
                self.css_framework = 'bootstrap3'

        self.link_size = kwargs.get('link_size', '')
        if self.link_size:
            if self.css_framework == 'foundation':
                self.link_size = ''
            else:
                self.link_size = ' pagination-{0}'.format(self.link_size)

        self.alignment = kwargs.get('alignment', '')
        if self.alignment and self.css_framework.startswith('bootstrap'):
            self.alignment = ' pagination-{0}'.format(self.alignment)

        self.current_page_fmt = CURRENT_PAGES[self.css_framework]
        self.link_css_fmt = CSS_LINKS[self.css_framework]
        self.gap_marker_fmt = GAP_MARKERS[self.css_framework]
        self.prev_disabled_page_fmt = PREV_DISABLED_PAGES[self.css_framework]
        self.next_disabled_page_fmt = NEXT_DISABLED_PAGES[self.css_framework]
        self.prev_page_fmt = PREV_PAGES[self.css_framework]
        self.next_page_fmt = NEXT_PAGES[self.css_framework]
        self.css_end_fmt = CSS_LINKS_END[self.css_framework]

    @property
    def total_pages(self):
        current_total = self.found if self.search else self.total
        pages = divmod(current_total, self.per_page)
        return pages[0] + 1 if pages[1] else pages[0]

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def endpoint(self):
        return request.endpoint

    @property
    def args(self):
        args = dict(request.args.to_dict().items() + request.view_args.items())
        args.pop('page', None)
        return args

    @property
    def prev_page(self):
        if self.has_prev:
            page = self.page - 1 if self.page > 2 else None
            url = url_for(self.endpoint, page=page, **self.args)
            return self.prev_page_fmt.format(url, self.prev_label)

        return self.prev_disabled_page_fmt.format(self.prev_label)

    @property
    def next_page(self):
        if self.has_next:
            url = url_for(self.endpoint, page=self.page + 1, **self.args)
            return self.next_page_fmt.format(url, self.next_label)

        return self.next_disabled_page_fmt.format(self.next_label)

    @property
    def first_page(self):
        # current page is first page
        if self.has_prev:
            return LINK.format(url_for(self.endpoint, page=1, **self.args), 1)

        return self.current_page_fmt.format(1)

    @property
    def last_page(self):
        if self.has_next:
            url = url_for(self.endpoint, page=self.total_pages, **self.args)
            return LINK.format(url, self.total_pages)

        return self.current_page_fmt.format(self.page)

    @property
    def pages(self):
        if self.total_pages < self.inner_window * 2 - 1:
            return range(1, self.total_pages + 1)

        pages = []
        win_from = self.page - self.inner_window
        win_to = self.page + self.inner_window
        if win_to > self.total_pages:
            win_from -= win_to - self.total_pages
            win_to = self.total_pages

        if win_from < 1:
            win_to = win_to + 1 - win_from
            win_from = 1
            if win_to > self.total_pages:
                win_to = self.total_pages

        if win_from > self.inner_window:
            pages.extend(range(1, self.outer_window + 1 + 1))
            pages.append(None)
        else:
            pages.extend(range(1, win_to + 1))

        if win_to < self.total_pages - self.inner_window + 1:
            if win_from > self.inner_window:
                pages.extend(range(win_from, win_to + 1))

            pages.append(None)
            pages.extend(range(self.total_pages - 1, self.total_pages + 1))
        elif win_from > self.inner_window:
            pages.extend(range(win_from, self.total_pages + 1))
        else:
            pages.extend(range(win_to + 1, self.total_pages + 1))

        return pages

    def single_page(self, page):
        if page == self.page:
            return self.current_page_fmt.format(page)

        if page == 1:
            return self.first_page

        if page == self.total_pages:
            return self.last_page

        return LINK.format(url_for(self.endpoint, page=page, **self.args), page)

    @property
    def links(self):
        '''get all the pagination links'''
        if self.total_pages <= 1:
            return ''

        s = [self.link_css_fmt.format(self.link_size, self.alignment)]
        s.append(self.prev_page)
        for page in self.pages:
            s.append(self.single_page(page) if page else self.gap_marker_fmt)

        s.append(self.next_page)
        s.append(self.css_end_fmt)
        if self.css_framework == 'foundation' and self.alignment:
            s.insert(0, F_ALIGNMENT.format(self.alignment))
            s.append('</div>')

        return ''.join(s)

    @property
    def info(self):
        '''get the pagination information'''
        start = 1 + (self.page - 1) * self.per_page
        end = start + self.per_page - 1
        if end > self.total:
            end = self.total if not self.search else self.found

        if start > self.total:
            start = self.total if not self.search else self.found

        s = ['<div class="pagination-page-info">']
        page_msg = self.search_msg if self.search else self.display_msg
        s.append(page_msg.format(found=self.found,
                                 total=self.total,
                                 start=start,
                                 end=end,
                                 record_name=self.record_name,
                                 )
                 )
        s.append('</div>')
        return ''.join(s)
