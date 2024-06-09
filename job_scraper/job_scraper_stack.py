from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
)
from constructs import Construct


class JobTableConstruct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, "JobScraperTableConstruct")

        self.table = dynamodb.Table(
            self,
            id=id,
            table_name=id,
            partition_key={'name': 'job_id', 'type': dynamodb.AttributeType.STRING},
        )


class JobScraperLambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, job_table: dynamodb.Table):
        super().__init__(scope, "JobScraperLambdaConstruct")

        self.function = _lambda.Function(
            self,
            id,
            function_name=id,
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="job_scraper.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                'JOB_TABLE': job_table.table_name
            }
        )



class JobScraperStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        job_table_construct = JobTableConstruct(self, "JobTable")

        job_scraper_lambda_construct = JobScraperLambdaConstruct(
            self,
            "JobScraperLambda",
            job_table=job_table_construct.table
        )

        job_table_construct.table.grant_write_data(job_scraper_lambda_construct.function)

        api = apigateway.LambdaRestApi(
            self, 'API',
            handler=job_scraper_lambda_construct.function,
            proxy=False
        )

        jobs = api.root.add_resource('jobs')
        jobs.add_method('GET')

        api_deployment = apigateway.Deployment(self, "Deployment", api=api)
        stage = apigateway.Stage(self, "Stage", deployment=api_deployment, stage_name="dev")


