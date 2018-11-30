marek.rocks
===========

The sourcecode of my website hosted at https://marek.rocks , which I use for demo's on how high performance, serverless webpages can be built using AWS Lambda.  

The webpage is using an API gateway which forwards to Python Lambda code. The Lambda code automatically retrieves all of the AWS blog posts which are kept in a DynamoDB database. You can include a Lambda layer with the aws-xray-sdk in order to support tracing of the function. 
 

![alt tag](https://raw.githubusercontent.com/marekq/marek.rocks/master/docs/1.png)


Configure the environment variables of the Lambda function as follows;

![alt tag](https://raw.githubusercontent.com/marekq/marek.rocks/master/docs/2.png)


You can find the Lambda code used to populate the DynamoDB here; https://github.com/marekq/rss-lambda


Contact
-------

In case of questions or bugs, please raise an issue or reach out to @marekq!
