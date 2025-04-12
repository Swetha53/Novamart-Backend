# Steps to Deploy and Test the Application
## Pre-Requisites
1. Docker Daemon: https://www.docker.com/

## Setup
### [OPTIONAL] Certificate Creation
**Note: Keep the name of certificates as it is so that no configuration need to be changed and just the certificate needs to be swapped. Keep the password "novamart" for the same reason.**
1. Open command terminal 
2. Generate private key using the command
```
openssl genpkey -algorithm RSA -out ca.key -aes256
```
3. Generate root certificate
```
openssl req -key ca.key -new -x509 -out ca.crt -days 3650
```
4. Create a configuration file for the certificate named san.cnf using the following comman
```
nano san.cnf
```
5. Add the following lines into the file and change the alt_names to list the IP addresses and DNS names you need.
```
[req]
default_bits = 2048
default_keyfile = server.key
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
commonName = Common Name (e.g. server FQDN or YOUR name)

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = example.com
IP.1 = 192.168.1.1
IP.2 = 192.168.1.2
IP.3 = 192.168.1.3
```
6. Generate a private key and certificate signing request (CSR)
```
openssl genpkey -algorithm RSA -out server.key
openssl req -new -key server.key -out server.csr -config san.cnf
```
7. Self-sign the certificate
```
openssl x509 -req -in server.csr -signkey server.key -out server.crt -days 365 -extensions v3_req -extfile san.cnf
```
8. Now you have a server.crt (certificate) and server.key (private key)
9. Convert .crt and .key to .p12 for spring boot
```
openssl pkcs12 -export -in server.crt -inkey server.key -out keystore.p12 -name server -CAfile ca.crt -caname root
```
10. Add keystore.p12 in the resources folder of all the microservices except reality-service.
    - Delete keystorep12 folder if present
11. Add server.crt and server.key in the reality-service


### 1. Docker Deployment
The certificate is self-signed so that deployed web can hit secure api.
1. Check the IP v4 address of your system if it is 10.200.67.24 (University of Ottawa's) IP address then it should work as it is with no change to certificate else follow the below process to setup a new certificate for the microservice.
2. Do mvn clean install for all the services so that a target folder is built for each microservice.
3. Run the following command in the terminal of Novamart-backend
```
docker-compose up --build -d
```
4. Wait few minutes for all the services to be up and running.

### 2. Reality Service Deployment
1. Create a virtual environment (e.g. py311) and set python as 3.11.11 in the environment. You can use Anaconda Navigator to create a virtual environment with a specific python version.
2. Use the following command in your editor (e.g. IntelliJ) to activate virtual environment.
```
conda activate py311
```
3. Run the following command to install all the necessary packages.
```
pip install --no-cache-dir -r requirements.txt
```
4. Run the following command to start the reality service
```
uvicorn main:app --host 0.0.0.0 --port 8443 --ssl-keyfile server.key --ssl-certfile server.crt
```
5. Once the application has started open the frontend repository (Novamart).

### 3. FrontEnd Deployment
1. Change the IP_ADDRESS in api.js file to the system's IP_ADDRESS [Optional do it only if your system IP is different from University IP mentioned above], push the changes and deploy it using
```
npm run deploy
```
2. The page should be deployed in https://<github_username>.github.io/NovaMart/#/ (https://swetha53.github.io/NovaMart/#/)
3. The API since it is self-signed might not be recognised by Chrome so we might have to physically go to the URL of the IP Address and trust the source using the following steps:
    - Go to the URL of the API: https://192.168.2.108:8080/api/products/all
    - Chrome will warn you that this is not secure, go to advanced and click trust anyway.

### 4. Test Reality Service Generation Process
1. To test the base process add only two url images, one of the front of the product and another for the back of the product and hit the create API using postman.
```
POST API
https://192.168.2.108:8080/api/products/create

Raw JSON Body:
{
    "name": "Swivel Chair",
    "merchantId": "d8714737-5b3c-49ea-9042-4e83bb599972",
    "description": "Swivel chair with soft shapes and nice padding. Upholstered in durable leather that blends well in all types of rooms – and with casters that make it easy to move.",
    "price": 379,
    "currencyCode": "CAD",
    "categories": ["home", "office"],
    "attributes": {
        "color": "light brown",
        "height": 96,
        "width": 54
    },
    "images": [
        "https://www.ikea.com/ca/en/images/products/tossberg-malskaer-swivel-chair-grann-light-brown-black__1199989_pe904797_s5.jpg?f=xl",
        "https://www.ikea.com/ca/en/images/products/tossberg-malskaer-swivel-chair-grann-light-brown-black__1199986_pe904796_s5.jpg?f=xl"
    ],
    "quantity": 250
}
```
2. To test the advanced API we need to do the following:
    - Git Clone Open MVS project to the reality-service
   ```
   git clone https://github.com/cdcseacave/openMVS.git
   ```
    - Add more than 2 images in the images request of the create API and before hitting the create API add the folder containing more than 50 images in the reality-service/asset and name the folder images. Such a large dataset can be taken from https://amazon-berkeley-objects.s3.amazonaws.com/index.html#download abo-spins.tar folder.
    - Note: If the process fails try again by hitting the api again sometimes it doesn't get enough features to match in the first set and needs to run again.

