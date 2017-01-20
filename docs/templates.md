## What is this?

When you create a new file, a template is inserted. For now, FileManager chooses which template it should insert using the extension. If you're trying to create a `.py` file, it will look for a template that has the extension `.py`.

You're probably a bit confused right now, so let's clarify this.

#### `${packages}/User/.FileManager/template.*`

You're template are stored in the `.FileManager` folder, inside your Sublime Text `User` directory. If you have a look, it should be empty.

A template will be a file called `template.` plus the extension you want it to be active with.

So, for example, if you create a file called `template.py` inside the the `.FileManager` directory with this content:

```python
# -*- encoding: utf-8 -*-

# this is my template
```

Each time you're going to create a new python file (with the extension `.py`), this content will be inserted as soon as it is opened.

Now, some of you might wondering: *why don't FileManager write the file with the right content, and **then** open it?*. Well, this the good part.

#### Your template is in fact... **snippets**!

Yes, they're in fact snippets! If you don't know how to use them, I strongly recommend having a look at [the unofficial documentation about snippets](http://docs.sublimetext.info/en/latest/extensibility/snippets.html).

## Create/edit templates from Sublime Text

You can create and edit your templates from Sublime Text.

#### Create

Open up the command palette, and in there, you should be able to find `File Manager: Create Template`.

If you pick this option, an input will appear with the text `template.`. Add the extension that you want, and it will create the template (if it already exists, it will simply open it)

Now, just edit the file, and you're done! Your template has been edited.

#### List

Open up the command palette, and in there, you should be able to find `File Manager: List Templates`.

It will open up the browser that you can get in the [create](Commands#create-fm_create) command, listing all your templates. Just pick one to edit it.

Here you go! Hope you enjoy it! If you do, please let others people know about it!
