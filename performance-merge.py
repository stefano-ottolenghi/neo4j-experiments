from neo4j import GraphDatabase, AsyncGraphDatabase
import neo4j
import random
from time import time, sleep
import asyncio
import os

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "verysecret")
NODE_N = 10000

def flush_cache():
    return
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.execute_query("CALL db.clearQueryCaches()")
    #return

    os.system("docker restart neo4j5-nightly")
    while True:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            try:
                driver.verify_connectivity()
                return
            except Exception:
                sleep(2)

def clear_db(driver):
    with driver.session() as session:
        session.run("MATCH (a)-[r]-() DETACH DELETE a,r")
        session.run("MATCH (n) DETACH DELETE n")

def merge():
    case = "merge"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        clear_db(driver)
        rows = [random.random() for i in range(NODE_N)]
        start_time = time()
        for row in rows:
            driver.execute_query("MERGE (n:Number {val: $val})", val=row, database_="neo4j")
        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")
def create():
    case = "create"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        clear_db(driver)
        rows = [random.random() for i in range(NODE_N)]
        start_time = time()
        for row in rows:
            driver.execute_query("CREATE (n:Number {val: $val})", val=row, database_="neo4j")
        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def createnovar():
    case = "createnovar"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        clear_db(driver)
        rows = [random.random() for i in range(NODE_N)]
        start_time = time()
        for row in rows:
            driver.execute_query("CREATE (:Number {val: $val})", val=row, database_="neo4j")
        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")


if __name__ == "__main__":
    flush_cache()
    createnovar()
    flush_cache()
    create()
