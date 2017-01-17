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

#### The idea is to make you save time, not to propose you features you're never going to use.

> This package has as main goal to be 100% optimized.

So, for example, there is an **auto completion** system (based on the folders/files, both, you choose) on every input that is showed by FileManager. Just press <kbd>tab</kbd> to cycle through the auto completion.

> There shouldn't be 2 commands when 1 can do the job.

FileManager doesn't have a command `create_new_file` and `create_new_folder`. Just `fm_create`. It opens up an input, and the last character you type in is a `/` (or a `\`), it creates a folder instead of a file.

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

To open their README, some of the package add a command in the menus, others in the command palette, or other nowhere. None of those options are really good, especially the last one on ST3 because the packages are compressed. But, fortunately, there is plugin that exists and will **solve this problem for us** (and he has a really cute name, don't you think?): [ReadmePlease](https://packagecontrol.io/packages/ReadmePlease). :tada:

## Contributing

You want to contribute? Great!

First, whatever you want to do, please raise an issue. Then, if you feel in a hacky mood, go ahead and code it:

- create a branch: `my-feature-name`
- don't hesitate to change stuff in the `.tasks` file.
- Push and PR

Note: This plugin is only working on Sublime Text 3.
