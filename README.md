## TermFrame subgraph extractor web service


### About

This repository contains the code and web service interface for extracting subgraphs from Karst terminology graphs. It is closely linked to the **[webanno2csv](https://github.com/vpodpecan/webanno2csv)** project and specific to the **[TermFrame](https://termframe.ff.uni-lj.si/)** project. The terminology networks used here (in folder `services/web/networks`) are created by the webanno2csv [convert module](https://github.com/vpodpecan/webanno2csv/blob/main/convert.py).

Currently, there are terminology graphs available for three languages: Slovene, Croatian, and English.


The web service implements two functions:

- fuzzy node search (suggestions) which identifies matching node names;
- subgraph extraction which extracts the neighbourhood of a given set of nodes

Note that subgraph extraction will perform fuzzy matching by default and take the best match for each query node. Also, edge direction will be ignored while searching the neighbourhood of node(s).



### Examples of use

Fuzzy node search request and result:

```bash
curl -X 'POST' \
  'http://0.0.0.0:5000/rest_api/find_matching_nodes' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "language": "sl",
  "text": "dol",
  "k": 5
}'
```

```json
{
  "nodes": [
    "dol",
    "Dolga",
    "Dolek",
    "dolgo",
    "dolec"
  ]
}
```

Subgraph extraction request and result:

```bash
curl -X 'POST' \
  'http://0.0.0.0:5000/rest_api/extract_subgraph' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "language": "sl",
  "nodes": [
    "dol"
  ],
  "width": 1
}'
```

```json
{
  "nodes": [
    {
      "id": 1,
      "label": "lj . na Dinarskem krasu",
      "group": "RELATION"
    },
    {
      "id": 2,
      "label": "A.1 Surface landform",
      "group": "CATEGORY"
    },
    {
      "id": 3,
      "label": "za različne površinske vdolbine (suho dolino, kraško polje) na Dinarskem krasu",
      "group": "RELATION"
    },
    {
      "id": 4,
      "label": "vdolbine",
      "group": "GENUS"
    },
    {
      "id": 5,
      "label": "dol",
      "group": "DEFINIENDUM"
    }
  ],
  "edges": [
    {
      "from": 1,
      "to": 5,
      "label": "has position"
    },
    {
      "from": 2,
      "to": 5,
      "label": "has category"
    },
    {
      "from": 3,
      "to": 5,
      "label": "defined as"
    },
    {
      "from": 4,
      "to": 5,
      "label": "is a"
    }
  ]
}
```


### Requirements

-  docker
-  docker-compose


### How to run

#### Development

The following command

```sh
$ docker-compose up --build
```

will build the images and run the container. If you go to [http://localhost:5000](http://localhost:5000) you will see a web interface where you can check and test the REST API.

#### Production

The following command

```sh
$ docker-compose -f docker-compose.prod.yml up -d --build
```

will build the images and run the service and proxy containers. The web interface is now available at [http://localhost](http://localhost) (port 8080). This setup can be used in production.


###  Authors

[Vid Podpečan](vid.podpecan@ijs.si)


### License

MIT
