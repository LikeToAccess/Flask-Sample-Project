# -*- coding: utf-8 -*-
# filename          : main.py
# description       : Flask sample project
# author            : Ian Ault
# email             : liketoaccess@protonmail.com
# date              : 05-03-2022
# version           : v1.0
# usage             : python main.py
# notes             :
# license           : MIT
# py version        : 3.10.2 (must run on 3.6 or higher)
#==============================================================================
import os
import json
import sqlite3
from contextlib import closing
from flask import Flask
from flask_restful import Resource, Api, reqparse
from waitress import serve


app = Flask(__name__)
api = Api(app)


def read_json_file(filename, encoding="utf8"):
	if not os.path.exists(filename): return []
	with open(filename, "r", encoding=encoding) as file:
		data = json.load(file)

	return data

def write_json_file(filename, data, encoding="utf8"):
	with open(filename, "w", encoding=encoding) as file:
		json.dump(data, file, indent=4, sort_keys=True)

	return json.dumps(data, indent=4, sort_keys=True)

def append_json_file(filename, data, encoding="utf8"):
	existing_data = read_json_file(filename, encoding=encoding)
	existing_data.append(data)
	write_json_file(filename, existing_data, encoding=encoding)

def read_database_file(path, table_name, args):
	with closing(sqlite3.connect(path)) as connection:
		with closing(connection.cursor()) as cursor:
			rows = []
			for key in args.keys():
				rows += cursor.execute(
					f"SELECT name, email, profile_picture FROM {table_name} WHERE {key} = ?",
					(args[key],),
				).fetchall()

	return rows

def create_database_file(path, table_name, data):
	with closing(sqlite3.connect(path)) as connection:
		with closing(connection.cursor()) as cursor:
			cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({data})")

def write_database_file(path, table_name, data):
	with closing(sqlite3.connect(path)) as connection:
		with closing(connection.cursor()) as cursor:
			cursor.execute(f"INSERT INTO {table_name} VALUES {data}")
			connection.commit()


class Users(Resource):
	def __init__(self):
		create_database_file("./data/users.db", "users", "name TEXT, email TEXT, profile_picture TEXT")

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument("email", required=False, type=str, location="args")
		parser.add_argument("name", required=False, type=str, location="args")
		args = parser.parse_args()
		if args:
			data = read_database_file("./data/users.db", "users", args)
			if data:
				print(f"Succesful 200 in GET request: {data}")
				return {"data": data}, 200
			print(f"Error 404 in GET request: {args['email']} does not exist")
			return {"message": f"{args['email']} does not exist"}, 404
		print("Error 409 in GET request: An email is required")
		return {"message": "An email is required"}, 409

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("name", required=True, type=str, location="args")
		parser.add_argument("email", required=True, type=str, location="args")
		parser.add_argument("profile_picture", required=False, type=str, location="args")
		args = parser.parse_args()


		data = read_database_file("./data/users.db", "users", {"email": args["email"]})
		if data:
			print(f"Error 409 in POST request: {args['email']} already exists")
			return {
				"message": f"{args['email']} already exists"
			}, 409

		data = args["name"], args["email"], args["profile_picture"]

		write_database_file(
			"./data/users.db",
			"users",
			f"{(args['name'], args['email'], args['profile_picture'])}".replace("None", "NULL")
		)

		# return {
		# 	"name":            args["name"],
		# 	"email":           args["email"],
		# 	"profile_picture": args["profile_picture"],
		# }, 200
		print("Succesful 200 in POST request: New user created")
		return {"message": "New user created"}, 200

class Reviews(Resource):
	def get(self):
		return {"message": "Not implemented"}, 501

	def post(self):
		return {"message": "Not implemented"}, 501


def main():
	api.add_resource(Users, "/users")
	api.add_resource(Reviews, "/reviews")
	serve(app, host="0.0.0.0", port=8080)
	# app.run()


if __name__ == "__main__":
	main()
