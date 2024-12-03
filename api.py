import json
import heapq
from dateutil import parser
from flask import Flask, jsonify, request, Response
# importing basic dependencies

#instructions for running
# 1. open virtual environment (venv)
# 2. pip install flask and dateutil

app = Flask(__name__)

values = []
#storing each timestamp in a priority queue

user_balance = {}
total_points = 0
#storing current total balance and individual balance

@app.route('/balance',methods=["GET"])
def return_balance():
    # return json of stored individual balances
    return jsonify(user_balance)

@app.route('/spend', methods=['POST'])
def spend_points():
    spending = json.loads(request.data)
    points = spending["points"]
    global total_points
    # taking care of input 

    if points > total_points:
        # if point is less than total points we cannot complete operation
        return Response(status=400, description ="Not enough points")

    return_dict = {}
    #storing the users we subtract points from
    while points > 0:
        # loop until we subtract all points
        element = heapq.heappop(values)
        #dequeue earliest element
        if element[2] > points:
            # case where earliest element has more than remaining points
            if element[1] not in return_dict:
                return_dict[element[1]] = -points
            else:
                return_dict[element[1]] -= points
            element[2] -= points
            user_balance[element[1]] -= points
            points = 0
        else:
            # default case where we need to continue looping
            points -= element[2]
            if element[1] not in return_dict:
                return_dict[element[1]] = -element[2]
            else:
                return_dict[element[1]] -= element[2]
            user_balance[element[1]] -= element[2]
    return jsonify(return_dict)
            


@app.route('/add',methods=['POST'])
def add_transaction():
    transaction = json.loads(request.data)
    points = transaction["points"]
    payer = transaction["payer"]
    timestamp = parser.parse(transaction["timestamp"]).timestamp()
    #timestamp is parsed to epoch
    global total_points 
    #taking care of input

    if points >=0:
        # case when we are adding points
        # add points to both individual user balance and the priority queue based on time
        if payer not in user_balance:
            user_balance[payer] = 0
        user_balance[payer] += points
        total_points += points
        heapq.heappush(values, [timestamp, payer, points])
    else:
        # case when we are subtracting points
        # remove top layer of PQ until we reduce all negative points
        if user_balance[payer] > abs(points):
            #only proceed if the points are available
            subtract = abs(points)
            temp_store = []
            # will add values from temp_store to PQ again later
            while subtract > 0:
                #iterating over PQ removing positive balance from same payer
                element = heapq.heappop(values)
                if element[1] == payer:
                    if element[2] > subtract:
                        element[2] -= subtract
                        subtract = 0
                        heapq.heappush(values,element)
                    else:
                        subtract -= element[2]
                else:
                    temp_store.append(element)
            for item in temp_store:
                #adding to PQ again
                heapq.heappush(values,item)
            user_balance[payer] -= abs(points)
            total_points -= abs(points)
    
    return Response(status=200) 
    
if __name__ == '__main__':
   app.run(port=8000)