# High level design

- the front end sends an object from input:

```json
{
  "role": "",
  "task": "",
  "constraints": "",
  "personality": "",
  "output":""
}
```

- the response will be full markdown text with the contents from the input object inserted into respective sections:

```markdown
# Role
{role}

# Task
{task}

# Constraints
{constraints}

# Personality
{personality}

# Output
{output}
```

**end points** :

- API_BASE_URL: "api/v1/pc/"

- main page : GET:  /API_BASE_URL/get_started" : shows the main page with examples and input form only get request.

- process page : POST:  "/API_BASE_URL/process" : takes the input object and returns the markdown text.

- health check : GET:  "/API_BASE_URL/health" : returns status 200 if the service is up and running.
