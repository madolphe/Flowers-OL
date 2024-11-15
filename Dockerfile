# syntax=docker/dockerfile:1
FROM python:3.8.20-bookworm

# Copy uv from its repository
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Add project files to the container
ADD . /src
WORKDIR /src


# Declare build arguments
ARG DJANGO_SECRET_KEY
ARG DJANGO_SUPERUSER_USERNAME
ARG DJANGO_SUPERUSER_PASSWORD
ARG DJANGO_SUPERUSER_EMAIL

# Set environment variables using the build arguments
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
ENV DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
ENV DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}

# Print environment variables to verify
RUN echo "DJANGO_SECRET_KEY is set to ${DJANGO_SECRET_KEY}"
RUN echo "DJANGO_SUPERUSER_USERNAME is set to ${DJANGO_SUPERUSER_USERNAME}"
RUN echo "DJANGO_SUPERUSER_PASSWORD is set to ${DJANGO_SUPERUSER_PASSWORD}"
RUN echo "DJANGO_SUPERUSER_EMAIL is set to ${DJANGO_SUPERUSER_EMAIL}"

# Create the static directory
RUN mkdir -p /src/flowers-ol/static

# Install dependencies using uv
RUN uv sync --frozen

# Run deployment tasks (like migrations, collectstatic, etc.)
RUN uv run ./flowers-ol/scripts/deploy.py -a

# Expose the application port
EXPOSE 8000

WORKDIR /src/flowers-ol/

# Run Gunicorn instead of Django's development server
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "flowers-ol.wsgi:application"]