from neo4j import GraphDatabase, AsyncGraphDatabase
import neo4j
import random
from time import time, sleep
import asyncio
import os

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secret")
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

def execute_transaction(tx, number):
    tx.run("CREATE (:Number {value: $value})",
           value=number)

async def async_clear_db(driver):
    async with driver.session() as session:
        await session.run("MATCH (a)-[r]-() DETACH DELETE a,r")
        await session.run("MATCH (n) DETACH DELETE n")

async def async_execute_transaction(tx, number):
    await tx.run("CREATE (:Number {value: $value})",
           value=number)


def exec_query_split():
    case = "execute_query with relationships split"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            driver.execute_query("CREATE (n:Number {value: $value}) "
                                 "CREATE (g:Group {value: $value2}) "
                                 "CREATE (n)-[:BELONGS]->(g) ",
                                 value=random.random(),
                                 value2=random.random(),
                                 database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def exec_query_nosplit():
    case = "execute_query without relationships split"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            driver.execute_query("CREATE (n:Number {value: $value})-[:BELONGS]->(g:Group {value: $value2}) ",
                                 value=random.random(),
                                 value2=random.random(),
                                 database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def exec_query_batch_split():
    case = "execute_query with batching with relationships split"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        rows = [{"number": random.random(), "group": random.random()} for i in range(NODE_N)]
        groups = [{"value": random.random()} for i in range(NODE_N)]

        start_time = time()
        driver.execute_query("WITH $rows as batch "
                             "UNWIND batch as row "
                             "CREATE (n:Number {node: row.number}) "
                             "CREATE (g:Group {node: row.group}) "
                             "CREATE (n)-[:BELONGS]->(g)",
                             rows=rows,
                             database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def exec_query_batch_nosplit():
    case = "execute_query with batching without relationships split"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        rows = [{"number": random.random(), "group": random.random()} for i in range(NODE_N)]
        groups = [{"value": random.random()} for i in range(NODE_N)]

        start_time = time()
        driver.execute_query("WITH $rows as batch "
                             "UNWIND batch as row "
                             "CREATE (n:Number {node: row.number})-[:BELONGS]->(g:Group {node: row.group}) ",
                             rows=rows,
                             database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")


if __name__ == "__main__":
    flush_cache()
    exec_query_batch_nosplit()
    flush_cache()
    exec_query_batch_split()
    flush_cache()
    exec_query_nosplit()
    flush_cache()
    exec_query_split()
