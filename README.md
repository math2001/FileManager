# File Manager

File Manager is a plugin for Sublime Text that is suppose to remplace SideBarEnhancement and AdvancedNewFile.

Why? Because those to plugin basically do the same thing: *They mangage files from sublime text*

<!-- MarkdownTOC -->

- ["Spirit"](#spirit)
- [Docs](#docs)
- [Installation](#installation)
- [How to open the `README`](#how-to-open-the-readme)
- [Contributing](#contributing)

<!-- /MarkdownTOC -->

## "Spirit"

This package has as a target to be 100% optimized. There shouldn't be 2 commands when can do the job. You can hide the command you don't use (please submit an issue to let me know if it's the case), there is an auto completion system, and, finally, I use it, so I'm able to see a fair bit of the bug, and I correct them (:smile:).

## Docs

The docs are a work in progress, but there's a few useful infos about the `fm_create` command especially (the one to create/open file/folder). They're simply on the [github wiki](https://github.com/math2001/FileManager/wiki). **Go have a quick look, you won't regret it** :smile:

## Installation

#### Using package control

Because it is not available on package control for now, you have to add this repo "manually" to your list.

1. open up the command palette (`ctrl+shift+p`), and find `Package Control: Add Repository`. Then enter the URL of this repo: `https://github.com/math2001/FileManager` in the input field.
2. open up the command palette again and find `Package Control: Install Package`, and just search for `FileManager`. (just a normal install)

#### Using the command line

```bash
cd "%APPDATA%\Sublime Text 3\Packages"     # on window
cd ~/Library/Application\ Support/Sublime\ Text\ 3 # on mac
cd ~/.config/sublime-text-3                        # on linux

git clone "https://github.com/math2001/FileManager"
```

**Although, remember that this plugin is in *development*. It means that there is probably some bugs. If it's the case, please log an issue [on the github  issue tracker](https://github.com/math2001/FileManager/issues)**

## How to open the [`README`](https://github.com/math2001/FileManager/blob/master/README.md)

Some of the package add a command in the menus, others in the command palette, or other nowhere. None of those options are really good, escpecially the last one on ST3 because the packages are compressed. But, fortunatly, there is plugin that exists and will **solve this problem for us** (and he has a really cute name, don't you think?): [ReadmePlease](https://packagecontrol.io/packages/ReadmePlease).

## Contributing

There is 2 way of contributing to this packages:

You have an idea that could improve this package:

1. fork it
2. create a new branch called with this format: `my-feature`
3. **add it to the todo.md**
4. If you know how to do it, you have the time and you *want* to do it, then **just do it** (and get the pleasure to remove it from the `todo.md`).
5. Pull Request

Note: This plugin is only working on Sublime Text 3.
