# File Manager

File Manager is a plugin for Sublime Text that is suppose to replace SideBarEnhancement and AdvancedNewFile.

Why? Because those to plugin basically do the same thing: *They manage files from sublime text*.

With this package, you can create, rename, move, duplicate and delete files or folders. You can also copy there relative/absolute path, or their name.

<!-- MarkdownTOC -->

- ["Spirit"](#spirit)
- [Docs](#docs)
- [Installation](#installation)
- [How to open the `README`](#how-to-open-the-readme)
- [Contributing](#contributing)

<!-- /MarkdownTOC -->

## "Spirit"

This package has as a target to be 100% optimized. There shouldn't be 2 commands when one can do the job. You can hide any command you don't use (please submit an issue to let me know if it's the case), there is an auto completion system, and, finally, I use it. So I'm able to see a fair bit of the bug, and I correct them (:smile:). The idea is to propose only the *needed* options, and hopefully, fit your needs.

## Docs

Although they're a fair bit of information in there, the docs are a work in progress. They're simply on the [github wiki](https://github.com/math2001/FileManager/wiki). **Go have a quick look, you won't regret it** :smile:

## Installation

#### Using package control

1. Open up the command palette: <kbd>ctrl+shift+p</kbd>
2. Search for `Package Control: Install Package`
3. Search for `FileManager`
4. Hit <kbd>enter</kbd> :wink:

#### Using the command line

If you want to contribute to this package, first thanks, and second, you should download this using `git` so that you can propose your changes.

```bash
cd "%APPDATA%\Sublime Text 3\Packages"             # on Windows
cd ~/Library/Application\ Support/Sublime\ Text\ 3 # on Mac
cd ~/.config/sublime-text-3                        # on Linux

git clone "https://github.com/math2001/FileManager"
```

## How to open the [`README`](https://github.com/math2001/FileManager/blob/master/README.md)

To open their README, some of the package add a command in the menus, others in the command palette, or other nowhere. None of those options are really good, escpecially the last one on ST3 because the packages are compressed. But, fortunately, there is plugin that exists and will **solve this problem for us** (and he has a really cute name, don't you think?): [ReadmePlease](https://packagecontrol.io/packages/ReadmePlease). :tada:

## Contributing

You want to contribute? Great! First, whatever you want to do, please raise an issue. Then, if you feel in a hacky mood, go ahead and code it:

- create a branch: `my-feature-name`
- don't hesitate to change stuff in the `.tasks` file.
- Push and PR

Note: This plugin is only working on Sublime Text 3.
