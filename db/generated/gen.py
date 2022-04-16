from unicodedata import category
from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random
from datetime import datetime
import time

num_users = 100
num_products = 500
num_purchases = 5000
num_categories = 20
num_inventories = 2000
num_ProductFeedback = 2000
num_SellerFeedback = 200
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
    user_ids = []

    with open('Users.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            user_ids.append(row[0])

    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            category = fake.random_int(min = 0,max = num_categories-1)
            description = fake.sentence(nb_words=10)
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            image = fake.image_url()
            available = fake.random_int(max=1)
            creator_id = fake.random_element(elements=user_ids)
            if available == 1:
                available_pids.append(pid)
            writer.writerow([pid, name, category, description, price, image ,available,creator_id])
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
            time_purchased = fake.date_between_dates(date_start=datetime(2022,1,1), date_end=datetime(2022,4,15))
            hex_time = hex(int(time.mktime(time_purchased.timetuple())))[2:]
            quantity = fake.random_int(min = 1,max = 100)
            price = fake.random_int(min = 1,max = 10000)
            order_id =  int(hex_time+str(uid),16)
            order_status = 0
            fulfill_date = fake.date_between_dates(date_start=datetime(2022,1,1), date_end=datetime(2022,4,15))
            writer.writerow([id, uid, pid,sid, time_purchased,quantity,price,order_id,order_status,fulfill_date])
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
            release_date = fake.date_between_dates(date_start=datetime(2022,1,1), date_end=datetime(2022,4,15))
            quantity = fake.random_int(min = 1,max = 100)
            price = fake.random_int(min = 1,max = 10000)
            writer.writerow([id, sid, pid, quantity,price,release_date])
        print(f'{num_inventories} generated')
    return 

def gen_ProductFeedback(num_ProductFeedback, available_products, available_buyers):
    with open('ProductFeedback.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('ProductFeedback...', end=' ', flush=True)
        for id in range(num_ProductFeedback):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_element(elements=available_buyers)
            pid = fake.random_element(elements=available_products)
            rating = fake.random_int(min = 1,max = 10)
            review = fake.sentence(nb_words=50)
            time_feedback = fake.date_between_dates(date_start=datetime(2022,1,1), date_end=datetime(2022,4,15))
            upvotes = fake.random_int(min = 1,max = 50)
            writer.writerow([id, uid, pid, rating, review, time_feedback, upvotes])
        print(f'{num_inventories} generated')
    return 

def gen_SellerFeedback(num_SellerFeedback, available_sellers, available_buyers):
    with open('SellerFeedback.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('SellerFeedback...', end=' ', flush=True)
        for id in range(num_SellerFeedback):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_element(elements=available_buyers)
            sid = fake.random_element(elements=available_sellers)
            rating = fake.random_int(min = 1,max = 10)
            review = fake.sentence(nb_words=50)
            time_feedback = fake.date_between_dates(date_start=datetime(2022,1,1), date_end=datetime(2022,4,15))
            upvotes = fake.random_int(min = 1,max = 50)
            writer.writerow([id, uid, sid, rating, review, time_feedback, upvotes])
        print(f'{num_inventories} generated')
    return 


users = gen_users(num_users)
categories = gen_categories(num_categories)
available_pids = gen_products(num_products,categories)
available_sellers = users[0]
available_buyers = users[1]
gen_purchases(num_purchases, available_pids,available_sellers)
gen_inventory(available_sellers,num_inventories)
gen_ProductFeedback(num_ProductFeedback, available_pids, available_buyers)
gen_SellerFeedback(num_SellerFeedback, available_sellers, available_buyers)
#test push