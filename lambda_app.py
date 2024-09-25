from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/order": {"origins": "*"}, r"/get_menu": {"origins": "*"}})

cred_file = {
  "type": "service_account",
  "project_id": "canteeno-6136",
  "private_key_id": "75f15bcdbb295abb9267d8265eda79dff93c334f",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDTlO3whMPU+41s\nfeiE77ex8zzSNaSbm1YzhiWJzYwGTTUc+LzWpWyyr/9TOuKTrHdvECNOEwH7crzi\naNOjsILvEG8Th+UUvtWxNQmYjUdj7j865l3pP40P5IbklkWA1cK4RDBM7QAJlFlc\nYTPUTS6MwqPtvE2lrFEEAhnMzpGajBciMntGf40ve/lcxD5vaMX4YmOJ3pf/hqSr\nmy9x131iUqQpz0oEPCDS86/+5kqeBVR0maI2Fzpa/B1EFkI3+l8LAk2p6AeC/Kv0\nMF5Ji1zr91NSH4Np2H66go9E3qWAXibzFluGXqutIET89hgUDB1Xnu+ceFogWcXG\nJTpzE5TjAgMBAAECggEABFUiYjB1yiC0jqotXruB6XTvo+ZRTpZpt3hhwGajHWXr\nVoKJa2PLzATql4u3JAr+DxonfuvIuJtq3sACxXFR3Q9bFu1LdZdKzOwnHCaYdaVl\nShF5jtMsUkz9riSdm7vE1v0eeBTKUWfmRIwBAbHq6Br8PFwEwwW6Svi4CoeYV6/J\nKGi5PbLnqRtoux8ZLlAA8IDXbBN1Xfc0Ta9ASLvQbVAt5mDJKMoiZFOnI4zGVa/J\nFObAnsUFwZRzkVFzm9eZ+1vK8+41z3vkqUivsQGw1FjC6qhetcikhJXiAFiRJO5j\nhi2JnGpzM1oVlo9pfg+GO4qQVRULZX9ib7IMnyadQQKBgQDvhldcIyMQQreSjaqV\nSSZeFmK+Z7H8IY4eoS8pnvebQ8JQwOoHLynkEOx5bFS2IISAovLYGN0GTH8eQ49J\nA9Gu7CX6U2nii/rG4OsJ2nV1Rtd4ler/XUQS9hZ3LzZLQHrxXW9awZtTy5yIZ4Sw\n0nGXb6PBmm5s/INCH7T4bOyHMQKBgQDiIo4fDrs6KBSNPcYM1q1fxjB+bMjBv1cW\n2Up0d6woGqIGni105Hd/DfEv23SbRQPsfJqsELSSLVoPEeH63VKwUaVTxay9P+8s\nMeq5Nr0KvNtSQwSQnCehU8wgDYmL8WIrLOnPLg0Mwl3Jbrf5eqM9+iRocrTBixS2\n8wgK2y/AUwKBgCwLRPchUupDimP9fteSquZ0MVYX1Ueql+qT8wsxOxCm5g1ZW+9U\nQdy5K/Kr8+vFkPfifsszzzjASkOzYp6ngCAtNlKQkhDhcoytgSq/rAeTrj1zO9IX\nQVRHQhxKZy5xPeoyJy7GGRzQfQksF98340FYewE3t4R87lnzYKCpztiRAoGAHNwk\nHzqWEnoDBXOYzxKm1c5JahkgFfoBd10L74lGY2fivc16J6zwwzpYSa9MVnScZ5YP\nd146bV10XO//UzDj2LTS0LotrYl3UMCeID0oKzKnGvyKnJoRRLmZF44iu8V2rePx\ngwtxhutXZNnIiQJpywMdmmbpQropTp/9qsUGdxkCgYAqBNO9M8JJrUn7EEmuhLzZ\nINtsb/8ArCQMnozF1XzPERcmx8aPT1CaF5nkdZC9sZCsxrHNGzeXnvmhE6102es8\nl49ajZ8HV9TzoRBebgblY5fu0iuOYqkdUArGpaHLG/zATz+HB9MiLwpxdUQ6ljX2\ngYRzAlLYRPafJ3hwdoI7bA==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-vqhdg@canteeno-6136.iam.gserviceaccount.com",
  "client_id": "112228737985549931277",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-vqhdg%40canteeno-6136.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Firebase Admin SDK
cred = credentials.Certificate(cred_file) 
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
