# SQS -> PostgreSQL Data Pipeline

This project fetches messages from an AWS SQS queue, masks PII data, and inserts the processed data into a PostgreSQL database.

## Setup

To set up the project, follow these steps:

1. Clone the repository.
2. Build the Docker containers using `docker-compose build`.
3. Ensure LocalStack and PostgreSQL services are running in Docker.
4. Run the application using `docker-compose up`.


## Usage

To run the application, use the following command:

`docker-compose up`

## Thought process behind the task

1. Create a streamline plan from setting up to adding data into database.
2. Thoroughly understand the requirements of the task.
3. Setup basic tools like Docker, AWS CLI, etc.
4. Understand how data flows from SQS to Postgres with created plan.
5. Implement Dockerfile and Docker compose to define requirements and commands for the task.
6. Connect to AWS Client -> Connect to Postgres -> Prepare the data pipeline in Main file.
7. Flow of Data Pipeline: In loop, Fetch Message -> If message found -> Process and Insert Message (For every message: Validate -> Log -> Mask -> Insert -> Handle Errors)


## Question and Answers:

1. How would you deploy this application in production?

I have already used Docker to containerize my application. I will use Kubernetes for orchestration. Github actions for CI/CD and AWS/GCP for cloud provision.

2. What other components would you want to add to make this production ready?

To make this application production-ready, I will first add API gateway to the application along with a load balancer. We can further define auto-scaling and setup secret management especially if we are using cloud support.

3. How can this application scale with a growing dataset.

We can add additional containers to scale horizontally along with a load balancer which appropriately routes requests. We can also use multiple SQS queues for sending messages and use a caching mechanism for easy-access. In the data pipeline, we can incorporate batch-processing to avoid congestion.

4. How can PII be recovered later on?

We can store the original PII in a secure system and store hashes in an encrypted database. That is how we can recover the original PIIs later.

5. What are the assumptions you made?

Initially, I made the assumption that the data was in correct format. But iterating over my approach, I thought I should implement error-handling to avoid system failure because of incorrect formats which I later encountered in the messages. I have also assumed that hashing is acceptable for masking PIIs as the integrity of the PIIs will remain intact and the analysts can identify duplicate values without exposing them to true PIIs.

For the app_version field, I assumed that taking only the integer value (major version) is sufficient because it ensures consistency in the database. This approach avoids potential issues with varying version formats and focuses on the significant part of the version number.

## Next Steps

Here are some potential improvements that I can make over the existing system:

1. **Error Handling:** Enhance error handling to manage different types of exceptions like network issues and database connectivity problems.
2. **Monitoring and Logging:** Integrate monitoring tools and enhance logging to provide better insights into application performance and issues throughout the process
3. **Scalability:** Explore ways to scale the application, such as adding support for horizontal scaling by adding more containers or exploring other ways.
4. **Testing:** Add unit tests and end-to-end tests to ensure the reliability and stability of the application.
5. **CI/CD Pipeline:** Set up a CI/CD pipeline using Github Actions to automate testing, building, and deployment of the application.

## Conclusion

This assignment was fun and I would love to work on such problems more often. I look forward to any feedback!

## References

1. https://www.freecodecamp.org/news/postgresql-in-python/
2. https://docs.aws.amazon.com/cli/latest/reference/sqs/
3. https://docs.aws.amazon.com/code-library/latest/ug/python_3_sqs_code_examples.html