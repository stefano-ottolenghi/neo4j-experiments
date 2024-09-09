import neo4j


def custom_resolver(socket_address):
    # assert isinstance(socket_address, neo4j.Address)
    if socket_address != ("example.com", 9999):
        raise OSError(f"Unexpected socket address {socket_address!r}")

    # You can return any neo4j.Address object
    yield neo4j.Address(("google.com", 7687))  # IPv4
#    yield neo4j.Address(("::1", 7687, 0, 0))  # IPv6
#    yield neo4j.Address.parse("localhost:7687")
#    yield neo4j.Address.parse("[::1]:7687")

    # or any tuple that can be passed to neo4j.Address(...).
    # This will initially be interpreted as IPv4, but DNS resolution
    # will turn it into IPv6 if appropriate.
#    yield "::1", 7687
    # This will be interpreted as IPv6 directly, but DNS resolution will
    # still happen.
#    yield "::1", 7687, 0, 0
#    yield "127.0.0.1", 7687


driver = neo4j.GraphDatabase.driver("neo4j://example.com:9999",
                                    auth=("neo4j", "secret"),
                                    resolver=custom_resolver)
driver.verify_connectivity()
