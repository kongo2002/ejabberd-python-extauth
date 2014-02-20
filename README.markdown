# ejabberd-python-extauth

*ejabberd-python-extauth* is a simple python script to be used for external
authentication in [ejabberd][ejabberd]. The script can be used to authenticate
against a JSON API that processes the authentication requests of
[ejabberd][ejabberd].

The script probably cannot be used *as-it-is* but may serve as a starting point
if you intent to create your own external authentication script for
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


## JSON API

The examplary JSON API used in the script expects the following API endpoints.
As described earlier the JSON calls are supposed to be an example for your own
API.


### Authenticate

    POST BASE_URL/login

``` json
{ "username": "user@domain", "password": "***" }
```


### User exists

    POST BASE_URL/exists

``` json
{ "username": "user@domain" }
```


[ejabberd]: http://ejabberd.im/
