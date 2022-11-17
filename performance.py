from neo4j import GraphDatabase, AsyncGraphDatabase
import neo4j
import random
from time import time, sleep
import asyncio
import os

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secret")
NODE_N = 5000

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

def exec_query_without_db():
    case = "execute_query, no database selection"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            driver.execute_query("CREATE (:Number {value: $value})",
                                 value=random.random())

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def exec_query_with_db():
    case = "execute_query, with database selection"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            driver.execute_query("CREATE (:Number {value: $value})",
                                 value=random.random(),
                                 database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def transaction_func_without_db():
    case = "transaction functions, without database selection"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            with driver.session() as session:
                session.execute_write(execute_transaction, random.random())

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def transaction_func_with_db():
    case = "transaction functions, with database selection"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            with driver.session(database="neo4j") as session:
                session.execute_write(execute_transaction, random.random())

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

async def async_exec_query_with_db():
    case = "async execute_query, with database selection"
    async with AsyncGraphDatabase.driver(URI, auth=AUTH) as driver:
        await driver.verify_connectivity()
        await async_clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            await driver.execute_query("CREATE (:Number {value: $value})",
                                       value=random.random(),
                                       database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

async def async_exec_query_without_db():
    case = "async execute_query, without database selection"
    async with AsyncGraphDatabase.driver(URI, auth=AUTH) as driver:
        await driver.verify_connectivity()
        await async_clear_db(driver)

        start_time = time()
        for _ in range(NODE_N):
            await driver.execute_query("CREATE (:Number {value: $value})",
                                       value=random.random())

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

def execute_query_batch():
    case = "execute_query with batching"
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        clear_db(driver)

        numbers = [{"value": random.random()} for i in range(NODE_N)]

        start_time = time()
        driver.execute_query("WITH $numbers as batch "
                             "UNWIND batch as node "
                             "CREATE (n:Number) "
                             "SET n += node",
                             numbers=numbers,
                             database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

async def async_execute_query_batch():
    case = "async execute_query with split batching"
    async with AsyncGraphDatabase.driver(URI, auth=AUTH) as driver:
        await driver.verify_connectivity()
        await async_clear_db(driver)

        split = 10
        numbers = [[{"value": random.random()} for i in range(NODE_N//split)] for x in range(split)]

        start_time = time()
        for number_list in numbers:
            await driver.execute_query("WITH $numbers as batch "
                                       "UNWIND batch as node "
                                       "CREATE (n:Number) "
                                       "SET n += node",
                                       numbers=number_list,
                                       database_="neo4j")

        execution_time = time() - start_time
        print(f"** Case {case} **\n"
              f"Run time {execution_time} seconds\n")

if __name__ == "__main__":
    flush_cache()
    exec_query_without_db()
    flush_cache()
    exec_query_with_db()
    flush_cache()
    transaction_func_without_db()
    flush_cache()
    transaction_func_with_db()
    flush_cache()
    asyncio.run(async_exec_query_without_db())
    flush_cache()
    asyncio.run(async_exec_query_with_db())
    flush_cache()
    execute_query_batch()
    flush_cache()
    asyncio.run(async_execute_query_batch())
