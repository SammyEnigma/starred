#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from io import BytesIO
from collections import OrderedDict
import click
from github3 import GitHub
from github3.exceptions import NotFoundError
from . import VERSION
from .github import get_user_starred_by_username


desc = '''# Awesome Stars [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d730\
5f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

> A curated list of my GitHub stars!  Generated by [starred](https://github.com/maguowei/starred)


## Contents
'''

license_ = '''
## License

[![CC0](http://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)]\
(https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, [{username}](https://github.com/{username})\
 has waived all copyright and related or neighboring rights to this work.
'''

html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)


@click.command()
@click.option('--username', envvar='USER', required=True, help='GitHub username')
@click.option('--token', envvar='GITHUB_TOKEN', required=True, help='GitHub token')
@click.option('--sort',  is_flag=True, help='sort by language')
@click.option('--repository', default='', help='repository name')
@click.option('--message', default='update stars', help='commit message')
@click.option('--private', is_flag=True, default=False, help='include private repos')
@click.version_option(version=VERSION, prog_name='starred')
def starred(username, token, sort, repository, message, private):
    """GitHub starred

    creating your own Awesome List used GitHub stars!

    example:
        starred --username maguowei --token=xxxxxxxx --sort > README.md
    """
    if repository:
        file = BytesIO()
        sys.stdout = file
    else:
        file = None

    stars = get_user_starred_by_username(token, username)
    click.echo(desc)
    repo_dict = {}

    for s in stars:
        # skip private repos if --private is not set
        if s.private and not private:
            continue

        language = s.language or 'Others'
        description = html_escape(s.description).replace('\n', '') if s.description else ''
        if language not in repo_dict:
            repo_dict[language] = []
        repo_dict[language].append([s.name, s.url, description.strip()])

    if sort:
        repo_dict = OrderedDict(sorted(repo_dict.items(), key=lambda l: l[0]))

    for language in repo_dict.keys():
        data = u'  - [{}](#{})'.format(language, '-'.join(language.lower().split()))
        click.echo(data)
    click.echo('')

    for language in repo_dict:
        click.echo('## {} \n'.format(language.replace('#', '# #')))
        for repo in repo_dict[language]:
            data = u'- [{}]({}) - {}'.format(*repo)
            click.echo(data)
        click.echo('')

    click.echo(license_.format(username=username))

    if file:
        gh = GitHub(token=token)
        try:
            rep = gh.repository(username, repository)
            readme = rep.readme()
            readme.update(message, file.getvalue())
        except NotFoundError:
            rep = gh.create_repository(repository, 'A curated list of my GitHub stars!')
            rep.create_file('README.md', 'starred initial commit', file.getvalue())
        click.launch(rep.html_url)


if __name__ == '__main__':
    starred()
