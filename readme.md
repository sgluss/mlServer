### To use container, first pull repo
`git clone https://github.com/sgluss/mlServer.git`

### To build container
From repo root:
`docker build -t app .`

### To run server
From repo root:
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

### Design Considerations:
#### API must be able to support 1000+ RPS
Thanks to the containerized, stateless nature of the service, this is a relatively simple task to accomplish.  
**1st:** Store the model in a database, so that many nodes can access it (these nodes may be geographically spread to create an edge service)    
**2nd:** Configure Gunicorn to spawn 1 worker per physical core (each instance can now support 2-64+x throughput)  
**3rd:** Put service layer into ECS/EKS (elastic container service), using autoscaler and elastic load balancer. This will allow each AZ (Availability Zone) to scale independently, as needed  
**4th:** Using service metrics, optimize code, perhaps choose higher performance language/ML solution (even without this, I have load tested a similar service to 300+ RPS on a single AWS C4 2xlarge, and the service is trivial to scale horizontally)   

#### Train/Test dataset is 3 GB or more
This may not be a big problem, depending on the chosen algorithm. A large dataset of this size will still fit on one machine.  

The dataset can be streamed into AWS S3 or a comparable service easily, then loaded into a training instance. The main concern is training time.  
#### Time needed to train each model is 3 hr
For large datasets and complicated model types, model training may take a very, very long time, even on a powerful machine. There are a variety of solutions to this.  

One approach is to use a model that can be trained in parallel on a GPU or a large cluster.

Another possibility is models that can be trained incrementally as new data comes in, which for very large datasets would be a huge advantage (as long as accuracy is not sacrificed).  

Model training can be improved by limiting the number of input variables, or by using fewer data points. This may be achievable without compromising prediction accuracy.  

#### Improve latency (30ms or faster)
Because the model service is stateless, it is easy to host it in the same datacenter as it's consumer, and scale horizontally to provide a sufficiently fast latency (p99 suffers as the load on the service increases due to requests waiting in the queue).

Certain model/dataset combos may simply take a long time to compute results. In this case, there are several possible solutions:  
 - use ML solution that is designed for higher performance
 - use technique such as Singular Value Decomposition to see if some input data can be ignored to reduce calculation time in exchange for a minimal loss in accuracy/precision  
 - pay AWS for machines with faster processors
