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

def encrypt_message(public_key, plaintext):
    public_key = serialization.load_pem_public_key(public_key, backend=None)


    ciphertext = public_key.encrypt(
        plaintext,
        pd.OAEP(
            mgf=pd.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def generate_aes_key(passphrase, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,
        salt=salt,
        length=32,  # 256 bits
        backend=default_backend()
    )
    key = kdf.derive(passphrase)
    return key

def encrypt_message2(aes_key, plaintext):
    iv = os.urandom(16)  # Generate a random IV (Initialization Vector)
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return iv + ciphertext

def decrypt_message2(aes_key, ciphertext):
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_plaintext

def base64_public_key(base64_encoded):
    base64_encoded=base64_encoded.encode()
    decoded_data = base64.b64decode(base64_encoded)
    public_key = serialization.load_pem_public_key(decoded_data, backend=default_backend())
    pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)
    print(pem_public_key.decode())
    return pem_public_key

def main_encrypt(plaintext,public_key):
    public_key=base64_public_key(public_key)
    passphrase = b"viywiegfIGGEWGYGBDHBHJVfew"
    salt = os.urandom(16)
    key = generate_aes_key(passphrase, salt)
    ciphertext = encrypt_message2(key, plaintext)
    as_en_ciphertext = encrypt_message(public_key, key)
    print("Ciphertext:", ciphertext)
    print("Ciphertext:", as_en_ciphertext)
    return ciphertext, as_en_ciphertext


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

import os

def file_help(file_path):
  directory_path = os.path.dirname(file_path)
  file_name_with_extension = os.path.basename(file_path)
  file_name, file_extension = os.path.splitext(file_name_with_extension)

  print("Directory Path:", directory_path)
  print("File Name:", file_name)
  print("File Extension:", file_extension)
  return directory_path,file_extension,file_name


def upload_file(file_path):
  import os
  import requests
  api_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDA4YjM2QThBMDk4NDA3Y0U0QTI0OTVlMEE5NzYzYjE1MDk5ODlFNTYiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2OTE3NzE5MjcxMDksIm5hbWUiOiJmaWxlX3NoYXJlIn0.ljp6uNn1r3YmRtMC0sHjWjrVhMDYRaEQUH8oUEJzStQ"
  upload_url = "https://api.web3.storage/upload"



  headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
  with open(file_path, 'rb') as file:
        file_content = file.read()

  response = requests.post(upload_url, headers=headers, data=file_content)

  if response.status_code == 200:
        print("File uploaded successfully!")
        print("CID:", response.json()["cid"])
        return response.json()["cid"]
  else:
        print("Failed to upload file.")
        return None

def encrypt_upload(file,pub_key):
      a=read_data_from_a_file(file)
      key,d=main_encrypt(a,pub_key)
      d1,get_extension,_=file_help(file)
      file_name='encrypted'+str(get_extension)
      file_path = os.path.join(d1, file_name)
      write_file(file_path,d)
      cidf=upload_file(file_path)
      file_name='key'
      file_path = os.path.join(d1,file_name)
      write_file(file_path,key)
      cidf=cidf+'_'+str(upload_file(file_path))
      return cidf
# base64_encoded='LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUE1dHdSODNwZ25hemgvOWRjZ01hcgpZVHdiZkplamVZWkNUNkM0ejNtUFE0UW03d1JJZkM1amNZYlRxeG5VUHY3VFM4ajhiRHh0VWNUbFR0RG5rd0hkCjJMRW1ySTdycHVBZnRFUnZnQjBLYjYwdFVWY24vOHBlZjhRc2RUaGVNeG5xQWx6eVRIRWNHR3MzMGU3V1NuMnIKNXlWMis3dlkzcTFOZENUQ3dHbEhOL2o1K2hmeTRDQ21PZENyNGtoU2dXcUt2aUdEb0VkKzBvOWcwaDF0WmplYgoyZi9LMWUydWlqWXpjZGRWQlp4U3YycFF4RlRSR25mbWpsU3Z3d3JOMFcxTDVtOVUwdXRXZnoybFVBQ1M4L0tzCjJzL2hvMDViQ0w0aHNTNm1XcUlycjBjMitXN0llaUFNV3hhV09uRmxIV2dvMHBwTm5xS05rTFFLcXorbWZvRksKaVFJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=='
# x=encrypt_upload('./content/Mask group.png',base64_encoded)

# print(x)
