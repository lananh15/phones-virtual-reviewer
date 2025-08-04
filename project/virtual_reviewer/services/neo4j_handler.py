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
        def execute(tx):
            result = tx.run(query, parameters)
            return [record.data() for record in result]
        with self.driver.session() as session:
            return session.execute_read(execute)

    def run_write_query(self, query, parameters={}):
        def execute(tx):
            tx.run(query, parameters)
        with self.driver.session() as session:
            session.execute_write(execute)

    def close(self):
        self.driver.close()