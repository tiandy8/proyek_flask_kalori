from flask import Flask, render_template, request;
app = Flask(__name__)
@app.route('/')
def hello_world():
    username = "calora"
    homepage_title = "dynamic homepage"
    return render_template('index.html', user=username, title=homepage_title)


@app.route('/submit', methods=['GET','POST'])
def submit():
    username = None
    if request.method == 'POST':
        username = request.form['username_input']
        print(f"Received username: {username}")
    return render_template('submit.html',name_sent=username)
    
if __name__ == '__main__':
    app.run(debug=True) 