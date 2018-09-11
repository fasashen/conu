import logging

from conu.backend.origin.backend import OpenshiftBackend
from conu.backend.docker.backend import DockerBackend
from conu.utils import run_cmd


api_key = run_cmd(["oc", "whoami", "-t"], return_output=True).rstrip()
with OpenshiftBackend(api_key=api_key, logging_level=logging.DEBUG) as openshift_backend:

    with DockerBackend() as backend:
        python_image = backend.ImageClass("centos/python-36-centos7", tag="latest")
        psql_image = backend.ImageClass("centos/postgresql-96-centos7", tag="9.6")

        openshift_backend.login_to_registry('developer')

        app_name = openshift_backend.new_app(
            image=python_image,
            template="https://raw.githubusercontent.com/sclorg/django-ex"
                     "/master/openshift/templates/django-postgresql.json",
            oc_new_app_args=["-p", "SOURCE_REPOSITORY_REF=master",  "-p", "PYTHON_VERSION=3.6",
                             "-p", "POSTGRESQL_VERSION=9.6"],
            name_in_template={"python": "3.6"},
            other_images=[{psql_image: "postgresql:9.6"}],
            project='myproject')

        try:
            openshift_backend.wait_for_service(
                app_name=app_name,
                expected_output='Welcome to your Django application on OpenShift',
                timeout=300)
        finally:
            openshift_backend.clean_project(app_name)
