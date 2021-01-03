import random

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

from . import util


class NewWikiForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea)

    def exists(self):
        """
        Checks if the entry exists on disk.
        :rtype: bool
        """
        # NOTE: self.is_valid creates the cleaned data attribute, so we call
        # that first in case it hasn't already been, so we have access to the
        # cleaned data.
        if not hasattr(self, 'cleaned_data'):
            self.is_valid()

        # now check existence with util function
        exists = util.entry_exists(self.cleaned_data["title"])
        return exists

    def save(self):
        """
        Saves form data to disk.
        :return: True if save successful, else False
        """

        # validate and set up cleaned data
        if not hasattr(self, 'cleaned_data'):
            valid = self.is_valid()
            if not valid:
                return valid

        success = util.save_entry(
            self.cleaned_data["title"],
            self.cleaned_data["content"]
        )
        return success


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
    content = util.get_entry(title, as_html=True)
    return render(request, f"encyclopedia/wiki.html", {
        "content": content,
        "title": title,
    })


def create_wiki(request):

    if request.method == 'POST':
        # create the page from params
        form = NewWikiForm(request.POST)

        if not form.is_valid() or form.exists():
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


def update_wiki(request, title):
    error_message = ""

    if request.method == "POST":

        form = NewWikiForm(request.POST)

        try:
            error_message = "Invalid form data"
            assert form.is_valid()

            error_message = f"Cannot overwrite existing entry " \
                            f"{form.cleaned_data['title']}"
            assert not form.exists() or form.cleaned_data["title"] == title

        except AssertionError:

            return render(request, "encyclopedia/update.html", {
                "error_message": error_message,
                "title": title,
                "form": form,
            })

        else:

            # if validation passes, now we can save the file
            form.save()

            # if title was edited, we need to remove the old file
            if form.cleaned_data["title"] != title:
                util.delete_entry(title)

            # redirect to edited page
            return HttpResponseRedirect(
                reverse(
                    'wiki', args=[form.cleaned_data["title"]]
                )
            )

    if util.entry_exists(title):

        form = NewWikiForm({
            "title": title,
            "content": util.get_entry(title)
        })

    else:
        form = None

    return render(request, "encyclopedia/update.html", {
        "error_message": error_message,
        "title": title,
        "form": form,
    })


def random_wiki(request):

    entries = util.list_entries()
    selection = random.choice(entries)
    return HttpResponseRedirect(
        reverse(
            "wiki", args=[selection]
        )
    )
