# Catalog app

This is the Catalog App project from the Udacity course Full Stack Web Development

## Getting Started

To get started you will need to pull this project into a local repository. 
### Prerequisites

* Virtualbox
* Python3 
* psycopg2 python package

To install paycopq2 run this command in the terminal or command line. 

```
 pip3 install psycopg2
```

### Installing

To launch vagrant, open a command line (or terminal) and change directory (cd) into the vagrent folder.

Then run this command 

```
vagrant up
```

Once vagrant has been initialized in the virtual environment you will need to ssh into the system

```
vagrent ssh
```

now cd into the vagrant virtual directory 

```
cd /vagrant
```

To run the code cd into the src file and run

```
python3 items_catalog_app.py
```

## Built With

* [Python3](https://www.python.org/downloads/) - Programing Language
* [Vagrant](https://www.vagrantup.com/) - Development Environment
* [Virtualbox](https://www.virtualbox.org/) - Virtual Environment

