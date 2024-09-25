from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/order": {"origins": "*"}, r"/get_menu": {"origins": "*"}})

# Firebase Admin SDK

cred = credentials.Certificate("canteeno-6136-firebase-adminsdk-vqhdg-75f15bcdbb.json")
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

if __name__ == '__main__':
    app.run(port=5001)
