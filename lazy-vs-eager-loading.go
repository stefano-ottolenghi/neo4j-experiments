package main

import (
    "context"
    "time"
    "fmt"
    "github.com/neo4j/neo4j-go-driver/v5/neo4j"
    "net/http"
)

var slowQuery = `
UNWIND range(1, 2500) AS s
RETURN reduce(s=s, x in range(1,1000000) | s + sin(toFloat(x))+cos(toFloat(x))) AS output,  // this property takes long to generate
range(1, 10000) AS dummyData  // this property is big in memory (~10kb)
`
var sleepTime = "0.5s"

func main() {
    http.HandleFunc("/hello", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "Hello, playground")
	})

ctx := context.Background()
    dbUri := "neo4j://localhost"
    dbUser := "neo4j"
    dbPassword := "verysecret"
    driver, err := neo4j.NewDriverWithContext(
        dbUri,
        neo4j.BasicAuth(dbUser, dbPassword, ""))
    if err != nil {
        panic(err)
    }
    defer driver.Close(ctx)

    err = driver.VerifyConnectivity(ctx)
    if err != nil {
        panic(err)
    }

    lazyLoading(ctx, driver)
    //eagerLoading(ctx, driver)
}


func eagerLoading(ctx context.Context, driver neo4j.DriverWithContext) {
    defer timer("eagerLoading")()

    log("Submit query")
    result, err := neo4j.ExecuteQuery(ctx, driver,
        slowQuery,
        nil,
        neo4j.EagerResultTransformer,
        neo4j.ExecuteQueryWithDatabase("neo4j"))
    if err != nil {
        panic(err)
    }

    sleepTimeParsed, err := time.ParseDuration(sleepTime)
    if err != nil {
        panic(err)
    }

    // Loop through results and do something with them
    for _, record := range result.Records {
        output, _ := record.Get("output")
        log(fmt.Sprintf("Processing record %v", output))
        time.Sleep(sleepTimeParsed)  // proxy for some expensive operation
    }
}

func lazyLoading(ctx context.Context, driver neo4j.DriverWithContext) {
    defer timer("lazyLoading")()

    sleepTimeParsed, err := time.ParseDuration(sleepTime)
    if err != nil {
        panic(err)
    }

    session := driver.NewSession(ctx, neo4j.SessionConfig{DatabaseName: "neo4j"})
    defer session.Close(ctx)
    session.ExecuteRead(ctx,
        func(tx neo4j.ManagedTransaction) (any, error) {
            log("Submit query")
            result, err := tx.Run(ctx, slowQuery, nil)
            if err != nil {
                return nil, err
            }
            for result.Next(ctx) != false {
                record := result.Record()
                output, _ := record.Get("output")
                log(fmt.Sprintf("Processing record %v", output))
                time.Sleep(sleepTimeParsed)  // proxy for some expensive operation
            }
            return nil, nil
        })
}

func log(msg string) {
    fmt.Println("[", time.Now().Unix(), "] ", msg)
}

func timer(name string) func() {
    start := time.Now()
    return func() {
        fmt.Printf("-- %s took %v --\n\n", name, time.Since(start))
    }
}
