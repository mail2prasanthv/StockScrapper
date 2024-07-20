import os.path
from downloadcompanylist import *
from extractdataxlsx import *
from ScreenerScrapper import *
import time
from math import ceil
from itertools import islice
import asyncio
from flask import Flask, jsonify, request

HOST = 'localhost'
PORT = 27017
DB_NAME = 'stock-market'
TABLE_NAME = 'companies'

client = MongoClient(HOST, PORT)
mongodatabase = client[DB_NAME]
companiesCollection = mongodatabase[TABLE_NAME]

app = Flask(__name__)

def divide_chunks(l, n):
     
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def sort_dictionary(dictionary_list):
  """Sorts a dictionary list by the value of the `name` key.

  Args:
    dictionary_list: A list of dictionaries.

  Returns:
    A sorted list of dictionaries.
  """

  sorted_dictionary_list = sorted(dictionary_list, key=lambda dictionary: dictionary['symbol'])
  return sorted_dictionary_list

def getUniqueDictionary(list_of_dicts, field):
    unique_list = []
    seen_names = set()

    for d in list_of_dicts:
        if d[field] not in seen_names:
            unique_list.append(d)
            seen_names.add(d[field])
    return unique_list

# https://testdriven.io/blog/flask-async/
# https://www.youtube.com/watch?v=0z74b3c63GA

def scrapCompanies(identifierMap, force):
    failedList =[]
    now= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for index, doc in enumerate(identifierMap):
     isin = doc["_id"]
     identifiers = doc["identifiers"]
     print(isin, identifiers)
     for index, identifier in enumerate(identifiers):
        print(identifier)
        try:

          print("start scrap:isin: " , isin, ":", identifier, )
          msg = startScrap(identifier, isin, force)
          break
        except (WebPageNotAvailableException, MarketCapDataNotAvailableException, LatestDataNotAvailable):
          print("Fail to scrap:" , isin, " identifier:", identifier)
          
          failedList.append(isin)
          with open('failed_'+now+'.txt', 'a') as file:
            file.write(isin+'\n')
    print("Failed List:")
    print(failedList)

def bulkScrap():
  print('-------------------bulkScrap-------------------------')
  length_to_split = [50]
  # isin_nse_bse_codes_map = getCompaniesListFromCsv()
  # scrapCompanies(isin_nse_bse_codes_map,False)
  projection = {
        "_id": 1,        
        "bseCode": 1,  
        "nseTradingSymbol": 1,
        "bseTradingSymbol": 1 
    }

  query = {}
  documents = read_selected_attributes(companiesCollection, query, projection)
  # Convert the values of each JSON document to retain the first field and combine the rest into a list
  converted_documents = convert_json_values_with_first_field(documents)
    # Print each document
  # for document in converted_documents:
  #    print(document)
  print("---------------------------") 
  for index, doc in enumerate(converted_documents):
     print(doc["_id"], doc["identifiers"])
     for index, identifier in enumerate(doc["identifiers"]):
         print(identifier)

  scrapCompanies(converted_documents,False);#{'_id': 'INE187D01029', 'identifiers': ['505160', 'TALBROAUTO']}
  print("Finished") 

def read_selected_attributes(collection, query={}, projection=None):
    # Query the collection and apply the projection
    documents = collection.find(query, projection)
    
    # Convert cursor to list and return
    return list(documents)

def convert_json_values_with_first_field(json_documents):
    """
    Retain the first field as is and combine the rest of the distinct values into a list.
    
    :param json_documents: List of JSON documents (dictionaries)
    :return: List of dictionaries with the first field retained and the rest combined into a distinct list
    """
    converted_documents = []
    for doc in json_documents:
        # Convert the document items to a list of tuples (key, value)
        items = list(doc.items())
        # Retain the first field
        first_field = items[0]
        # Combine the rest of the values into a set to ensure uniqueness
        remaining_values = {value for _, value in items[1:]}
        # Convert the set back to a list
        remaining_values_list = list(remaining_values)
        # Create the new document structure
        new_doc = {first_field[0]: first_field[1], "identifiers": remaining_values_list}
        converted_documents.append(new_doc)
    return converted_documents

def scrapCompany(isin):
   scrapCompanies(list(isin), True)

# @app.route('/import/financials', methods=['GET'])
# async def bulkScrapEndpoint():
#    data = await bulkScrap()  
#    return jsonify({'message': 'Task started successfully!'}), 202


if __name__ == '__main__':
  bulkScrap()