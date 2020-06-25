# scraper_dag
A scheduled scraper implemented in Python using mainly Scrapy and Airflow to watch latest prices for your desired ebay products. The Airflow scheduler can be set up on a cheap EC2 free-tier instance, and monitored using the web interface. The prices are loaded onto a PostgreSQL database that you can query and analyse using the Jupyter notebook provided in the `nbs` folder.

## Resouces index
+ `dags`: Contains the airflow DAG to be copied to your `$AIRFLOW_HOME/dags` folder 
+ `ebay_proj`: This is where the `scrapy` spider definition resides, and also contains the operator files for the airflow dag
+ `nbs`: A jupyter notebook file to connect to your PostgreSQL database from your client for ad-hoc querying
+ `figs`: figures for this README

## Setup instructions on host
`TO-DO`


## Setup instructions on client
`TO-DO`


## Expected results on client
Use your laptop client to connect to your AWS EC2 host using a browser at `http://<AWS-ip-address>:8080`. You will be able to see the following. You can manually trigger the DAG to run or let it run according to the set schedule at 16:00 every day by default
![fig_dag](fig/fig_dag.png)

You can also analyse the price trends from the PostgreSQL database. Simply launch a Jupyter notebook server on your laptop and use the notebook provided. Connect to your Amazon RDS set up earlier, by changing the credentials to yours. Then run the queries. You will be able to see the statistics in a graph like the following:
![notebook_fig](fig/fig_nb.png)
