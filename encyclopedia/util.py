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


def entry_exists(title):
    """
    Checks if a given entry title already exists in storage
    :param title: Name of a potential wiki
    :return: True if exists, else False
    """

    filename = get_file_name(title)
    return default_storage.exists(filename)


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = get_file_name(title)
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))

    return entry_exists(title)


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        file_name = get_file_name(title)
        f = default_storage.open(file_name)
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def get_file_name(title):
    """
    Determines file name from title
    :param title: File name without extension and parent directories
    :return: Path to markdown file
    """
    return f"entries/{title}.md"


def delete_entry(title):
    """
    Delete entry file, if it exists
    :param title: File name without extension and parent directories
    :return: True if delete was successful, else False
    """
    filename = get_file_name(title)
    if default_storage.exists(filename):
        default_storage.delete(filename)
        return not entry_exists(title)
    else:
        return False
