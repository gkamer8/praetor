# Data-Explore

This section of the repo contains a reasonably self-contained Flask app for exploring datasets.

## Layout

The project is lightweight and based on the Flask tutorial project to make things simple.

## Run

First you should have a venv setup with the correct requirements, activated using `source venv/bin/activate`.

You can run the development server from this directory using:

```
flask --app app run --debug
```

If you need to initialize the database, you can use:

```
flask --app app init-db
```
