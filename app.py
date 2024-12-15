from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import pymongo


import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# ------------------ database and collectios ---------------------- #

myclient = pymongo.MongoClient("mongodb+srv://abhi:1maratha@cluster0.frc7h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = myclient["themagicstore"]
collection_user = db["customers"]
collection_products = db["products"]
collection_seller = db["sellers"]
collection_cart = db["cart"]


# ------------------------ cloudinary cloud ------------------------ #
cloudinary.config( 
    cloud_name = "dql90uw2x", 
    api_key = "272696395322952", 
    api_secret = "9UBaqXBLiAikOSFlK55cXKNAsAw",
    secure=True
)

# --------------------------- routes ------------------------------ #
@app.route('/')
def index():
    products = collection_products.find({"category": "Fashion"}).sort("_id",-1)
    books = collection_products.aggregate([{ "$match": {"category": "Books"} },{ "$sample": { "size": 1000 } }])
    electronics = collection_products.aggregate([{ "$match": {"category": "Electronics"} },{ "$sample": { "size": 1000 } }])

    return render_template('index.html', products=products, books=books, electronics=electronics, email=session.get('email'), semail=session.get("semail"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        address = {}
        
        collection_user.insert_one({"name": name, "email": email, "password": password, "address": address})
        
        print("New User Registered Successfully")
        print("Name: ", name)

        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)

        session['name'] = name
        session['email'] = email
        session['password'] = password

        return redirect(url_for('login'))
       
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        

        user = collection_user.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=24)
            session['email'] = email
            session.pop('semail', None)

            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to index route
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/profile')
def profile():
    email =session.get('email')
    semail =session.get('semail')

    if email:
        user = collection_user.find_one({'email': email})
        
        
        email = user['email']
        name=user['name']
        password=user['password']
        address = user["address"]

        return render_template('profile.html', email=email, name=name, password=password, user = user)
    
    if semail:
        seller = collection_seller.find_one({'email': semail})
        
        email = seller['email']
        name=seller['name']
        password=seller['password']
        saddress = seller["address"]

        return render_template('profile.html', email=email, name=name, password=password, seller = seller)

    return render_template('register.html', email=email, name=name, password=password)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    session.pop('semail', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/sellerregister', methods=['GET', 'POST'])
def sellerregister():
    if request.method == "POST":
        
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        address = {}

        
        collection_seller.insert_one({"name": name, "email": email, "password": password, "address":address})
        
        print("New seller Registered Successfully")
        print("Name: ", name)


        session['sname'] = name
        session['semail'] = email
        session['spassword'] = password

        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)

        return redirect("/sellerlogin")
       
    return render_template('sellerregister.html')


@app.route('/sellerlogin', methods=['GET', 'POST'])
def sellerlogin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        

        seller = collection_seller.find_one({'email': email})
        
        if seller and check_password_hash(seller['password'], password):
            
 
            session['semail'] = email
            session['spassword'] = password
            session.pop('email', None)
            
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=24)

            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to index route
        else:
            flash('Invalid email or password', 'error')

    return render_template('sellerlogin.html')


@app.route('/manageproduct', methods=["GET", "POST"])
def manageproduct():
    
    email = session.get('semail')
    seller = collection_seller.find_one({"email": email})
    name = seller['name']

    if request.method == "POST":
        productname = request.form["product_name"]
        productdescription = request.form["product_description"]
        productprice = request.form["product_price"]
        productcategory = request.form["product_category"]
        productsubcategory = request.form["product_subcategory"]
        
        productimage = request.files["product_image"]
        productimage2 = request.files["product_image2"]
        productimage3 = request.files["product_image3"]
        productimage4 = request.files["product_image4"]

        imgs =[productimage, productimage2, productimage3, productimage4]
        purllist = []

        for pimg in imgs:
            productimg = cloudinary.uploader.upload(pimg)
            productimgurl = productimg["secure_url"]
            purllist.append(productimgurl)
        



        collection_products.insert_one({"product_name": productname,
                                        "description": productdescription, 
                                        "price": int(productprice),
                                        "images": purllist,
                                        "category": productcategory,
                                        "seller_name": name,
                                        "subcategory": productsubcategory})

        return redirect('manageproduct')
    
    products = collection_products.find({"seller_name" : name}).sort("_id",-1)
    print(name)
    return render_template('manageproduct.html', products=products, email=session.get('semail'))
    


@app.route('/books')
def books():
    products = collection_products.aggregate([{ "$match": {"category": "Books"} },{ "$sample": { "size": 1000 } }])
    return render_template('books.html', products=products, email=session.get('email'), semail=session.get('semail'))


@app.route('/electronics')
def electronics():
    products = collection_products.aggregate([{ "$match": {"category": "Electronics"} },{ "$sample": { "size": 1000 } }])
    return render_template('electronics.html',products=products, email=session.get('email'), semail=session.get('semail'))


@app.route('/fashion')
def fashion():
    products = collection_products.aggregate([{ "$match": {"category": "Fashion"} },{ "$sample": { "size": 1000 } }])
    return render_template('fashion.html', products=products, email=session.get('email'), semail=session.get('semail'))


@app.route('/order/<id>',methods=["GET", "POST"])
def order(id):
    product = collection_products.find_one({"_id" : ObjectId(id)})
    email = session.get('email')
    user = collection_user.find_one({"email":email})
    print(product["_id"])

    if request.method == "POST":
        
        if product["category"] == "Fashion":
            psize = request.form["size"]
            psubcategory = product["subcategory"]
        else:
            psize = None
            psubcategory = None
        
        if email:
            collection_cart.insert_one({"product_name": product["product_name"],
                                        "description": product["description"], 
                                        "price": product["price"]*int(request.form["qty"]),
                                        "images": product["images"],
                                        "category": product["category"],
                                        "seller_name": product["seller_name"],
                                        "subcategory": psubcategory,
                                        "size":psize,
                                        "quantity":int(request.form["qty"]),
                                        "customername":user["name"]})
            return redirect(url_for("cart"))
        
        else:
            return redirect(url_for('register'))

    return render_template('order.html', email=session.get('email'),semail=session.get('semail'), product_id=id, product = product)



@app.route('/cart')
def cart():
    email = session.get('email')
    user = collection_user.find_one({"email":email})
    products = collection_cart.find({"customername": user["name"]})
    
    return render_template('cart.html', email=session.get('email'),semail=session.get('semail'), products = products)
    
@app.route('/remove_item', methods=['POST'])
def remove_item():
    data = request.get_json()
    item_id = data['id']
    result = collection_cart.delete_one({'_id': ObjectId(item_id)})
    return jsonify({'success': result.deleted_count > 0})


@app.route('/deliveryaddress')
def deliveryaddress():
    email = session.get('email')
    user = collection_user.find_one({'email': email})
    products = collection_cart.find({"customername": user["name"]})
    
    x = [i["price"] for i in collection_cart.find({"customername": user["name"]})]
    print(x)
    
    return render_template('deliveryaddress.html', products=products, email=session.get('email'), semail=session.get('semail'), user = user, total = sum(x))

@app.route('/addnewaddress',methods=["GET", "POST"])
def addnewaddress():
    if request.method == "POST":
        email = session.get('email')
        house = request.form["house"]
        street = request.form["street"]
        landmark = request.form["landmark"]
        pincode = request.form["pincode"]
        city = request.form["city"]
        phone = request.form["phone"]
        user = collection_user.find_one({'email': email})

        
        collection_user.update_one({"email": email}, {'$set': {"address.house" : house,
                                                           "address.street" : street,
                                                           "address.landmark" : landmark,
                                                           "address.pincode" : pincode,
                                                           "address.city" : city,
                                                           "phone" : phone }})
        return redirect("deliveryaddress")
        
    return render_template("addnewaddress.html")


if __name__ == '__main__':
    app.run(debug=True)
