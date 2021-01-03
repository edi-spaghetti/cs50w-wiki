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


def get_entry(title, as_html=False):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        file_name = get_file_name(title)
        f = default_storage.open(file_name)
        # normalise line endings by removing any carriage returns
        text = f.read().decode("utf-8").replace('\r', '')

        if as_html:
            text = markdown_to_html(text)

        return text

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


def markdown_to_html(markdown):
    """
    Convert markdown text into html.
    Currently supports:
        - headings
        - boldface text
        - unordered lists
        - links
        - paragraphs
    :param markdown: Text input in markdown format
    :return: Html-formatted string
    """

    # init a container for text return value
    text = ""

    # sanitise incoming markdown to avoid injection
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    for char, safe_char in html_escape_table.items():
        markdown = re.sub(char, safe_char, markdown)

    # Split the markdown into blocks, as determined by 2 or more line breaks
    # assume newlines have been normalised
    # TODO: header doesn't require double line break
    blocks = re.split('(?:\n)(?:\n)+', markdown)

    for block in blocks:

        heading = re.match("(#+)\s", block)
        unordered_list = block.startswith("* ")

        if heading:
            level = len(heading.group(1))
            inner = re.sub("^#+\s", "", block)
            inner = line_substitution(inner)
            text += f"<h{level}>{inner}</h{level}>"

        elif unordered_list:

            text += "<ul>"
            for list_item in re.split("\n", block):
                inner = re.sub("^\*\s", "", list_item)
                inner = line_substitution(inner)
                text += f"<li>{inner}</li>"

            text += "</ul>"

        else:
            text += "<p>"
            text += line_substitution(block)
            text += "</p>"

    return text


def line_substitution(text):
    """
    Replaces markdown with html for syntax that doesn't span multiple lines
    Currently Supports:
        - Bold
        - Links
    :param text: Markdown text that requires substitution
    :return: Html-formatted text for supported tags
    """

    text = re.sub("\*\*([^\*.]+)\*\*", r"<b>\1</b>", text)
    text = re.sub("\[([^\].]+)\]\(([^\).]+)\)", r'<a href="\2">\1</a>', text)

    return text
