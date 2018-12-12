# assignment5-2018-Benjamin-Dewey

### To deploy server on a vm instance

```
> sudo apt-get update; sudo apt-get install python-dev python-virtualenv git
> git clone https://github.com/CSCI-UA0480-009/assignment5-2018-Benjamin-Dewey.git
> cd assignment5-2018-Benjamin-Dewey
> ./install.sh
> source ./env/bin/activate
> nohup python3 server.py &
```

### To run client

```
# you need python 3.6+ and virtualenv installed on your machine
> git clone https://github.com/CSCI-UA0480-009/assignment5-2018-Benjamin-Dewey.git
> cd assignment5-2018-Benjamin-Dewey
> ./install.sh
> source ./env/bin/activate
> ./mailman.sh
```
