All the input that are created from File Manager has an auto completions system. There is few things that you can change, but let's start with the beginning.

Say you have the following structure:

```
root/
    img/
        favicon.png

    styles/
        stylus/
            main.styl
        css/
            main.css

    scripts/
        coffee/
            main.coffee
        js/
            main.js

    index.html
```

If you want to create a new script, you're going to have to type `scripts/coffee/mynewscript.coffee`. But, if you just type `sc` and then press <kbd>tab</kbd>, you'll see that `scripts/` automatically replace the `sc`, and you can type `co` press <kbd>tab</kbd>, `coffee` will replace the `co`. I say <q>replace</q> because it is case **insensitive**. If you type `ST`, it will replace it by `styles` (in lower case).

Here's a little gif to show you:

![FileManager: auto completion](imgs/auto-completion.gif)

### Options

- `case_sensitive`: defines if the completion case sensitive. (default to `false`)
- `complete_with_files_too`: If you want the auto completion to use complete with files too (default to `true`)
- `pick_first`: only relevant if `complete_with_files_too` is `true`. Define what to choose first if at least one folder and one file are available for completion. The valid values: `files`, `folders` or `null`. (default to `folders`)
