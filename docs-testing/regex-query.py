from neo4j import GraphDatabase
import re

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secret")
driver = GraphDatabase.driver(URI, auth=AUTH)

text = open('create.adoc').read()

# This pattern matches Cypher queries from asciidoc files from the Neo4j Cypher manual.
pattern = re.compile(r"""
(?:                             # non-capturing group to match example opening
    \[source,\s*cypher[^\]]*\]  # [source,cypher] and all possible variations, with whitespace and other attributes
    \s*                         # line break and any white space
    -{4}                        # 4 opening dashes
    \s*                         # line break and any white space
)
([^\$]*?)                       # CYPHER QUERY, excluding any query with query attributes (prefixed by $)
\s*                             # line break and any white space
-{4}                            # 4 closing dashes
""", re.MULTILINE | re.DOTALL | re.VERBOSE)
queries = pattern.findall(text)
for query in queries:
    print(f'== Testing `{query}`')
    
    # test query
    res = driver.session().run(query)
    print(list(res))
    print(res.consume().counters)
