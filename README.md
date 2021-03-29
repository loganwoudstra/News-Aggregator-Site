# News-Aggregator-Web-App 
A site where you can access all your favourite news outlets in one place

## How to install this app on your computer
### 1. Clone this repository
Change the current working directory to the location where you want the cloned directory.
```terminal
$ git clone https://github.com/loganwoudstra/News-Aggregator-Web-App.git 
```

### 2. Install the requirement.txt on your computer using pip

```python
pip install -r requirements.txt
```

### 3. Make migrations
```python
python manage.py makemigrations
python manage.py migrate
```

### 4. Run the server
```python
python manage.py runserver
```

## Built With
* [Django](https://www.djangoproject.com/) - The web framework used
