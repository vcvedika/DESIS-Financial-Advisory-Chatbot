import csv
import os
from pymongo import MongoClient

# connect to MongoDB atlas
client = MongoClient(
    'mongodb+srv://Desis:Desis@cluster0.4qlek3x.mongodb.net/?retryWrites=true&w=majority')
db = client['Desis']
user_data_collection = db['Desis']

# dictionary to store user data
user_data = {
    "user": 'user_1',
    "Important": {},
    "Non-important": {},
    "Essential": {},
    "Non-Essential": {},
    "Global Balance": 0,
}

# CHANGE name of directory where check file is
csv_directory = r"C:\Users\Aastha Khandelwal\Desktop\DESIS Ascend Educare 2022\Project\desis-final-project\SavedCSV"   # CHANGE

# list all CSV files in the directory
csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]
# read csv file and populate user_data dictionary
for file in csv_files:
    with open(csv_directory+f"/{file}", mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            transaction = {}
            transaction = {
                "TxnDate": row['Txn Date'],
                "Description": row['Description'],
                "Transfer To/From": row['Transfer To/From'],
                "RefNo+ChequeNo.": row['Ref No./Cheque No.'],
                "Debit": float(row['Debit']),
                "Credit": float(row['Credit']),
                "Balance": float(row['Balance'])
            }
            category = row['Class']
            ref_no = row['Ref No./Cheque No.']
            if ref_no != '':
                user_data[category][ref_no] = transaction

            # update category balance
            user_data[category]["Balance"] = user_data[category].get(
                "Balance", 0) - transaction["Debit"] + transaction["Credit"]

            # update global balance
            user_data["Global Balance"] += - \
                transaction["Debit"] + transaction["Credit"]

    # insert user data into MongoDB
    user_data_collection.insert_one(user_data)
