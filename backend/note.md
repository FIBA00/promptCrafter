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

## PromptCrafter / main service

- main page : GET:  /API_BASE_URL/main/get_started" : shows the main page with examples and input form only get request.

- process page : POST:  "/API_BASE_URL/main/process" : takes the input object and returns the markdown text.

- health check : GET:  "/API_BASE_URL/main/health" : returns status 200 if the service is up and running.

### PromptCrafter / user service

- main page : GET:  "/API_BASE_URL/user/{user_id}" : shows the user profile page with user details and history only get request.

- update page : POST:  "/API_BASE_URL/user/{user_id}" : takes the user object and updates the user details.

- history page : GET:  "/API_BASE_URL/user/{user_id}" : shows the user history page with list of previous prompts and responses.

- delete history : DELETE:  "/API_BASE_URL/user/{user_id}/history/{history_id}" : deletes a specific history entry for the user.

users:
    - list, create, get one, update, delete
