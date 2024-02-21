FROM nvcr.io/nvidia/pytorch:24.01-py3

ENV PYTHON_VERSION=3.10

RUN python -m pip install --upgrade pip

RUN apt-get update && apt-get -y install --no-install-recommends postgresql-client

CMD dbt deps --project-dir /workspaces/sql-gen/dbt_project && dbt build --project-dir /workspaces/sql-gen/dbt_project --profiles-dir /workspaces/sql-gen/dbt_project/profiles && sleep infinity
CMD ["/bin/bash"]