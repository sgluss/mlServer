### To build container
`docker build -t app .`

### To run server
`docker run --name app --rm -i -p 8080:8080 -t app`

### Service Hello World
curl <host>:8080/hello

### To train model
curl <host>:8080/train

### To request prediction
curl <host>:8080/predict -H "Content-Type: text/csv" --data <CSV data>

EG:  
curl localhost:8080/predict -H "Content-Type: text/csv" --data "25, Private, 22
6802, 11th, 7, Never-married, Machine-op-inspct, Own-child, Black, Male, 0, 0, 40, United-States"
