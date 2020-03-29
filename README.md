APIBench
========

This repo benchmarks an `asyncio`-based ASGI app (powered by
[Starlette][starlette]) against a traditional WSGI app (powered by
[Flask][flask]). It also includes a version in Go, for reference.

My read of the results is that while ASGI is much more efficient for trivial
tasks, the performance gap narrows considerably for tasks reading from a
database and responding with JSON.

## Result summary

### Starlette is 5x faster than Flask at a trivial "hello world" benchmark.

|           | Req/s | p50 resp time | p80 resp time | p90 resp time |
|-----------|-------|---------------|---------------|---------------|
| Flask     | 960   | 50ms          | 52ms          | 56ms          |
| Starlette | 5789  | 8ms           | 10ms          | 11ms          |
| Golang    | 7797  | 6ms           | 7ms           | 8ms           |


### When hitting external APIs, Starlette is faster at p80, but slower at p90.

|           | Req/s | p50 resp time | p80 resp time |  p90 resp time |
|-----------|-------|---------------|---------------|----------------|
| Flask     | 268   | 152ms         | 206ms         | 227ms          |
| Starlette | 302   | 42ms          | 108ms         | 403ms          |
| Golang    | 924   | 36ms          | 49ms          | 60ms           |

### When connecting directly to a database, Starlette and Flask perform comparably.

However, switching to a _synchronous_ DB client, instead of the [async client
recommended by the Starlette docs][asyncdb], improved Starlette performance by
nearly 2x. This may just be a quirk of SQLite.

|                   | Req/s | p50 resp time | p80 resp time |  p90 resp time |
|-------------------|-------|---------------|---------------|----------------|
| Flask             | 690   | 71ms          | 74ms          | 75ms           |
| Starlette (async) | 712   | 69ms          | 75ms          | 79ms           |
| Starlette (sync)  | 1388  | 35ms          | 38ms          | 42ms           |
| Golang            | 4120  | 11ms          | 13ms          | 15ms           |


## Run it yourself
1. Clone the repo:  
  `git clone git@github.com:chrisfrank/apibench-py`
2. Install dependencies:  
   `make install`
3. In new shell, start the app you'd like to measure:  
   `make starlette` or `make flask` or `make go`
4. In your original shell, benchmark the app:  
   `make bench`

To tweak the settings to better represent your workload, edit the Makefile.

## Concerns
- Using a local SQLite DB is simpler to set up than a remote Postgres DB, but
  totally fails to account for network latency and connection management.
  Anecdotally, I saw similar relative numbers in a version that connected to a
  remote Postgres DB, but I need to do more testing.
- The Flask app launches Gunicorn with _40 threads_, which is unusually high.
  However, this number matches the number of threads started by `uvicorn` on my
  machine.

## Full results

### Flask
```
Flask

BENCH SANS I/O

ab -c 50 -n 1000 -q 127.0.0.1:8000/hi
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        gunicorn/20.0.4
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /hi
Document Length:        18 bytes

Concurrency Level:      50
Time taken for tests:   1.041 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      170000 bytes
HTML transferred:       18000 bytes
Requests per second:    960.72 [#/sec] (mean)
Time per request:       52.044 [ms] (mean)
Time per request:       1.041 [ms] (mean, across all concurrent requests)
Transfer rate:          159.50 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.9      0      14
Processing:     1   50   6.8     50      64
Waiting:        1   49   7.4     50      62
Total:         14   50   5.3     50      64

Percentage of the requests served within a certain time (ms)
  50%     50
  66%     51
  75%     51
  80%     52
  90%     56
  95%     59
  98%     62
  99%     62
 100%     64 (longest request)


BENCH HTTP I/O

ab -c 50 -n 1000 -q 127.0.0.1:8000/users
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        gunicorn/20.0.4
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /users
Document Length:        4104 bytes

Concurrency Level:      50
Time taken for tests:   3.734 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      4258000 bytes
HTML transferred:       4104000 bytes
Requests per second:    267.80 [#/sec] (mean)
Time per request:       186.705 [ms] (mean)
Time per request:       3.734 [ms] (mean, across all concurrent requests)
Transfer rate:          1113.57 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.2      0      10
Processing:    39  173  55.2    152     409
Waiting:       29  170  54.8    150     409
Total:         40  173  55.4    152     410

Percentage of the requests served within a certain time (ms)
  50%    152
  66%    162
  75%    194
  80%    206
  90%    227
  95%    324
  98%    369
  99%    383
 100%    410 (longest request)


BENCH DB I/O

ab -c 50 -n 1000 -q 127.0.0.1:8000/posts
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        gunicorn/20.0.4
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /posts
Document Length:        12623 bytes

Concurrency Level:      50
Time taken for tests:   1.448 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      12778000 bytes
HTML transferred:       12623000 bytes
Requests per second:    690.46 [#/sec] (mean)
Time per request:       72.416 [ms] (mean)
Time per request:       1.448 [ms] (mean, across all concurrent requests)
Transfer rate:          8615.87 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.6      0      13
Processing:    16   70   6.5     71      83
Waiting:        1   69   6.8     70      83
Total:         16   70   5.5     71      83

Percentage of the requests served within a certain time (ms)
  50%     71
  66%     72
  75%     73
  80%     74
  90%     75
  95%     76
  98%     78
  99%     79
 100%     83 (longest request)
 ```

### Starlette
```

BENCH SANS I/O

ab -c 50 -n 1000 -q 127.0.0.1:8000/hi
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        uvicorn
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /hi
Document Length:        17 bytes

Concurrency Level:      50
Time taken for tests:   0.173 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      142000 bytes
HTML transferred:       17000 bytes
Requests per second:    5789.15 [#/sec] (mean)
Time per request:       8.637 [ms] (mean)
Time per request:       0.173 [ms] (mean, across all concurrent requests)
Transfer rate:          802.79 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.5      1       3
Processing:     3    8   1.5      7      12
Waiting:        1    6   1.2      6      11
Total:          4    8   1.5      8      13

Percentage of the requests served within a certain time (ms)
  50%      8
  66%      9
  75%      9
  80%     10
  90%     11
  95%     11
  98%     12
  99%     12
 100%     13 (longest request)


BENCH HTTP I/O

ab -c 50 -n 1000 -q 127.0.0.1:8000/users
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        uvicorn
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /users
Document Length:        4103 bytes

Concurrency Level:      50
Time taken for tests:   3.314 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      4230000 bytes
HTML transferred:       4103000 bytes
Requests per second:    301.71 [#/sec] (mean)
Time per request:       165.722 [ms] (mean)
Time per request:       3.314 [ms] (mean, across all concurrent requests)
Transfer rate:          1246.32 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   1.0      0       9
Processing:    13  133 242.4     42    2423
Waiting:       13  133 242.4     42    2422
Total:         13  133 242.8     42    2429

Percentage of the requests served within a certain time (ms)
  50%     42
  66%     91
  75%    101
  80%    108
  90%    403
  95%    604
  98%    877
  99%   1197
 100%   2429 (longest request)


BENCH DB I/O

ab -c 50 -n 1000 -q 127.0.0.1:8000/posts
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        uvicorn
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /posts
Document Length:        12682 bytes

Concurrency Level:      50
Time taken for tests:   0.720 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      12810000 bytes
HTML transferred:       12682000 bytes
Requests per second:    1388.03 [#/sec] (mean)
Time per request:       36.022 [ms] (mean)
Time per request:       0.720 [ms] (mean, across all concurrent requests)
Transfer rate:          17363.97 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.9      1       6
Processing:     8   34   6.5     33      61
Waiting:        1   30   5.7     30      55
Total:          9   35   6.5     35      62

Percentage of the requests served within a certain time (ms)
  50%     35
  66%     36
  75%     38
  80%     38
  90%     42
  95%     51
  98%     54
  99%     55
 100%     62 (longest request)
 ```

### Golang (for reference)
```
Go (http.NewServeMux)

 BENCH SANS I/O 

ab -c 50 -n 1000 -q 127.0.0.1:8000/hi
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /hi
Document Length:        18 bytes

Concurrency Level:      50
Time taken for tests:   0.128 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      126000 bytes
HTML transferred:       18000 bytes
Requests per second:    7797.21 [#/sec] (mean)
Time per request:       6.413 [ms] (mean)
Time per request:       0.128 [ms] (mean, across all concurrent requests)
Transfer rate:          959.42 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    3   0.9      3       6
Processing:     0    3   0.9      3       8
Waiting:        0    2   0.9      2       6
Total:          1    6   1.2      6      10

Percentage of the requests served within a certain time (ms)
  50%      6
  66%      7
  75%      7
  80%      7
  90%      8
  95%      9
  98%      9
  99%      9
 100%     10 (longest request)


 BENCH HTTP I/O 

ab -c 50 -n 1000 -q 127.0.0.1:8000/users
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /users
Document Length:        5645 bytes

Concurrency Level:      50
Time taken for tests:   1.082 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      5733000 bytes
HTML transferred:       5645000 bytes
Requests per second:    924.16 [#/sec] (mean)
Time per request:       54.103 [ms] (mean)
Time per request:       1.082 [ms] (mean, across all concurrent requests)
Transfer rate:          5174.03 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2   1.6      1      13
Processing:    19   38  12.8     35     232
Waiting:       18   38  12.5     34     219
Total:         19   40  13.2     36     233

Percentage of the requests served within a certain time (ms)
  50%     36
  66%     42
  75%     46
  80%     49
  90%     60
  95%     63
  98%     64
  99%     67
 100%    233 (longest request)


 BENCH DB I/O 

ab -c 50 -n 1000 -q 127.0.0.1:8000/posts
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /posts
Document Length:        12614 bytes

Concurrency Level:      50
Time taken for tests:   0.243 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      12702000 bytes
HTML transferred:       12614000 bytes
Requests per second:    4120.58 [#/sec] (mean)
Time per request:       12.134 [ms] (mean)
Time per request:       0.243 [ms] (mean, across all concurrent requests)
Transfer rate:          51112.96 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    4   1.1      3       8
Processing:     1    8   1.8      8      18
Waiting:        1    5   1.4      4      15
Total:          6   12   2.0     11      22

Percentage of the requests served within a certain time (ms)
  50%     11
  66%     12
  75%     13
  80%     13
  90%     15
  95%     16
  98%     17
  99%     18
 100%     22 (longest request)
 ```


[starlette]: https://www.starlette.io/
[flask]: https://flask.palletsprojects.com/en/1.1.x/
[asyncdb]: https://www.starlette.io/database/
