When, in this documentation, I'm talking about settings *in general*, I'm talking about FileManager's settings.

## Quick reminder

There's two "type" of settings.

#### 1: The global settings. Here's the hierarchy:

> Below, you can see the order in which Sublime Text would process a hypothetical hierarchy of settings for Python files on Windows:
>
> 1. Packages/Default/Preferences.sublime-settings
> 2. Packages/Default/Preferences (Windows).sublime-settings
> 3. Packages/AnyOtherPackage/Preferences.sublime-settings
> 4. Packages/AnyOtherPackage/Preferences (Windows).sublime-settings
> 5. Packages/User/Preferences.sublime-settings
> 6. Settings from the current project
> 7. Packages/Python/Python.sublime-settings
> 8. Packages/Python/Python (Windows).sublime-settings
> 9. Packages/User/Python.sublime-settings
> 10. Session data for the current file
> 11. Auto-adjusted settings

> *– from [the unofficial docs](http://docs.sublimetext.info/en/latest/customization/settings.html#the-settings-hierarchy) (Thanks a lot)*

#### 2: The packages settings.

They don't affect anything, except ... the plugin. They have 2 files, with the same name: one in the package folder, the other in you `User` directory. This is the case for FileManager. And this file is called ... `FileManager.sublime-settings`. So, the file in the package directory is the default one, and the one in the user directory **overwrites** them.

## So, which one are you talking about then?

The second one.

## How do I edit them?

There's a few different ways:

- `Preferences -> Packages Settings -> FileManager`
- Open the command palette (<kbd>ctrl+shift+p</kbd>), and find `Preferences: File Manager Settings`

The file on the left is the default one (don't edit it, just look at it), and the one on the right is yours, have fun with it!

## A few example to make sure you understand...

> In your [settings](Settings), you can specify an option: `aliases`. It has to be an object.

<details>
    <summary>In this part, I meant...</summary>
    The FileManager's settings (the second one)
</details>
