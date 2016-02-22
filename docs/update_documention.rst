Updating the documentation
========

Simply commit and push the code to github. You can actually edit and preview changes directly in github!
The changes will be uploaded to readthedocs automatically through webHooks.



If you want to see the resulting html before you commit (usually you don't need to):

1. Run::

    pip install sphinx

2. Make the updates you want to the .rst files, and then run::

    make html

3. Open the index.html file in the browser to see the result.
