Updating the documentation
========

For simple changes, commit and push the code to github. You can actually edit and preview changes directly in github!
The changes will be uploaded to readthedocs automatically through webHooks.

For more complex changes where you want to see the resulting html before you commit:

1. Run::

    pip install sphinx

2. Make the updates you want to the .rst files, and then run::

    make html

3. Open the index.html file in the browser to see the result.
