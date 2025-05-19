from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        dbname='postgres',  
        user='JONAS',       
        password='KeaPasword2011',  
        host='tambayanpostgresql.postgres.database.azure.com',  
        port='5432',        
        sslmode='require'
    )
    return conn

# Route for home/index page
@app.route('/')
def index():
    return render_template('index.html')


# Route for inventory page
@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Ingredients;')
    ingredients = cur.fetchall()
    cur.close()
    conn.close()
    
    ingredient_status = []
    for ingredient in ingredients:
        if ingredient[2] < ingredient[5]:  # quantity < threshold
            status = 'red'
        else:
            status = 'green'
        ingredient_status.append({
            'id': ingredient[0],
            'name': ingredient[1],
            'quantity': ingredient[2],
            'unit': ingredient[3],
            'threshold': ingredient[5],
            'status': status
        })
    
    return render_template('inventory.html', ingredients=ingredient_status)

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

def get_employees():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name || ' ' || last_name, job_title FROM employees ORDER BY first_name;")
    employees = cur.fetchall()
    conn.close()
    return employees



# Route for adding quantity to ingredients
@app.route('/add_quantity/<int:ingredient_id>', methods=['POST'])
def add_quantity(ingredient_id):
    quantity_to_add = float(request.form['amount'])
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE Ingredients SET Quantity = Quantity + %s WHERE IngredientID = %s', (quantity_to_add, ingredient_id))
    conn.commit()
    cur.close()
    conn.close()
    flash('Quantity added successfully!')
    return redirect(url_for('inventory'))

# Route for deducting quantity from ingredients
@app.route('/deduct_quantity/<int:ingredient_id>', methods=['POST'])
def deduct_quantity(ingredient_id):
    quantity_to_deduct = float(request.form['amount'])
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE Ingredients SET Quantity = Quantity - %s WHERE IngredientID = %s', (quantity_to_deduct, ingredient_id))
    conn.commit()
    cur.close()
    conn.close()
    flash('Quantity deducted successfully!')
    return redirect(url_for('inventory'))

# Route for displaying dishes to remove
@app.route('/remove', methods=['GET', 'POST'])
def remove():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM Menu;')
    dishes = cur.fetchall()
    
    if request.method == 'POST':
        selected_dishes = request.form.getlist('dishes')
        quantity_to_deduct = int(request.form['quantity'])
        
        for dish_id in selected_dishes:
            cur.execute('''SELECT mi.IngredientID, mi.QuantityNeeded, mi.Unit
                           FROM MenuIngredients mi WHERE mi.MenuID = %s;''', (dish_id,))
            ingredients_needed = cur.fetchall()
            
            for ingredient in ingredients_needed:
                ingredient_id, quantity_needed, unit = ingredient
                cur.execute('''UPDATE Ingredients
                               SET Quantity = Quantity - %s
                               WHERE IngredientID = %s;''', (quantity_needed * quantity_to_deduct, ingredient_id))
        
        conn.commit()
        cur.close()
        conn.close()
        flash("Deduction successful!")
        return redirect(url_for('remove'))
    
    cur.close()
    conn.close()
    return render_template('remove.html', dishes=dishes)

# Other routes
@app.route('/medarbejder')
def medarbejder():
    return render_template('medarbejder.html')


@app.route('/Beskeder')
def beskeder():
    return render_template('beskeder.html')

@app.route('/Dine_oplysninger')
def dine_oplysninger():
    return render_template('dine_oplysninger.html')

if __name__ == '__main__':
    app.run(debug=True)
