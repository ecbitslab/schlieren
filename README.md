# Installation

Important prerequisites that should be installed in advance:
* Numpy and Scipy
  * Both source and binary distributions available for various platforms.
  * The [Anaconda](http://continuum.io/downloads) distribution is a good 'just works' option.
* OpenCV
  * Used for its mulitplatform support for video capture.
  * Tends to be difficult to install from source; binary distributions recommended.

Installation of additional required packages is handled automatically
by `setuptools`.

Additional development of the Schlieren code should be "sandboxed"
using the utility `virtualenvwrapper`.

```
$ mkvirtualenv schlieren-sandbox
$ toggleglobalsitepackages
$ git clone git@github.com:ecbitslab/schlieren.git
$ cd schlieren/python2.7 && python setup.py install
```

# Execution

Running `setup.py` will add the executable `schlieren-cmd` to the path.

```
$ schlieren-cmd --help
```
