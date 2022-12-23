from neo4j import GraphDatabase
import re

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secret")
driver = GraphDatabase.driver(URI, auth=AUTH)

text = open('create.adoc').read()

pattern = re.compile(r"""
(?:                             # non-capturing group to match example openin
    \[source,\s*cypher[^\]]*\]  # [source,cypher] and all possible variations, with whitespace and other attributes
    \s*                         # line break and any white space
    -{4}                        # 4 opening dashes
    \s*                         # line break and any white space
)
([^\$]*?)                       # CYPHER QUERY, excluding any query with query attributes (prefixed by $)
\s*                             # line break and any white space
-{4}                            # 4 closing dashes
.*?
(?:
    \[role="queryresult"[^\]]*\]
    \s*
    \|={3}
    \s*
)
(.*?)
\s*
\|\={3}



""", re.MULTILINE | re.DOTALL | re.VERBOSE)
queries = pattern.findall(text)
for query in queries:
    print(query)
    
    # test query
    res = driver.session().run(query)
    print(list(res))
    print(res.consume().counters)
