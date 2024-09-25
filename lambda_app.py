from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/order": {"origins": "*"}, r"/get_menu": {"origins": "*"}})

# Firebase Admin SDK
cred = credentials.Certificate('canteeno-6136-firebase-adminsdk-vqhdg-23230b274a.json') 
firebase_admin.initialize_app(cred)
db = firestore.client()

# Route to fetch menu
@app.route('/get_menu', methods=['GET'])
def get_menu():
    try:
        menu_items = []
        docs = db.collection('menu').stream()
        for doc in docs:
            menu_items.append(doc.to_dict())
        return jsonify(menu_items), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to handle order placement
@app.route('/order', methods=['POST'])
def place_order():
    try:
        data = request.get_json()  # Retrieve order data from request
        if not data:
            return jsonify({'error': 'Invalid order data'}), 400

        # Extract items and total from data
        items = data.get('items')
        total = data.get('total')

        if not items or total is None:
            return jsonify({'error': 'Missing order details'}), 400
        
        import random
        user_id = f"uid{random.randint(100,1000)}"
        # Add order to Firestore
        db.collection('orders').add({
            'userId': user_id,
            'product_items': items,
            'total': total,
            'timestamp': datetime.now()
        })

        return jsonify({'status': 'Order placed successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# # Endpoint to get menu
# @app.route('/get_menu', methods=['GET'])
# def get_menu():
#     menu_ref = db.collection('menu')
#     docs = menu_ref.stream()
#     menu_items = []
#     for doc in docs:
#         menu_items.append(doc.to_dict())
#     return jsonify(menu_items)

# # Endpoint to place an order
# @app.route('/place_order', methods=['POST'])
# def place_order():
#     data = request.get_json()
#     product_id = data.get('productId')

#     # Fetch the product details
#     product_ref = db.collection('menu').document(product_id)
#     product = product_ref.get().to_dict()

#     # You can store orders in Firestore under an 'orders' collection
#     order_ref = db.collection('orders').add({
#         'userId': product_id,
#         'items': data['product_items'],
#         'total': data['total'],
#         'timestamp': datetime.now()
#     })
#     return jsonify({"message": f"Order for {product['name']} has been placed!"})

if __name__ == '__main__':
    app.run()
