from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import boto3
import os

app = Flask(__name__)

# Email setup
sender_email = 'Cryptowatcher2023@gmail.com'
app_key = 'ktvtnuazhwoxruvl'

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_key)
    server.send_message(msg)
    server.quit()

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    cryptos = request.form.getlist('cryptos')
    if not email or not cryptos:
        return "Missing required fields", 400

    subject = "Crypto Price Updates Subscription"
    body = f"You have subscribed to updates for: {', '.join(cryptos)}"
    
    # Store user data in DynamoDB (or any other database)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CryptoWatcherSubscribers')
    table.put_item(
        Item={
            'email': email,
            'cryptos': cryptos
        }
    )

    send_email(email, subject, body)
    return "Subscription successful!", 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return "Missing email field", 400

    # Remove user data from DynamoDB (or any other database)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CryptoWatcherSubscribers')
    response = table.delete_item(
        Key={
            'email': email
        }
    )

    subject = "Crypto Price Updates Unsubscription"
    body = "You have been unsubscribed from crypto price updates."
    send_email(email, subject, body)
    return "Unsubscription successful!", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
