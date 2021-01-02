from django.shortcuts import render

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def load_wiki(request, title):
    content = util.get_entry(title)
    return render(request, f"encyclopedia/wiki.html", {
        "content": content,
        "title": title,
    })
