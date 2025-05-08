from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        dbname='ResturantTambayan',  # Your database name
        user='postgres',             # Your database username
        password='kea123',           # Your database password
        host='localhost',            # Your database host
        port='5432'                  # Default PostgreSQL port
    )
    return conn

# Route for displaying inventory
@app.route('/')
def inventory():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Ingredients;')  # Query Ingredients table
    ingredients = cur.fetchall()
    cur.close()
    conn.close()
    
    # Check ingredient status (red for below threshold, green for above threshold)
    ingredient_status = []
    for ingredient in ingredients:
        if ingredient[2] < ingredient[5]:  # If quantity is less than threshold
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
    
    # Query all dishes from the menu
    cur.execute('SELECT * FROM Menu;')
    dishes = cur.fetchall()
    
    if request.method == 'POST':
        selected_dishes = request.form.getlist('dishes')  # Get selected dishes
        quantity_to_deduct = int(request.form['quantity'])  # Get quantity to deduct
        
        # Deduct ingredients used by selected dishes
        for dish_id in selected_dishes:
            cur.execute('''SELECT mi.IngredientID, mi.QuantityNeeded, mi.Unit
                           FROM MenuIngredients mi WHERE mi.MenuID = %s;''', (dish_id,))
            ingredients_needed = cur.fetchall()
            
            for ingredient in ingredients_needed:
                ingredient_id, quantity_needed, unit = ingredient
                # Deduct the quantity of the ingredient
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

if __name__ == '__main__':
    app.run(debug=True)
