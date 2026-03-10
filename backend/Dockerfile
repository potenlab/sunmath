FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ${LAMBDA_TASK_ROOT}/app/

# Copy GCP service account credentials if present
COPY google.jso[n] ${LAMBDA_TASK_ROOT}/

CMD ["app.main.handler"]
