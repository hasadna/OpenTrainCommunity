Updating the documentation
========

The build the docs, you'll need ``sphinx``. Run::

    pip install sphinx

Find the Spinx documentation here: http://www.sphinx-doc.org/en/stable/contents.html
Update the documentation in with the .rst files, and then run::

    make html

Open the index.html file in the browser to see the result.

When you are done making changes, simply commit and push your code, and the changes will be uploaded to the site automatically
(through webHooks)
