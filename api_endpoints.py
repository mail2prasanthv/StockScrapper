from flask import Flask, jsonify, request
from orchestration import *
import threading
import asyncio


app = Flask(__name__)



@app.route('/import/financials', methods=['GET'])
async def bulkScrapEndpoint():
   thread = threading.Thread(target=bulkScrap)
   thread.start()
   
   return jsonify({'message': 'Task started successfully!'}), 202
   
@app.route('/import/<string:isin>/financials', methods=['GET'])
def bulkCompanyEndpoint(isin):
   print('-----------------------abc-----------------')
   asyncio.create_task(scrapCompany(isin))
   return jsonify({'message': 'Task started successfully!'}), 202

if __name__ == '__main__':
    app.run(debug=False)