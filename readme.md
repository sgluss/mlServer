### To build container
`docker build -t app .`

### To run server
`docker run --name app --rm -i -p 8080:8080 -t app`

### Service Hello World
Make request to:
<host>:8080/hello

### To train model
Make request to:
<host>:8080/train
