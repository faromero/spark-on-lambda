# Spark on Lambda - README
----------------------------------------

## Foreword
This is a fork of the original Spark on Lambda project. It includes updates for 1) the hadoop-lzo dependency, 2) the maximum number of HTTP connections allowed by the HTTP Pool Manager, and 3) unknown hostname in Lambda executor. It also provides more details on how to set up the system. Some parts of the README are borrowed from the original repository.

## Original Introduction
AWS Lambda is a Function as a Service which is serverless, scales up quickly and bills usage at 100ms granularity. We thought it would be interesting to see if we can get Apache Spark run on Lambda. This is an interesting idea we had, in order to validate we just hacked it into a prototype to see if it works. We were able to make it work making some changes in Spark's scheduler and shuffle areas. Since AWS Lambda has a 5 minute max run time limit, we have to shuffle over an external storage. So we hacked the shuffle parts of Spark code to shuffle over an external storage like S3.

This is a prototype and its not battle tested possibly can have bugs. The changes are made against OS Apache Spark-2.1.0 version. We also have a fork of Spark-2.2.0 which has few bugs will be pushed here soon. We welcome contributions from developers.

## Setting up the EC2 and Network Environment
First, you need to set up a VPC, subnets, a NAT Gateway, and an Internet Gateway so that the Lambda can communicate back to the Spark Driver via its Private IP. [This link](https://gist.github.com/reggi/dc5f2620b7b4f515e68e46255ac042a7) provides a great step-by-step guide on how to do this (note that you may need to set up the NAT Gateway before setting up the routing tables instead of at the end). Once this is done, bring up an EC2 machine with AWS credentials to invoke the Lambda functions. The EC2 machine should be in the VPC you just created and the IGW subnet (not the NAT subnet, which will be used for the Lambda function). The security group should allow for all incoming and outgoing traffic.

## Building Spark on Lambda
To compile, use the following command:
```
./dev/make-distribution.sh --name spark-lambda-2.1.0 --tgz -Phive -Phadoop-2.7 -Dhadoop.version=2.6.0-qds-0.4.13 -DskipTests 
```
Due to aws-java-sdk-1.7.4.jar which is used by hadoop-aws.jar and aws-java-sdk-core-1.1.0.jar having compatibility issues, as of now we have to compile using Qubole shaded hadoop-aws-2.6.0-qds-0.4.13.jar.

Spark on Lambda package for driver can be found [here](s3://public-qubole/lambda/spark-2.1.0-bin-spark-lambda-2.1.0.tgz) - This can be downloaded to an EC2 instance where the driver can be launched.

## Lambda Package for Executors
Run the following command from the Spark on Lambda home directory to create the package for Lambda executors to download. It will create directory `lambda/` inside of your bucket and place the package in there.
```
bash -x bin/lambda/spark-lambda <software version> <zip> <bucket>
```
Example:
```
bash -x bin/lambda/spark-lambda 149 spark-2.1.0-bin-spark-lambda-2.1.0.tgz s3://my-spark-bucket/
```

## Setting up the Lambda Function
Create the Lambda function with the name `spark-lambda` from the AWS console using the code in `bin/lambda/spark-lambda-os.py`. Note that this code slighly differs from the original project. The Lambda should be in the same VPC as the EC2 instance, and should use the NAT subnets you previously created. The security group should also match that of the EC2 instance. Finally, the Lambda's role should have permissions for S3, VPC, ENI, and Lambda Execution. You also need to add the following environment variable: `HOSTALIASES=/tmp/HOSTALIASES`


Also if you want to copy the packages to your bucket, use:
```
aws s3 cp s3://s3://public-qubole/lambda/spark-lambda-149.zip s3://YOUR_BUCKET/
aws s3 cp s3://s3://public-qubole/lambda/spark-2.1.0-bin-spark-lambda-2.1.0.tgz s3://YOUR_BUCKET/
```

## Launching a Job
You can launch `spark-shell` or `spark-submit` jobs using the binary found in the `spark-on-lambda/bin/` directory. The most important part of the launch is the configuration options you need to pass. Below are a list of the parameters you should pass either through `spark-defaults.conf` or directly on the command-line using `--conf <configuration parameter>=<value>`. Parameters listed are defaults, with those between `<>` requiring the user to fill in before use.

```
--master lambda://test /* Required for starting the LambdaSchedulerBackend */
--conf spark.dynamicAllocation.enabled=true
--conf spark.dynamicAllocation.minExecutors=2
--conf spark.shuffle.s3.enabled=true
--conf spark.lambda.concurrent.requests.max=100 /* How many requests to concurrently request */
--conf spark.hadoop.fs.s3n.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
--conf spark.hadoop.fs.s3.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
--conf spark.hadoop.fs.AbstractFileSystem.s3.impl=org.apache.hadoop.fs.s3a.S3A
--conf spark.hadoop.fs.AbstractFileSystem.s3n.impl=org.apache.hadoop.fs.s3a.S3A
--conf spark.hadoop.fs.AbstractFileSystem.s3a.impl=org.apache.hadoop.fs.s3a.S3A
--conf spark.hadoop.qubole.aws.use.v4.signature=true
--conf spark.hadoop.fs.s3a.fast.upload=true
--conf spark.lambda.function.name=spark-lambda
--conf spark.lambda.spark.software.version=149 /* Must be the same version as you used in creating the Lambda package */
--conf spark.hadoop.fs.s3a.endpoint=<your-endpoint> /* Depends on where your bucket is located. Defaults to us-east-1. Example for us-west-2: "s3.us-west-2.amazonaws.com" */
--conf spark.hadoop.fs.s3n.awsAccessKeyId=<your-access-key>
--conf spark.hadoop.fs.s3n.awsSecretAccessKey=<your-secret-access-key>
--conf spark.shuffle.s3.bucket=s3://<your-bucket> /* Can be the same as the bucket with the executor package */
--conf spark.lambda.s3.bucket=s3://<your-lambda-bucket> /* Must be the same bucket as you used in creating the Lambda package */
```
If the Spark driver complains about an unknown hostname while running in the VPC, you can do the following:
1) Run `hostname` and copy the output
2) Edit `/etc/hosts` and add the output of `hostname` to the end of the first line (after `localhost`)
Example first line: `127.0.0.1 localhost <output of hostname>`

## References
1. http://deploymentzone.com/2015/12/20/s3a-on-spark-on-aws-ec2/

