from flask import flask, render_template

app= flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ medarbejder')
def medarbejder():
    return render_template('medarbejder.html')

@app.route('/vagtplan')
def vagtskema():
    return render_template('vagtskema.html')

@app.route('/beskeder')
def beskeder():
    return render_template('beskeder.html')

@app.route('/dine-oplysninger')
def dine_oplysninger ():
     return render_template('dineoplysninger.html')

@app.route('/inventar')
def inventar():
    return render_template('inventar.html')

if __name__ == '__main__':
    app.run(debug=True)