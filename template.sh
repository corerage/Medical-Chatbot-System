mkdir -p src
mkdir -p etl
mkdir -p Notebook

#create files inside folders
touch src/__init__.py
touch etl/__init__.py
touch etl/etl.py
touch etl/transform.py
touch etl/load.py
touch src/helper.py
touch src/prompt.py
touch setup.py
touch README.md
touch requirements.txt
touch .gitignore
touch .env
touch app.py
touch Notebook/notebook.ipynb

echo "Project structure created successfully."