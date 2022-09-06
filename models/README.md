# Models package

## How to use flask migrate
Declare where the flask app is with `FLASK_APP=_flask_app:app` and then use the flask migrate CLI.

```sh
FLASK_APP=_flask_app:app
flask db current
flask db migrate -m "Revision message"
flask db upgrade
```
