from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jHandler:
	def __enter__(self):
		self.uri = os.getenv('NEO4J_URI')
		self.user = os.getenv('NEO4J_USER')
		self.password = os.getenv('NEO4J_PASS')
		self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.driver.close()

	def run_read_query(self, query, parameters={}):
		"""
		Executes a read (query) operation on the Neo4j database
		Inputs:
			query (str): Cypher query string
			parameters (dict): Optional query parameters
		Output:
			list: A list of dictionaries representing query results
		"""

		def execute(tx):
			result = tx.run(query, parameters)

			return [record.data() for record in result]

		with self.driver.session() as session:
			return session.execute_read(execute)

	def run_write_query(self, query, parameters={}):
		"""
		Executes a write (update/create/delete) operation on the Neo4j database
		Inputs:
			query (str): Cypher query string
			parameters (dict): Optional query parameters
		Output:
			None
		"""

		def execute(tx):
			tx.run(query, parameters)

		with self.driver.session() as session:
			session.execute_write(execute)

	def close(self):
		self.driver.close()