import re
import random

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util

wiki_entries_directory = "entries/"


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "title": "Home",
        "heading": "All Pages"
    })


def entry_page(request, title):
    entry_contents = util.get_entry(title)
    html_entry_contents = markdown_to_html(entry_contents) if entry_contents else None
    # html_entry_contents = entry_contents

    return render(request, "encyclopedia/entry.html", {
        "body_content": html_entry_contents,
        "entry_exists": entry_contents is not None,
        "title": title if entry_contents is not None else "Error"
    })


def markdown_to_html(markdown_string):
    if '\r' in markdown_string:
        markdown_string = markdown_string.replace('\r\n', '\n')
    assert('\r' not in markdown_string)
    unique_marker = 'PROTECTED_CHARS_fwargnmejlgnsjglsibgtnovdrsfeaijler'

    heading_matcher = re.compile(r'^(?P<hash_tags>#{1,6})\s*(?P<heading_title>.*)$', re.MULTILINE)
    heading_substituted = heading_matcher.sub(
        lambda m: rf"{unique_marker}<h{len(m.group('hash_tags'))}>{m.group('heading_title')}{unique_marker}"
                  + rf"</h{len(m.group('hash_tags'))}>", markdown_string)

    bold_matcher = re.compile(r"(\*\*|__)(?P<bolded_content>.+?)\1")
    bold_substituted = bold_matcher.sub(r"<b>\g<bolded_content></b>", heading_substituted)

    list_outside_matcher = re.compile(r"^([-*])\s+.*?(?=\n\n|\n((?!\1)[-*])\s|\Z)", re.MULTILINE | re.DOTALL)
    list_inside_matcher = re.compile(r"^([-*])\s+(?P<list_item>.*?)(?=\n[-*]\s+|\Z)", re.MULTILINE | re.DOTALL)
    list_substituted = list_outside_matcher.sub(lambda m: unique_marker + '<ul>\n'
                                                + list_inside_matcher.sub(unique_marker
                                                                          + r"<li>\g<list_item>"
                                                                          + unique_marker + "</li>", m.group())
                                                + '\n' + unique_marker + '</ul>', bold_substituted)

    link_matcher = re.compile(r"\[(?P<text>((?!\n\n).)*?)\]\((?P<link>((?!\n\n).)*?)\)", re.DOTALL)
    link_substituted = link_matcher.sub(rf'<a href="\g<link>">\g<text></a>', list_substituted)

    paragraph_matcher = re.compile(rf"^(?!{unique_marker}|\n|\Z)(?P<paragraph_text>.*?)(?=(\n\n)|{unique_marker}|\Z)",
                                   re.MULTILINE | re.DOTALL)
    paragraph_substituted = paragraph_matcher.sub(r"<p>\g<paragraph_text></p>", link_substituted)

    html_string = paragraph_substituted.replace(unique_marker, '')
    return html_string


if __name__ == "__main__":
    print("THIS IS NOT RUNNING")
    with open("entries/HTML.md") as handle:
        markdown_str = handle.read()
    print(markdown_str)
    print(markdown_to_html(markdown_str))

