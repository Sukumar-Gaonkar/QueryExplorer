import time
import mysql.connector
import psycopg2
import traceback
import json
from flask import render_template

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def query():
    print(request.args)
    startTime = 0
    result = []
    if 'query' in request.args:
        try:
            if request.args['activeDB'] == "MySQL":

                mydb = mysql.connector.connect(
                    host="mydbproj.cxjhjt1oejvp.us-east-2.rds.amazonaws.com",
                    user="supernidhi",
                    passwd="Nidhi267",
                    database="NCAA"
                )

                mycursor = mydb.cursor()
                query = request.args['query'] + " LIMIT 0, 100;"
                print(query)
                startTime = time.time()
                mycursor.execute(query)
                myresult = mycursor.fetchall()

                for x in myresult:
                    result.append(x)
                columns = mycursor.column_names
                execTime = time.time() - startTime
            elif request.args['activeDB'] == "RedShift":
                redshiftdb = psycopg2.connect(dbname='dev', host='cs527.cnyf8pn1ogln.us-east-2.redshift.amazonaws.com',
                                              port='5439', user='supernidhi', password='Nidhi267')
                redshiftdb.autocommit = True

                cur = redshiftdb.cursor()
                query = request.args['query'] + " LIMIT 100;"
                print(query)
                startTime = time.time()
                cur.execute(query)
                myresult = cur.fetchall()

                columns = list(zip(*cur.description))[0]

                for x in myresult:
                    result.append(x)
                cur.close()
                execTime = time.time() - startTime
            elif request.args['activeDB'] == "MongoDB":
                import re
                import pprint as pp
                from pymongo import MongoClient

                groups = re.search(r'select\s+(.*)\s+from\s+(.*?)\s(where\s+.*)*', request.args['query'] + "\n", re.IGNORECASE)

                table_name = groups.group(2).strip()
                cols = [x.strip() for x in groups.group(1).split(",")]
                where_clause = []
                if not groups.group(3) is None:
                    where_clause_str = groups.group(3).strip("\n").split()
                    where_clause = [(where_clause_str[i], where_clause_str[i+1], where_clause_str[i+2], where_clause_str[i+3].strip('"') if '"' in where_clause_str[i+3] else int(where_clause_str[i+3])) for i in range(0, int(len(where_clause_str)), 4)]

                project_clause = {p : 1 for p in cols} if cols[0] != "*" else {}
                project_clause["_id"] = 0
                mongo_clause = {}
                operators = {"=": "$eq", ">": "$gt", "<": "$lt", ">=": "$gte", "<=": "$lte", "<>":"$ne"}
                if len(where_clause) == 1:
                    mongo_clause[where_clause[0][1]] = {operators[where_clause[0][2]]: where_clause[0][3]}
                elif len(where_clause) > 1:
                    mongo_clause["${}".format(where_clause[1][0])] = [{j: {operators[k]:l}} for i, j, k, l in where_clause]

                client = MongoClient('localhost', 27017)
                db = client.CS527
                for json_str in db[table_name].find(mongo_clause, project_clause).limit(10):
                    result.append(json.dumps(json_str, indent=4).replace("\n", "</br>"))
                # Issue the serverStatus command and print the results
                print(request.args)
                columns = "something"
                execTime = time.time() - startTime

        except Exception as ex:
            print(str(ex))
            print(traceback.format_exc())
            return render_template('queryExplorer.html', mysqlActive="active", redShiftActive="", msg=str(ex), status="danger")
        mysqlActive = "active" if request.args['activeDB'] == 'MySQL' else ""
        redShiftActive = "active" if request.args['activeDB'] == 'RedShift' else ""
        mongodbActive = "active" if request.args['activeDB'] == 'MongoDB' else ""

        isNoSQL = True if request.args['activeDB'] == 'MongoDB' else False

        return render_template('queryExplorer.html', resultPresent=True, isNoSQL=isNoSQL, columns=columns, data=result, mysqlActive=mysqlActive, redShiftActive=redShiftActive, mongodbActive=mongodbActive, msg=request.args['query'] + " (Execution Time : " + str(execTime)[:7] + "s)", status="success")
    else:
        return render_template('queryExplorer.html', resultPresent=False, mysqlActive="active", redShiftActive="")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
    # app.run()
