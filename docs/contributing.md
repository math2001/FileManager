You want to contribute to this package? Great!

If you want to contribute to the documentation, you're at the right place.
Otherwise, you should have a look [in the readme][0]

First, you need to fork this repo.

### The doc with... MkDoc

I'm using mkdoc to build the documentation. Here's how you can get going:

```sh
$ git clone <your_fork>
$ cd FileManager
$ virtualenv venv
$ source venv/bin/activate  # Windows: .\venv\Scripts\activate.bat
$ pip install -r requirements.txt
```

> I don't have pip!

Quickly, pip is a package manager for python. You can install it by saving this
script: [get-pip.py][get-pip] and running it like so

```sh
python get-pip.py
```

> I don't have virtualenv!

Well, you install it by using `pip` like so:

```sh
pip install virtualenv
```


Once you have this installed, you have access to the command `mkdocs`.

Now, you need to create a new branch, with the "name" of what your adding. For
example:

```sh
git checkout -b improve-fm-create-explanation
```

Make your changes. You can preview them in your browser by running:

```sh
mkdocs serve
```

Now, commit your changes, and push them. In this case, it'd be:

```sh
git push origin improve-fm-create-explanation
```

And then, just send a pull request :wink:

[0]: https://github.com/math2001/FileManager#contributing
[1]: http://www.mkdocs.org/#installation
[get-pip]: https://bootstrap.pypa.io/get-pip.py
