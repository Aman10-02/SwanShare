from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as pd
from cryptography.hazmat.primitives import asymmetric
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
import base64
import os
import requests

def download(x):
  ric=x.split('_')
  print(ric)
  for i in range(0,2):
    cid = ric[i]

    ipfs_gateway_url = f'https://ipfs.io/ipfs/{cid}'


    response = requests.get(ipfs_gateway_url)

    if response.status_code == 200:

      with open('downloaded_file'+str(i), 'wb') as file:
          file.write(response.content)
      print("File downloaded successfully!")
    else:
      print("File download failed.")
      print("Response:", response.text)


def decrypt_message(private_key_filename, ciphertext):

    with open(private_key_filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=None
        )

    print(private_key)
    plaintext = private_key.decrypt(
        ciphertext,
        pd.OAEP(
            mgf=pd.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext


def decrypt_message2(aes_key, ciphertext):
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_plaintext


def read_data_from_a_file(file_path):
  try:
      with open(file_path, 'rb') as file:
          binary_data = file.read()
      return binary_data

  except FileNotFoundError:
      print("File not found.")
  except Exception as e:
      print("An error occurred:", e)

def write_file(file_path,d):

  try:
      with open(file_path, 'wb') as file:
        file.write(d)
  except FileNotFoundError:
      print("File not found.")
  except Exception as e:
      print("An error occurred:", e)

def detect_file_type(binary_data):
    magic_numbers = {
        b'\x74\x65\x78\x74': 'TXT',
        b'\x89PNG': 'PNG',
        b'\xff\xd8\xff': 'JPEG',
        b'%PDF': 'PDF',
        b'\xFF\xD8\xFF\xE0': 'JPEG',
        b'\xFF\xD8\xFF\xE1': 'JPEG',
    }

    magic = binary_data[:8]

    for signature, file_type in magic_numbers.items():
        if magic.startswith(signature):
            return file_type

    return 'Unknown'

def main_decrypt(x):
  download(x)
  d1=read_data_from_a_file('./downloaded_file0')
  print(d1)
  key=decrypt_message('./private_key.pem',d1)
  print(key)
  d2=read_data_from_a_file('./downloaded_file1')
  final=decrypt_message2(key, d2)
  magicnumber=detect_file_type(final)
  write_file('./downloads/'+ x +'.'+str(magicnumber.lower()),final)

# x='bafkreiaqtfuqcyz3snvclsav2zzvbckpynbxyqmmjymxkd2c4zr6p4nihi_bafkreih5p6pflfwpdigoytglt6ll3bd7oe2qqm5fs5kou7ybx7qknt7md4'
# main_decrypt(x)