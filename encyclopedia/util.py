import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries(title=None):
    """
    Returns a list of names of encyclopedia entries, optionally filtered.
    :param title: String to filter entry names by. If None, no filtering done.
    :rtype: list[str]
    """
    _, filenames = default_storage.listdir("entries")
    markdown_files = [f for f in filenames if f.endswith('.md')]
    entries = [re.sub("\.md$", "", f) for f in markdown_files]

    if title is None:
        filtered_entries = entries
    else:
        filtered_entries = [e for e in entries if title in e]

    return list(sorted(filtered_entries))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
