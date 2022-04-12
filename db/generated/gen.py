from unicodedata import category
from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random


num_users = 100
num_products = 2000
num_purchases = 2500
num_categories = 20
num_inventories = 5000
Faker.seed(516)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_categories(num_categories):
    categories = set()
    with open('Categories.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Categories...', end=' ', flush=True)
        for i in range(num_categories):
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            name = fake.word()
            if name in categories:
                continue
            writer.writerow([i,name])
            categories.add(name)
        print(f'{num_categories} generated')
    return list(categories)


def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        sellers = []
        buyers = []
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            isSeller =  fake.random_int(max=1)
            balance = random.randint(20, 10000)
            address = fake.address()
            writer.writerow([uid, email, password, firstname, lastname,isSeller,balance,address])
            if isSeller == 1:
                sellers.append(uid)
            else:
                buyers.append(uid)
        print(f'{num_users} generated')
    return [sellers,buyers]

def gen_products(num_products, categories):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            category = fake.random_int(min = 0,max = num_categories-1)
            description = fake.sentence(nb_words=10)
            image = fake.image_url()
            #price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            available = fake.random_int(max=1)
            if available == 1:
                available_pids.append(pid)
            writer.writerow([pid, name, description,image ,available, category])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

def gen_purchases(num_purchases, available_pids,available_sellers):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        purchaseId = []
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            sid = fake.random_element(elements = available_sellers)
            time_purchased = fake.date_time()
            quantity = fake.random_int(min = 1,max = 100)
            price = fake.random_int(min = 1,max = 10000)
            order_id = fake.random_int(min = 1, max = num_purchases//3)
            order_status = 0
            writer.writerow([id, uid, pid,sid, time_purchased,quantity,price,order_id,order_status])
            purchaseId.append(id)
        print(f'{num_purchases} generated')
    return purchaseId

def gen_inventory(available_sellers,num_inventories):
    with open('Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        for id in range(num_inventories):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            pid = fake.random_element(elements=available_pids)
            sid = fake.random_element(elements = available_sellers)
            release_date = fake.date_time()
            quantity = fake.random_int(min = 1,max = 100)
            price = fake.random_int(min = 1,max = 10000)
            writer.writerow([id, sid, pid, quantity,price,release_date])
        print(f'{num_inventories} generated')
    return 


users = gen_users(num_users)
categories = gen_categories(num_categories)
available_pids = gen_products(num_products,categories)
available_sellers = users[0]
gen_purchases(num_purchases, available_pids,available_sellers)
gen_inventory(available_sellers,num_inventories)