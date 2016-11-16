# File Manager

File Manager is a plugin for Sublime Text that is suppose to remplace SideBarEnhancement and AdvancedNewFile.

Why? Because those to plugin basically do the same thing: *They mangage files from sublime text*

So, why would you take File Manager? Here's a few thing:

- Use auto completion in the input to create a file
- Is available from the side bar
- Compared to SideBarEnhancement, it comes only with feature that are *useful* (thinking about the `edit` open)
- When you select `File: New File`, and you have different folder in the current project, you can pick which folder take as a reference by typing it's position (from 0).

```
FOLDERS
> User
> Default
> fast-markdown
```

If you want to create a file from `fast-markdown`, just type: `2>path/to/my/file`. And the `>` is customizable! You can pick a space for example!

If there is no project open, it's going to create from the file that is currently open, and if there is none, then from `~`.

- It uses user friendly path. Even on window, you can do: `~/Documents/a_new_document.txt`. (it's the same as `C:/Users/<user>/Documents/a_new_document.txt`)
- When you forget what folders were in the current directory, you can try to use the auto completion, but there is better! Say you've typed `~/Pictures`, and `Pictures` exists, if you hit `enter`, it will open a quick panel (such as the command palette) with all the folders and files listed, with 2 options added:
    1. Create from here: open a new input panel to create from were you were in the quick panel
    2. Go up (`..`)
- Logs in the status bar where it's creating the file
- It uses templates! You can create a template for each different extension. In the folder `${packages}/User/.FileManager`, create a file `template.<ext>`, and now, every file that you will create using File Manager with the extension `<ext>` will have as a default content the file you've just created's content.



## Installation (for sublime text 3 only)

#### Using package control

Because it is not available on package control for now, you have to add this repo "manually" to your list.

1. open up the command palette (`ctrl+shift+p`), and find `Package Control: Add Repository`. Then enter the URL of this repo: `https://github.com/math2001/FileManager` in the input field.
2. open up the command palette again and find `Package Control: Install Package`, and just search for `FileManager`. (just a normal install)

## Using the command line

```
cd "%APPDATA%\Roaming\Sublime Text 3\Packages"     # on window
cd ~/Library/Application\ Support/Sublime\ Text\ 3 # on mac
cd ~/.config/sublime-text-3                        # on linux

git clone "https://github.com/math2001/fast-markdown"
```

Note: to open the README, use [ReadmePlease](https://packagecontrol.io/packages/ReadmePlease)
