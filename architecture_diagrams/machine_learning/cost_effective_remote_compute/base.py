from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.custom import Custom
from diagrams.generic.storage import Storage
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import Client
from diagrams.onprem.container import Docker
from diagrams.onprem.vcs import Github


def Gradle(description: str) -> Custom:
    return Custom(
        description,
        "./architecture_diagrams/machine_learning/cost_effective_remote_compute/LOGO-GRADLE-STACK_RGB.png",
    )


def Terraform(description: str) -> Custom:
    return Custom(
        description,
        "./architecture_diagrams/machine_learning/cost_effective_remote_compute/HashiCorp Terraform.png",
    )


def main():
    with Diagram(
        "Machine Learning - Cost Effective - Remote Compute",
        filename="base",
        outformat="png",
        direction="TB",
        graph_attr={"nodesep": "1.0"},
    ):
        developer = Client("Developer")

        source_code = Cluster("Source Code")
        with source_code:
            main_repo = Github("Main ML Mono-repo (Training/Inference)")

            main_repo - developer

        ci_cd = Cluster("GitHub Actions")
        with ci_cd:
            validation_wf = GithubActions("Validation CI")
            deployment_wf = GithubActions("Deployment CD")

            main_repo >> validation_wf
            validation_wf >> deployment_wf

        containers = Docker("Containers")

        terraform_scripts = Terraform("Terraform Deployments")
        terraform_scripts >> containers

        deployment_wf >> terraform_scripts

        storage = Cluster("Storage")
        with storage:
            training_data = SimpleStorageServiceS3("Training Data")
            model_weights = SimpleStorageServiceS3("Model Weights")

        remote_compute = Cluster("Remote Compute")
        with remote_compute:
            training_compute = EC2("Training VM")
            inference_compute = EC2("Inference VM")

            terraform_scripts >> [training_compute, inference_compute] << containers

        training_data >> training_compute >> model_weights
        model_weights >> inference_compute

        gradle_scripts = Cluster("Gradle Scripts")
        with gradle_scripts:
            gradle_terraform_scripts = Gradle("Run Terraform")
            gradle_storage_scripts = Gradle("Run S3 Sync")
            gradle_containers_scripts = Gradle("Build Containers")

            developer >> gradle_terraform_scripts >> terraform_scripts
            developer - gradle_storage_scripts >> training_data

            model_weights >> gradle_storage_scripts

            gradle_containers_scripts >> containers


if __name__ == "__main__":
    main()
