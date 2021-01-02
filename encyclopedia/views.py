from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from . import util


def index(request):

    if request.method == 'POST':
        query = request.POST.get('q')
        results = util.list_entries(title=query)

        # if we only got one result back and it matches the query exactly,
        # go straight to the wiki entry
        if len(results) == 1 and results[0] == query:
            return HttpResponseRedirect(reverse('wiki', args=[query]))

        # else, list search results
        return render(request, "encyclopedia/index.html", {
            "header": f"Search results for: {query}",
            "entries": results,
        })

    return render(request, "encyclopedia/index.html", {
        "header": "All Pages",
        "entries": util.list_entries(),
    })


def load_wiki(request, title):
    content = util.get_entry(title)
    return render(request, f"encyclopedia/wiki.html", {
        "content": content,
        "title": title,
    })
