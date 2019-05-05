import time
import mysql.connector
import psycopg2
import traceback
from flask import render_template

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def query():
    print(request.args)
    startTime = 0
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
                result = []
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

                result = []
                for x in myresult:
                    result.append(x)
                cur.close()
                execTime = time.time() - startTime
            elif request.args['activeDB'] == "MongoDB":
                import re
                from pymongo import MongoClient

                groups = re.search(r'select\s+(.*)\s+from\s+(.*)\s+(where (.*)=(.*))', request.args['query'], re.IGNORECASE)

                client = MongoClient('localhost', 27017)
                db = client.CS527
                for doc in db[groups.group(2)].find().limit(10):
                    print(doc)
                # Issue the serverStatus command and print the results
                print(request.args)
                columns = "something"
                result = ""
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
