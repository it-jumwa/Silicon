# Databaes

---  

We acknowledge the use of ChatGPT ([chat.openai.com](https://chat.openai.com)) to draft, create sample code, debug
and assist in the learning of our technology stack. The output from this tool was modified to fit our needs.
---  

# Git Policy

## Branching strategy:

This branching strategy aims to be flexible and maintain stability, consisting of core branches while allowing for
additional types (e.g. refactoring, bugfix)

There are three core branch types:

**Main branch:** Always deployable and contains stable code

**Development branch (`develop`):** Used for integrating features and preparing for the next release, serving as the
staging area before merging into the main branch

**Feature branches:** A separate branch is created for each feature (e.g., feature/user-login) <br>  

Regularly merge working code into develop for smaller, incremental progress

## Committing:

**Atomic Commits:** Each commit should represent a single, necessary change or addition <br>

**Avoid Large Commits:** Keep commits manageable and easy to review<br>

**Avoid Trivial Commits:** Each commit should add meaningful value<br>

**Clear Commit Messages:** Each commit message should be clear, concise and formatted as follows: <br>  
&nbsp;&nbsp;&nbsp;&nbsp;**Title:** A short summary of the change (written in sentence case) <br>  
&nbsp;&nbsp;&nbsp;&nbsp;**Body:** A detailed list of the changes or improvements made (if necessary)

```  
Updated card view and button styling  
  
 - Added margin to toggle view buttons
 - Adjusted background colour of task cards
 - Added border radius to kanban board  
```

## Pulling/Merging:

- Pull before working to ensure your local repository is up-to-date with remote changes
- Resolve merge conflicts immediately to maintain code stability and follow the branching strategy

---  

# Hosting Flask Application Locally

[Flask Installation](https://flask.palletsprojects.com/en/3.0.x/installation/)<br>  
[Flask Quickstart](https://flask.palletsprojects.com/en/3.0.x/quickstart/)

1. Create a virtual environment:

```bash  
py -3 -m venv .venv
```  

This will create a new `venv` folder in your local repository

2. Activate the environment

```bash  
.venv\Scripts\activate  
```  

3. Install Flask and Flask-SQLAlchemy

```bash  
pip install flask flask_sqlalchemy
```  

4. Verify Installation

```bash  
pip show flask flask_sqlalchemy
```

5. Start the flask application

```bash  
flask --app src.app run --debug
```

  
---  

# Google Coding Style Guides

- [Python](https://google.github.io/styleguide/pyguide.html)
- [HTML/CSS](https://google.github.io/styleguide/htmlcssguide.html)
- [JavaScript](https://google.github.io/styleguide/jsguide.html)