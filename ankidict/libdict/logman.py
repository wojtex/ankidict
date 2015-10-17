# -*- coding: utf-8 -*-

from pagemodel.html import (Node, StrictNode, Text, ShallowText, Attr,
    Html, StrictHtml, ThisClass, Constant)
from pagemodel.bsoup import PageModel
from libdict.models import Models
from libdict.cache import Cache

import urllib2


__all__ = ["models", "LogmanCache"]

models = Models("logman")

class Example(PageModel):
    model_class = models.Example

    page_tree = Html(
        Node("> img")(),
        content = Text()
    )

class ColloExampleList(PageModel):
    model_class = dict

    page_tree = Html(
        # TODO
    )

class GramExampleList(PageModel):
    model_class = dict

    page_tree = Html(
        # TODO
    )

class Subsense(PageModel):
    model_class = models.Subsense

    page_tree = Html(
        Node("> ftdef > span.DEF")(
            Node("span")(),
            definition = Text()
        )
        # TODO: They can be mixed.
        #Node.list("> ftexa > div.EXAMPLE")(
        #    examples = Example()
        #)
        #Node.list("> div.ColloExa")(
        #    collo_examples = ColloExampleList()
        #)
        #Node.list("> div.GramExa")(
        #    gram_examples = GramExampleList()
        #)
    )

class Sense(PageModel):
    model_class = models.Sense

    page_tree = Html(
        Node("> div.Sense")(
            Node.optional("> h2 > span.SIGNPOST > span")(
                shortened_def = Text()
            ),
            Node.optional("> span.REGISTERLAB")(
                Node("> span")(),
                style_level = Text()
            ),
            Node.optional("> span.GRAM")(
                Node("> span")(),
                syntax_coding = Text(),
                Node("> span")()
            ),
            Node("> ftdef > span.DEF")(
                definition = Text()
            ),
            Node("> span.SYN")(
                # TODO
            ),
            Node("> span.OPP")(
                # TODO
            ),
            Node("> span.RELATEDWD")(
                # TODO
            )
            # TODO: examples like in subsense
            # ...
            Node.list("> div.Subsense")(
                subsenses = Subsense()
            )
        )
    )

class Entry(PageModel):
    model_class = models.Entry

    page_tree = Html(
        # parse entry
        Node("> div.Head > div.unfolded > table.headword")(
            Node("span.headwordSelected span.HWD")(
                original_key=Text()
            ),
            Node("span.wordclassSelected span.POS")(
                part_of_speech=Text()
            )
        ),
        Node.list("> div.Sense")(
            senses = Sense()
        ),
        Node.optional("> div.Tail")(
        )
    )

class PhrasalVerbEntry(PageModel):
    model_class = models.Entry

    page_tree = Html(
        # parse entry
        Node("> div.Head")(
        ),
        Node.list("> div.Sense")(
            senses = Sense()
        ),
        Node.optional("> div.Tail")(
        )
    )


class DictionaryPage(PageModel):
    model_class = dict

    page_tree = Html(
        Node("div.content1")(
            Node("> div.Entry")(
                entries = Entry(),
                Node.list("> div.PhrVbEntry")(
                    phrvbs = PhrasalVerbEntry()
                )
            )
        )
    )

    @classmethod
    def postproc(cls, dic):
        dic['entries'].extend(dic.pop('phrvbs', []))
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
