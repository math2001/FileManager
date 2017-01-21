## Installation

### Using Package Control

You can really easily install FileManager by using [Package Control][pck-con].

If it's not already, you need to [install it][install-pck-con] first.

!!! note
    If you're using the latest build of Sublime Text 3, you can just do
    *Tools → Install Package Control…*

- Open up the command palette (<kbd>ctrl+shift+p</kbd>)
- Search up `Package Control: Install Package` (might take a few seconds)
- In the panel that just showed up, search for `FileManager`

Done! You have now access to every single features of FileManager! :wink:

### Using `git`

```sh
$ cd "%APPDATA%\Sublime Text 3\Packages"             # on Windows
$ cd ~/Library/Application\ Support/Sublime\ Text\ 3 # on Mac
$ cd ~/.config/sublime-text-3                        # on Linux

$ git clone "https://github.com/math2001/FileManager"
```

> So, which one do I pick?!

I depends of what you want to do. If you want to just use FileManager, pick the first solution,
you'll get every update automatically. But if you want to contribute, then choose the second
solution.

## Usage

Here's a few tips that should get you started:

### Create

Press <kbd>alt+n</kbd> to create a file relative to the current opened folder, or, if there is
none, the current view, or finally `C:/Users/<your username>` (`~` for the purists) if no view's
open

### Use the auto completion

Press <kbd>tab</kbd> to go through the auto completion (and <kbd>shift+tab</kbd> to go
backwards)

### Use the aliases

Create and use some [aliases](references/aliases.md)! You already have plenty! For example, you
have `$packages`. Try it out!

### Use the "browser"

Try to create (<kbd>alt+n</kbd>) a folder that *already* exists. You'll see, you're computer will
dance the samba! Na, just kidding, but really, give it a go!

### Bye bye menus!

All the command are available from the command palette! `rename`, `move`, `duplicate`, etc

!!! tip
    Always prefer the command palette to the menus. You'll be *much* faster. You can even
    [add your own items][]!

Here's the next step: all about every FileManager's [commands](commands.md)

[add your own items]: http://docs.sublimetext.info/en/latest/extensibility/command_palette.html
[pck-con]: https://packagecontrol.io/
[install-pck-con]: https://packagecontrol.io/installation
