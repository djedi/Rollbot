About
=====
This is a simple python script that uses twisted & BeautifulSoup to connect to
an IRC channel and monitor for pasted links. Once it finds a link it will
attempt to get the page title. If it can't find the page title (an image for
example) it will report the mimetype.

Install dependencies::

    pip install -r requirements.txt


Usage::

    python rollbot.py channel_name
