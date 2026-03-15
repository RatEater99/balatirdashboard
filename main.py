from app import app
from layout import create_layout
import callbacks  # importing registers all callbacks

app.index_string = open("index.html").read()
app.layout = create_layout()
server = app.server

if __name__ == "__main__":
    app.run(debug=False)