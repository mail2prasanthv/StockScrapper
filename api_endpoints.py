from flask import Flask, jsonify, request
from orchestration import *
import threading
import asyncio


app = Flask(__name__)



@app.route('/import/financials', methods=['GET'])
async def bulkScrapEndpoint():
   
   mode = request.args.get('mode')
   allowed_modes = ["refresh-missing", "full-refresh"]
   if mode not in allowed_modes:
        return jsonify({"error": "Invalid mode parameter [refresh-missing, full-refresh]"}), 400
   
   thread = threading.Thread(target=bulkScrap, args=(mode,))
   thread.start()
   
   return jsonify({'message': 'Task started successfully!'}), 202
   
@app.route('/import/<string:isin>/financials', methods=['GET'])
def bulkCompanyEndpoint(isin):
   print('-----------------------abc-----------------')
   asyncio.create_task(scrapCompany(isin))
   return jsonify({'message': 'Task started successfully!'}), 202

if __name__ == '__main__':
    app.run(debug=False)