# HackMIT-Flask

## Running the Flask Application

To run the flask app, open the command prompt and navigate to the folder that holds the full application. Ensure that you have virtualenv installed on your computer using [these instructions](http://flask.pocoo.org/docs/0.11/installation/#installation).

In the command line, enter the following code to activate the virtual environment:

    $ venv\scripts\activate

If you're using a Mac, you'll need to use the following code:

    $ venv/bin/activate

Now, enter the following code to run the flask app:


    $ set FLASK_APP=main.py
    $ flask run
        * Running on http://127.0.0.1:5000/

*If you are using a Mac or Linux, you'll need to use 'export' instead of 'set'*

Now, just head over to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to view the running application.