marek.rocks
===========

The sourcecode of my serverless demo website which I use to demonstrate how high performancewebpages can be built using AWS. You can view the demo website on this URL; https://marek.rocks/

The webpage is using an API gateway which forwards to Lambda running Python. The Lambda code retrieves all AWS blog posts from a DynamoDB database, for which you can find the sourcecode here; https://github.com/marekq/rss-lambda

The webpage uses the following serverless components whenever a visitor opens it; 


![alt tag](https://raw.githubusercontent.com/marekq/marek.rocks/master/docs/1.png)


Installation
------------

Configure the environment variables of the Lambda function as follows;


![alt tag](https://raw.githubusercontent.com/marekq/marek.rocks/master/docs/2.png)



Contact
-------

In case of questions or bugs, please raise an issue or reach out to @marekq!