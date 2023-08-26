import time
# from time import time
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
from pprint import pprint

class Blockchain():
    def __init__(self):
        self.chain = []
        self.__secret = ''
        self.__difficulty = 4 
        self.nodes = set()
        self.clients = {}

    def create_block(self, sender:str, receiver:str,information:str):
        block = {
            'index': len(self.chain),
            'sender': sender,
            'receiver': receiver,
            'timestamp': str(time.strftime("%d %B %Y , %I:%M:%S %p", time.localtime())),  # d-date, B-Month, Y-Year ,I-Hours in 12hr format, M-Minutes, S-secnods, p-A.M or P.M,
            'file_unique_id': information
        }

        block['previous_hash'] = self.chain[-1]['hash']
        i = 0
        while True:
            block['nonce'] = i
            _hash = hashlib.sha256(str(block).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                block['hash'] = _hash
                break
            i+=1
        self.chain.append(block)
    def validate_blockchain(self, chain):
        valid = True
        n = len(chain)-1
        i = 0
        while(i<n):
            if(chain[i]['hash'] != chain[i+1]['previous_hash']):
                valid = False
                break
            i+=1
        if valid: 
            print('The blockchain is valid...')
            return valid
        else: 
            print('The blockchain is not valid...')
            return valid
