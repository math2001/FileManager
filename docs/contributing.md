You want to contribute to this package? Great!

If you want to contribute to the documentation, you're at the right place.
Otherwise, you should have a look at [the readme][0]

The documentation is written using [mkdocs][]. So, if you want to just fix a typo for example, you
might not need to download everything, just edit the corresponding markdown file (it's *really*
simple), and if you're a bit careful, it should be all right. But as soon as you start making some
bigger changes, please do the following to have a preview to know how it's going to look like.

Whichever option you chose, you first need to fork this repo.

!!! note
    You can just raise an issue on the [GitHub issue tracker][issues] to request a fix in the docs,
    it's up to you

## Install `mkdocs`

So, you want to make big changes? Or you just want to have the beautiful material theme on your
computer :smile:

So, here's how to get going:

!!! note
    You'll need Python installed on your system. It works with both `2` and `3`.

```sh
$ git clone <your_fork>
$ cd FileManager
$ virtualenv venv
$ source venv/bin/activate  # Windows: .\venv\Scripts\activate.bat
$ pip install -r requirements.txt
```

> I don't have pip!

Quickly, pip is a package manager for python. You can install it by saving this script:
[get-pip.py][get-pip] and running it like so

```sh
$ python get-pip.py
```

> I don't have virtualenv!

Well, you can install it by using `pip` like so:

```sh
$ pip install virtualenv
```

Once you have this installed, you have access to the command `mkdocs`.

## Make your changes!

Now, you need to create a new branch, with the "name" of what your adding. For
example:

```sh
$ git checkout -b improve-fm-create-explanation
```

Make your changes. You can preview them in your browser by running:

```sh
$ mkdocs serve
```

Now, commit your changes, and push them. In this case, it'd be:

```sh
$ git push origin improve-fm-create-explanation
```

And then, just send a pull request :wink:

!!! note
    If you're creating a new page, you'll need to add it the `mkdocs.yml` `pages` object.

    ```yaml
    pages:
      - pagename: page/path.md
    ```

## Convention

To keep this doc enjoyable to edit, here are the conventions that it has to respect:

- keep the line length under 100 chars (`\n` included). I advice you to add this to your project
settings: `rulers: [99]`. Tables are the only exception. URLs are not, because you can specify
them at the bottom of the file — [more info][md-cheat-sheet]
- prefer *files* link instead of *URL* link. You can do this: `[my link](relative/path/to/file.md)`
Mkdocs will convert it to the valid URL for you
- use `!!!` block with avidity! Na, not *that* much, but don't hesitate to use them, it brings
rhythm to the doc, which make it more enjoyable to read. — [more info][admonition]
- use fenced code block: <code>```</code> — [more info][codehilite]

!!! warning
    Those convention haven't been respected since the beginning.

### Recommended `.sublime-project` file

```json
{
    "folders":
    [
        {
            "path": "C:\\Users\\math\\AppData\\Roaming\\Sublime Text 3\\Packages\\FileManager",
            "folder_exclude_patterns": [".sublime", "FMCommands", "messages", "send2trash", "site",
                                        "tests"],
            "file_exclude_patterns": ["messages.json", "*.py"]
        }
    ],
    "settings":
    {
        "save_on_focus_lost": false,
        "spell_check": true,
        "rulers": [99]
    }
}

```

[0]: https://github.com/math2001/FileManager#contributing
[1]: http://www.mkdocs.org/#installation
[get-pip]: https://bootstrap.pypa.io/get-pip.py
[mkdocs]: http://www.mkdocs.org/
[admonition]: http://squidfunk.github.io/mkdocs-material/extensions/admonition/#usage
[md-cheat-sheet]: https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#links
[code-hilite]: http://squidfunk.github.io/mkdocs-material/extensions/codehilite/#usage
[issues]: https://github.com/math2001/FileManager/issues
[codehilite]: http://squidfunk.github.io/mkdocs-material/extensions/codehilite/#usage
