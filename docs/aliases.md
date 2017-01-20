## Why should I use aliases?

For example, if you'd like to create file in the Sublime Text packages directory, on window, you'd have to type `~/AppData/Roaming/Sublime Text 3/Packages` and then, the name/path of your file. Because you have access to those aliases

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

You can just type `$packages/` and your file/path! Sounds good? Then keep reading!

So, the table above shows all the aliases you have access to by default when you use the input of FileManager.

Here, the values are the ones I get when, as you can see, I'm editing this page (`Aliases.md`), I'm on Windows, the project name is `FileManagerDocs.sublime-project` etc...

When you want to use those prefixes, you have to prefix them with a `$`, like so: `$packages`, `$project_base_name`.

## Using the aliases

If you're a Sublime Text 3 package developer, you've probably guessed that FileManager is using the `sublime.expand_variables` function. So, you probably already know how it works. If it's the case, you can skip this part, if not, then read on, what are you waiting for? :laughing:

As I just said earlier, every aliases have to be prefixed by a `$`. But you can also wrap the alias name with some `{curly braces}`, with the `$`, like so: `${my var}`. When should you use curly braces? When there is character in the alias name that aren't normally allowed (such as spaces).

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

## Escaping

> What if I want to use a **literal** `$`?

Just prefix it by an other `$`!

```
string: "Hello $$var"
aliases:
    - var: "it doesn't matter"
result: "Hello $$var"
```

Note: the function `sublime.expand_variables` escape the `$` using a backslash (`\`). The problem is that FileManager auto replaces the backslash by forward slashes (because of windows).

### What if I try to use an alias that doesn't exists?

Well, you're computer's going to start dancing the salsa. Na, just kidding. The default value of every aliases are an empty string `''`. So, it will be replaced by an empty string.

```
string: "Hello ${world}"
aliases: 
    - "something": "a value"

result: "Hello "

```

### Changing the default value

If you want to change the default value, in case the alias is not defined, you can do it like so: `${my var:default value}`

```
string: "${my undefined var:my default value} and some text"
aliases: <empty>
result: "my default value and some text"

string: "${my undefined var:my default value} and some text"
aliases: 
    - "my undefined var": "hello"
result: "hello and some text"
```

### Nesting

You can nest them, like so: `${var1:${var2:default}}`.

## Much to complicated

For the default value, and the nested value, I don't see *any* use of this when you have to create a file. You know which aliases you have access to, so... I told you this just so that you're aware that it exists, and you can use it, not because in this case it's useful.

## Real example

For example, if you run the `fm_create` command (<kbd>alt+n</kbd>):

```
$packages/FileManager/FMcommands
```

It will open the ["browser"](Commands#the-browser) listing all the commands of FileManager, because each of them are in a separated file. 

## Custom aliases

This is the good part. In your [settings](Settings), you can specify an option: `aliases`. It has to be an object.

```json
"aliases": {
    "name": "value (with othere $aliases if you want to)"
}
```

In the name, **do not specify the prefixing `$`**. It won't work otherwise.

In your alias' value, you can use other aliases. And those aliases can use others, etc... It's recursive, there's no limit (almost). 


```js
"aliases": {
    "st": "$packages", // because being lazy is the first quality of a programmer
    "stu": "$st/User",
}
```

You see? It's fairly simple, but it saves (at least for me) a fair bit of time! (because I love looking having a look at the plugins code, okay, but I'm sure you'll find a use too!)

### Watch out for infinite loops!

Because aliases can "call" each other, it can make an infinite loop... And you don't want this.

#### An example of infinite loop

```json
"aliases": {
    "first": "include $second",
    "second": "include $first"
}
```

As you can see, they're going to call each other over and over again. So, an error message will pop up, telling you that there's been an infinite loop, and you need to check your aliases. It will also open your default browser right here. If you want to disable this last behaviour, add this to your [settings](Settings):

```json
"open_help_on_alias_infinite_loop": false,
```

*Note: the limit is 100. If there is more than 100 recursions, it will stop, and show up the error message, as explained earlier.*


Watch out for the viscous ones! This one is fairly simple, there's only 2 steps. But here's a not-so-well-intentioned:

```json
"aliases": {
    "first": "include $second",
    "second": "hello $third",
    "third": "show $forth",
    "forth": "loop $first"
}
```
