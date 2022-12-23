from neo4j import GraphDatabase
import re

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secret")
driver = GraphDatabase.driver(URI, auth=AUTH)

text = open('create.adoc').read()

# This pattern matches a query and a result found afterwards, skipping 
# any content found in between. Source page should always contain a result
# for each query. 
# Expected input is an asciidoc file from the Neo4j Cypher manual.
pattern = re.compile(r"""
(?:                               # non-capturing group to match example opening
    \[source,\s*cypher[^\]]*\]    # [source,cypher] and variations (whitespace, other attributes)
    \s*                           # line break and any white space
    -{4}                          # 4 opening dashes
    \s*                           # line break and any white space
)
([^\$]*?)                         # CYPHER QUERY, excluding any query with query attributes (prefixed by $)
\s*                               # line break and any white space
-{4}                              # 4 closing dashes
.*?                               # non-greedy match any char in between query and result
(?:                               # non-capturing group to match result opening
    \[role="queryresult"[^\]]*\]  # [role="queryresult"] and variations (whitespace, other attributes)
    \s*                           # line break and any white space
    \|={3}                        # opening |===
    \s*                           # line break and any white space
)
(.*?)                             # QUERY RESULT
\s*                               # line break and any white space
\|\={3}                           # closing ===|
""", re.MULTILINE | re.DOTALL | re.VERBOSE)
matches = pattern.findall(text)
for (query, result) in matches:
    print(f'== Testing `{query}`')
    print(f' > Expected result:\n{result}\n')
    
    # test query
    res = driver.session().run(query)
    print(list(res))
    print(res.consume().counters)
