from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

from . import util


class NewWikiForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea)

    def is_valid(self):
        """
        Check form validity by its field contents, as well as checking if it
        already exists (which would also make it invalid)
        :rtype: bool
        """

        valid = super(NewWikiForm, self).is_valid()
        # NOTE: self.is_valid also creates the cleaned data attribute
        exists = util.entry_exists(self.cleaned_data["title"])

        return valid and not exists


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


def create_wiki(request):

    if request.method == 'POST':
        # create the page from params
        form = NewWikiForm(request.POST)

        if not form.is_valid():
            return render(request, "encyclopedia/create.html", {
                "error": True,
                "form": form,
            })

        else:
            util.save_entry(
                form.cleaned_data["title"],
                form.cleaned_data["content"]
            )
            return HttpResponseRedirect(
                reverse(
                    'wiki', args=[form.cleaned_data["title"]]
                )
            )

    return render(request, "encyclopedia/create.html", {
        "error": False,
        "form": NewWikiForm()
    })
