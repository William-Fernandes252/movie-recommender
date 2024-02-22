ARG pythonVersion=3.11.8-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${pythonVersion} as python

# Set default build arguments
ARG poetryVersion=1.5.0
ARG appHome=/app
ARG buildEnv=development

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${buildEnv}
ENV POETRY_VERSION ${poetryVersion}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential \
    # psycopg dependencies
    libpq-dev \
    # Translations dependencies
    gettext \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to cache them in docker layer
COPY requirements/base.txt ${appHome}/requirements/base.txt
COPY requirements/${buildEnv}.txt ${appHome}/requirements/${buildEnv}.txt

# Set the working directory
WORKDIR ${appHome}

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r ${appHome}/requirements/${buildEnv}.txt

# Copy the entrypoint script
COPY ./docker/${BUILD_ENV}/django/entrypoint.sh /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

# Copy the start script
COPY ./docker/${buildEnv}/django/start.sh /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# Copy application code to WORKDIR
COPY . ${appHome}

ENTRYPOINT ["/entrypoint"]
