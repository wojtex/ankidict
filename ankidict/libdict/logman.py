# -*- coding: utf-8 -*-

from pagemodel.html import (Node, StrictNode, Text, ShallowText, Attr,
    Html, StrictHtml, ThisClass, Constant)
from pagemodel.bsoup import PageModel
from libdict.models import Models
from libdict.cache import Cache

import urllib2


__all__ = ["models", "LogmanCache"]

models = Models("logman")

class Entry(PageModel):
    model_class = dict      # FIXME

    page_tree = Html(
    )


class DictionaryPage(PageModel):
    model_class = dict

    page_tree = Html(
        Node.list("div.content1")(
            entries = Entry()
        )
    )

    @classmethod
    def postproc(cls, dic):
        # TODO: Get phrasal verbs entries from Entry and move to dic['entries']
        return dic

class SearchPage(PageModel):
    model_class = dict

    page_tree = Html(
        Node("div.content1 div.border-search")(
            Node.list("div.folded")(
                Node("td > a")(
                    urls=Attr("href"),
                    Node("span")(
                        titles=Text()
                    )
                )
            )
        )
    )

def query_site(query):
    normal_prefix = "http://www.ldoceonline.com/search/?q="
    url = ""
    if query[:7] == "http://":
        url = query
    else:
        url = normal_prefix + query.replace(' ', '+')
    response = urllib2.urlopen(url)
    data = response.read()
    # try to parse disabiguing page
    res = None
    try:
        res = SearchPage(data)
    except ValueError:
        # Nic się jeszcze nie stało...
        # Po prostu to nie ten typ strony...
        pass
    if res:
        urls = res['urls']
        if len(urls) == 0: return []
        if query[:7] == "http://": assert(False)

        urls,_ = zip(*filter(lambda (u,t): t == query, zip(res['urls'], res['titles'])))
        ret = []
        for u in urls:
            # parse it!
            # and add it to ret
            pass
        return ret
    res = None
    # parse real entry page
    try:
        res = DictionaryPage(data)
    except ValueError:
        # Teraz też jeszcze nic się nie stało...
        pass
    if res:
        # po prostu zwracamy entries
        return res['entries']

    # kod jest nieaktualny i nie można sparsować strony
    assert(False)
    # lub wyślij maila do autora...

class LogmanCache(Cache):
    pass
