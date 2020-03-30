package main

import (
	"database/sql"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"

	_ "github.com/mattn/go-sqlite3"
)

type Post struct {
	Id    int
	Title string
	Body  string
}

type Greeting struct {
	Hello string
}

func main() {
	db, err := sql.Open("sqlite3", "./testposts.db")
	if err != nil {
		log.Fatal(err)
	}

	postHandler := func(w http.ResponseWriter, r *http.Request) {
		rows, err := db.Query("SELECT id, title, body FROM posts ORDER BY id DESC LIMIT 10")
		if err != nil {
			log.Fatal(err)
		}
		defer rows.Close()

		var results []Post
		for rows.Next() {
			var p Post
			err := rows.Scan(&p.Id, &p.Title, &p.Body)
			if err != nil {
				log.Fatal(err)
			}
			results = append(results, p)
		}

		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode(results)
	}

	userHandler := func(w http.ResponseWriter, r *http.Request) {
		res, err := http.Get("https://jsonplaceholder.typicode.com/users")
		if err != nil {
			log.Fatal(err)
		}
		defer res.Body.Close()

		bodyBytes, err := ioutil.ReadAll(res.Body)
		if err != nil {
			log.Fatal(err)
		}

		w.Header().Add("Content-Type", "application/json")
		w.Write(bodyBytes)
	}

	helloHandler := func(w http.ResponseWriter, r *http.Request) {
		hello := &Greeting{"world"}

		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode(hello)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/hi", helloHandler)
	mux.HandleFunc("/posts", postHandler)
	mux.HandleFunc("/users", userHandler)
	log.Print("Listening...")
	log.Fatal(http.ListenAndServe("localhost:8000", mux), nil)
}
