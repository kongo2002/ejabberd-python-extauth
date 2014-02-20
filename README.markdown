# ejabberd-python-extauth

*ejabberd-python-extauth* is a simple python script to be used for external
authentication in [ejabberd][ejabberd]. The script can be used to authenticate
against a JSON API that processes the authentication requests of
[ejabberd][ejabberd].


## Requirements

* python < 3
* JSON API


## Usage

In order to use *ejabberd-python-extauth* you have to edit the
ejabberd configuration in your `ejabberd.cfg`:

``` erlang
{auth_method, external}.
{extauth_program, "python /path/to/auth.py http://base.url/auth/"}.
```


## Configuration

The authentication script accepts a few configuration arguments:

    $ ./auth.py -h
    usage: auth.py [-h] [-l LOG] [-d] [URL]

    ejabberd authentication script

    positional arguments:
      URL                base URL (default: http://localhost:8000/auth/)

    optional arguments:
      -h, --help         show this help message and exit
      -l LOG, --log LOG  log directory (default: /var/log/ejabberd)
      -d, --debug        toggle debug mode


[ejabberd]: http://ejabberd.im/
