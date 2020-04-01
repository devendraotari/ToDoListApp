
from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)
  
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="devendra"
)


@app.route('/')
def index():
   mycursor = mydb.cursor()
   mycursor.execute("SELECT * FROM todoList")
   myresult = mycursor.fetchall()
   return render_template("home.html", tasks=myresult)

@app.route('/add',methods=['POST'])
def add():
    task = request.form['todoitem']
    insertquery = "INSERT into todoList (task,completed) values ('{}',0)".format(task)
    mycursor = mydb.cursor()
    mycursor.execute(insertquery)
    mydb.commit()
    return redirect('/')

@app.route('/task/<taskname>/<taskstatus>')
def change_task_status(taskname,taskstatus):
    i_taskstatus = int(taskstatus)
    if i_taskstatus==1:
      updatequery = "UPDATE todoList set completed=0 where task='{}'".format(taskname)
      
    elif i_taskstatus==0:
        updatequery = "UPDATE todoList set completed=1 where task='{}'".format(taskname)
        
    
    mycursor = mydb.cursor()
    mycursor.execute(updatequery)
    mydb.commit()
    return redirect("/")


@app.route("/delete/<task>")
def deletetask(task):
  deletequery = "delete from todoList where task='{}'".format(task)
  mycursor = mydb.cursor()
  mycursor.execute(deletequery)
  mydb.commit()
  return redirect("/")
 


