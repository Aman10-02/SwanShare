import os
import urllib.request
from my_constants import app
import time
import asyncio
import threading
import pyAesCrypt
from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit
# from "web3.storage" import Web3Storage
# from web3storage import Client
from public_private import generate_and_store_keys
from key_management import get_str_from_key
from upload_function import encrypt_upload
from download_function import main_decrypt
# from utils import send_offer_and_icecandidate, create_peer_connection
import socketio
import pickle
from blockchain import Blockchain
import requests

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCIceGatherer

# The package requests is used in the 'hash_user_file' and 'retrieve_from hash' functions to send http post requests.
# Notice that 'requests' is different than the package 'request'.
# 'request' package is used in the 'add_file' function for multiple actions.

myid = ''
my_key = ''
my_name = ''
sio = socketio.Client(logger = True,engineio_logger=True)
client_ip = app.config['ADDR']
connection_status = False

peer_connections = {}
blockchain = Blockchain()

async def replace_chain():
        network = blockchain.nodes
        print("network")
        longest_chain = None
        initial = len(blockchain.chain)
        response = requests.get(f'{app.config["SERVER_IP"]}/get_chain')
        
        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
            if length > initial and blockchain.validate_blockchain(chain):
                blockchain.chain = chain

        # def call_back(data):
        #         length = data.get('length')
        #         max_length = len(blockchain.chain)
        #         chain = data.get('chain')
        #         print("from ch",chain)
        #         if length > max_length and blockchain.validate_blockchain(chain):
        #             blockchain.chain = chain
        
        
        # for node in network:
        #     if node != myid :
        #         print("insidenode")
        #         await send_offer_and_icecandidate(node, call_back)

        if initial < len(blockchain.chain):
            return True
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# def append_file_extension(uploaded_file, file_path):
    file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
    user_file = open(file_path, 'a')
    user_file.write('\n' + file_extension)
    user_file.close()

# def decrypt_file(file_path, file_key):
#     encrypted_file = file_path + ".aes"
#     print("decr", encrypted_file)
#     os.rename(file_path, encrypted_file)
#     pyAesCrypt.decryptFile(encrypted_file, file_path,  file_key, app.config['BUFFER_SIZE'])

# def encrypt_file(file_path, file_key):
#     pyAesCrypt.encryptFile(file_path, file_path + ".aes",  file_key, app.config['BUFFER_SIZE'])

# def hash_user_file(user_file, file_key):
    encrypt_file(user_file, file_key)
    encrypted_file_path = user_file + ".aes"
    # client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    client = Client(api_key = app.config['KEY'] )
    response = client.upload_file(encrypted_file_path)
    file_hash = response['cid']
    return file_hash

# def retrieve_from_hash(file_hash, file_key):
    # client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    # client = Client(api_key= app.config['KEY'] )
    # # file_content = bytes.fromhex(file_hex)
    # client.download(file_hash)
    response = requests.get(f'https://{file_hash}.ipfs.dweb.link') # add error handelling
    file_content = response.content

    # print(file_content)
    file_path = os.path.join("./downloads",file_hash) 

    # print("file-content: ",file_content)

    user_file = open(file_path, 'wb')
    user_file.write(file_content)
    user_file.close()
    print("inside line 62", file_path)
    decrypt_file(file_path, file_key)
    print("inside line 64", file_path)
    with open(file_path, 'rb') as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
    user_file.close()
    file_extension = last_line
    saved_file = file_path + '.' + file_extension.decode()
    os.rename(file_path, saved_file)
    print("save-file",saved_file)
    return saved_file
    # return file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html' , message = "Welcome!")

@app.route('/download')
def download():
    return render_template('download.html' , message = "Welcome!")

@app.route('/add_file', methods=['POST'])
async def add_file():

    if request.method == 'POST':
        error_flag = True
        if 'file' not in request.files:
            message = 'No file part'
        else:
            user_file = request.files['file']
            receiver = request.form['receiver_name']
            receiver_key = ''
            if user_file.filename == '':
                message = 'No file selected for uploading'

            if receiver not in blockchain.clients:
                message = 'Invalid Receiver'
            else:
                receiver_key = blockchain.clients[receiver]

            if receiver_key and user_file and allowed_file(user_file.filename):
                error_flag = False
                filename = secure_filename(user_file.filename)
                # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_path = os.path.join("./uploads", filename)
                print(file_path)
                user_file.save(file_path)
                # append_file_extension(user_file, file_path)
                sender = request.form['sender_name']
                file_key = request.form['file_key']
                    
                try:
                    def cb(data) :
                        if data.get("flag") == False :
                            nonlocal error_flag, message
                            error_flag = True
                            message = 'Could not complete. Try again !!'
                    # hashed_output1 = hash_user_file(file_path, file_key)
                    hashed_output1 = encrypt_upload(file_path, receiver_key)
                    index = blockchain.create_block(my_name, receiver, hashed_output1)
                    sio.emit("set_chain", {"chain": blockchain.chain}, callback = cb )
                except Exception as err:
                    message = str(err)
                    error_flag = True
                    if "ConnectionError:" in message:
                        message = "Gateway down or bad Internet!"
                # message = f'File successfully uploaded'
                # message2 =  f'It will be added to Block {index-1}'
            else:
                error_flag = True
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'
    
        if error_flag == True:
            return render_template('upload.html' , message = message)
        else:
            return render_template('upload.html' , message = "File succesfully uploaded")

@app.route('/retrieve_file', methods=['POST'])
async def retrieve_file():

    if request.method == 'POST':

        error_flag = True

        if request.form['file_hash'] == '':
            message = 'No file hash entered.'
        elif request.form['file_key'] == '':
            message = 'No file key entered.'
        else:
            error_flag = False
            file_key = request.form['file_key']
            file_hash = request.form['file_hash']
            try:
                # file_path = retrieve_from_hash(file_hash, file_key)
                main_decrypt(file_hash)
            except Exception as err:
                message = str(err)
                error_flag = True
                if "ConnectionError:" in message:
                    message = "Gateway down or bad Internet!"

        if error_flag == True:
            return render_template('download.html' , message = message)
        else:
            return render_template('download.html' , message = "File successfully downloaded")

@sio.on("me")
def setme(data) :
    global myid
    myid = data["id"]
    print("id", myid)

@sio.on("connect")
def connect():
    print("Connected to signaling server")
    sio.emit("add_client", {"key" : my_key, "userName" : my_name})

@sio.on("disconnect")
def disconnect():
    print("disconnected from signaling server")



@sio.on("update_chain")
def update_chain(data):
    print("message", data)
    blockchain.chain = data.get("chain")

@sio.on("my_response")
def my_response(data):
    print("message", data)
    # print(pickle.loads(data['data']))
    blockchain.nodes = pickle.loads(data.get('nodes'))
    blockchain.clients = data.get('clients')

@sio.on("get_chain")
def get_chain(data):
    print("getChain")
    chain = blockchain.chain
    length = len(chain)
    response = {'chain': chain, 'length': length}
    return response

@app.route('/connect_blockchain')
async def connect_blockchain():
    global connection_status
    global my_key, my_name
    nodes = len(blockchain.nodes)

    if os.path.exists("./private_key.pem"):
        print("File exists!")
        with open('public.txt', 'r') as fl:
            my_key = fl.read()
        with open('username.txt', 'r') as nm:
            my_name = nm.read()
    else:
        generate_and_store_keys()
        my_key = get_str_from_key()
        my_name = str(int(time.time()))
        with open('username.txt', 'w') as userfile:
            userfile.write(my_name)
    if not connection_status:
        thread = threading.Thread(target= connect_socketio)
        thread.start()
    
    is_chain_replaced = await replace_chain()
    connection_status = True
    
    # Render the template immediately
    return render_template('connect_blockchain.html', messages={
        'message1': "Welcome to the services page",
        'message2': "Congratulations, you are now connected to the blockchain.",
    }, chain=blockchain.chain, nodes=nodes, userName = my_name)

def connect_socketio():
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    
    # loop.run_until_complete(
    sio.connect(app.config['SERVER_IP'])
        # )
    # loop.run_until_complete(
    sio.wait()
        # )
    # loop.close()

@app.route('/disconnect_blockchain')
async def disconnect_blockchain():
    global connection_status
    connection_status = False
    sio.disconnect()
    # await sio.wait()
    
    return render_template('index.html')


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    app.run(host = client_ip['Host'], port= client_ip['Port'], debug=True)
    # app.run(app.config['NODE_ADDR'], debug=True)