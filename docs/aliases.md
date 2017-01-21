## Why should you use aliases?

For example, if you'd like to create file in the Sublime Text packages directory, on window, 
you'd have to type `~/AppData/Roaming/Sublime Text 3/Packages` and then, the name/path of your
file. Because you have access to those aliases

|      Alias Name     |                              Value (changes, that's the good part :wink:)                             |
|---------------------|-------------------------------------------------------------------------------------------------------|
| `project_extension` | `sublime-project`                                                                                     |
| `project_name`      | `FileManagerDocs.sublime-project`                                                                     |
| `file_name`         | `Aliases.md`                                                                                          |
| `packages`          | `C:\Users\math\AppData\Roaming\Sublime Text 3\Packages`                                               |
| `project_base_name` | `FileManagerDocs`                                                                                     |
| `file_base_name`    | `Aliases`                                                                                             |
| `file`              | `C:\Users\math\AppData\Roaming\Sublime Text 3\Packages\FileManagerDocs\wiki\Aliases.md`               |
| `folder`            | `C:\Users\math\AppData\Roaming\Sublime Text 3\Packages\FileManagerDocs`                               |
| `file_extension`    | `md`                                                                                                  |
| `project_path`      | `C:\Users\math\AppData\Roaming\Sublime Text 3\Packages\User\Projects`                                 |
| `file_path`         | `C:\Users\math\AppData\Roaming\Sublime Text 3\Packages\FileManagerDocs\wiki`                          |
| `project`           | `C:\Users\math\AppData\Roaming\Sublime Text 3\Packages\User\Projects\FileManagerDocs.sublime-project` |
| `platform`          | `Windows`                                                                                             |

Here, the values are the ones I get when, as you can see, I'm editing this page (`Aliases.md`), 
I'm on Windows, the project name is `FileManagerDocs.sublime-project` etc...

So, in my case I could just type `$packages/` and it'd be replaced by 
`C:\Users\math\AppData\Roaming\Sublime Text 3\Packages`! Sounds good? Then keep reading!

So, the table above shows all the aliases you have access to by default when you use any input
shown by FileManager.

When you want to use those prefixes, you have to prefix them with a `$`, like so: `$packages`, 
`$project_base_name`, etc.

## Usage

!!! note
    This variable system is exactly the same as the *snippets* variables. So, if you already know
    how to use them, then you can skip this part. Otherwise, then keep reading, what are you
    waiting for? :laughing:


As I just said earlier, every aliases have to be prefixed by a `$`. But you can also wrap the
alias' name with some `{curly braces}`, with the `$`, like so: `${my var}`. 

When should you use curly braces? When there is character in the alias name that aren't normally
allowed (such as spaces).

```
string: "Hello $var!"
aliases: 
    - "var": "world"

result: "Hello world!"

string: "Hello ${my var}!"
aliases: 
    - "my var": "world"

result: "Hello world!"
```

### What if I try to use an alias that doesn't exists?

The default value of every aliases are an empty string `''`. So, it will be replaced by an empty
string.

```
string: "Hello ${world}"
aliases: 
    - "something": "a value"

result: "Hello "

```

### Changing the default value

If you want to change the default value, in case the alias is not defined, you can do it like so:
`${my var:default value}`

```
string: "${my undefined var:my default value} and some text"
aliases: <empty>
result: "my default value and some text"

string: "${my undefined var:my default value} and some text"
aliases: 
    - "my undefined var": "hello"
result: "hello and some text"
```

### Escaping

> What if I want to use a **literal** `$`?

Just prefix it by an other `$`!

```
string: "Hello $$var"
aliases:
    - var: "it doesn't matter"
result: "Hello $$var"
```

!!! note
    the function `sublime.expand_variables` escape the `$` using a backslash (`\`). So, for the
    snippets, you'd have to escape with a `\`. The problem is that FileManager auto replaces the 
    backslash by forward slashes (because of Windows), and because `$` can be in a file name, 
    there's no way to tell if it's an escaped dollar sign, or a path.

### Nesting

You can nest them, like so: `${var1:${var2:default}}`.

### Regex and format string: substitutions

This part is, just as nesting, and default values, probably not of any use *for FileManager*.
I just wanted to mention it because it's useful for the snippets. You can find more info about it 
on [the community powered unofficial documentation][undocs-snippet]

## Real example

For example, if you run the `fm_create` command (<kbd>alt+n</kbd>):

```
$packages/FileManager/FMcommands
```

It will open the ["browser"](Commands#the-browser) listing all the commands of FileManager,
(because each of them are in a separated file).

## Custom aliases

This is the good part. In your [settings](settings.md), you can specify an option: `aliases`. It
has to be an object.

```json
"aliases": {
    "name": "value (with other $aliases if you want to)"
}
```

!!! warning
    In the name, **do not specify the prefixing `$`**. It won't work otherwise.

In your alias' value, you can use other aliases. And those aliases can use others, etc... It's
recursive, there's no limit (almost). 


```js
"aliases": {
    "st": "$packages", // because being lazy is the first quality of a programmer ;)
    "stu": "$st/User",
}
```

You see? It's fairly simple, but it saves (at least for me) a fair bit of time! (because I love
having a look at the plugins code, okay, but I'm sure you'll find a use too!)

### Watch out for infinite loops!

Because aliases can "call" each other, it can make an infinite loop... And you don't want this.

#### An example of infinite loop

```json
"aliases": {
    "first": "include $second",
    "second": "include $first"
}
```

As you can see, they're going to call each other over and over again. So, an error message will pop
up, telling you that there's been an infinite loop, and you need to check your aliases. It will
also open your default browser right here. If you want to disable this last behaviour, add this to
your [settings](settings.md):

```json
"open_help_on_alias_infinite_loop": false,
```

!!! note
    The limit is `100`. If there is more than 100 recursions, it will stop, and show up the error
    message, as explained earlier.


Watch out for the viscous ones! This one is fairly simple, there's only 2 steps. 
But here's a not-so-well-intentioned one:

```json
"aliases": {
    "first": "include $second",
    "second": "hello $third",
    "third": "show $forth",
    "forth": "loop $first"
}
```

[undocs-snippet]: http://docs.sublimetext.info/en/latest/extensibility/snippets.html#substitutions
