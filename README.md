# Databaes

---

We acknowledge the use of ChatGPT(chat.openai.com) to draft, create sample code, debug, and assist us in learning our 
technology stack. The output from this tool was modified to fit our project requirements.
---
# Git Policy
###### Branching strategy:

There should be four ‘types’ of branches: <br>
A `master` branch, development branch, features branches and bugfix branches. The master branch should always
be deployable and contain code that is stable.

The development branch (named `develop`) should be used for integrating features and preparing for the next release -
this is the staging area before merging to the main branch.

For the `feature` branches, there should be a separate branch for each feature (e.g. named `feature/user-login`). 
It is encouraged to merge working code in to the `develop` branch, allowing for smaller increments of progress.

For `bugfix` branches, this should be branches off the development branch, (e.g. named `bugfix/user-login-fix`).

###### Committing:

Each commit should represent a single, necessary change or addition, and should be tested locally before committing to
ensure the change works as intended. Large commits should be avoided, as included changes may be difficult to
review/manage. On the other hand, commiting trivial, minor changes should also be avoided, as the commit/change history
should be meaningful and readable. Additionally, each commit should be accompanied by a concise but sufficiently
descriptive of the changes that were made, allowing for to understand the purpose and context for each change. The
structure should take the following form: Change made, and the improvement. For example, ‘Fixed broken user login, now
correctly validated password’.


###### Pulling/Merging:

Pulling should always be done before working on any changes, to ensure changes in the remote repository are synced in
the local repository. If any merge conflicts arise, they should be resolved as they’re noticed, and the branching
strategy (above) should be adhered to better ensure that code is stable and deployable. Depending on the conflict,
the appropriate steps to resolve them may vary.

---

### Hosting Flask Application Locally
[Flask Installation](https://flask.palletsprojects.com/en/3.0.x/installation/)<br>
[Flask Quickstart](https://flask.palletsprojects.com/en/3.0.x/quickstart/)

Create a virtual environment: 
1. In terminal run `py -3 -m venv .venv` <br>
This should create a `venv` folder in your local repository
2. Activate the environment `.venv\Scripts\activate`
3. Install Flask `pip install flask flask_sqlalchemy`
4. Use `pip show flask flask_sqlalchemy` to check if installed
5. Start the flask application using `flask --app src.app run`
   1. Running `flask --app src.app run --debug` gets flask to refresh the app when changes occur

---
# Google Coding Style Guides
 - [Python](https://google.github.io/styleguide/pyguide.html)
 - [HTML/CSS](https://google.github.io/styleguide/htmlcssguide.html)
 - [JavaScript](https://google.github.io/styleguide/jsguide.html)