# Browser Automation Demo

Asks a human for a Connic account email, password, and project title, then opens [connic.co](https://connic.co), signs in, and creates a project using **Deploy via CLI**. The agent returns the new project's name and URL.

```bash
pip install connic-composer-sdk
connic init my-project --templates=browser-automation-demo   # new project
connic init . --templates=browser-automation-demo            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/reference/cli)

## How it works

1. `get_connic_email` asks for the Connic account email.
2. `get_connic_password` asks for the account password in a masked input.
3. `get_project_title` asks for the title of the new project.
4. The agent opens the Connic homepage, finds the sign-in flow, and enters the supplied credentials.
5. It navigates to project creation, chooses **Deploy via CLI**, and creates a project with the supplied title.
6. It returns the created project's name and URL.

The prompt describes the task. The agent chooses the browser actions from the page it sees.

## Connic features used

| Feature | Where |
|---------|-------|
| `approval.inputs` | Collects the email, password, and project title during the run |
| Sensitive human input | Masks the password, encrypts it at rest, and redacts its exact value from captured traces and logs |
| Browser tools | `web_browser_*` enables the complete browser toolkit |

## Run it

Follow the [Connic quickstart](https://connic.co/docs/v1/quickstart) to run the agent in your project. Start `browser-automation-demo` and leave the input empty.

The run pauses for each required value. Open the pending request in Connic, provide the email, password, and project title, then submit each response. The password field is masked. The agent resumes from the same run and performs the browser workflow.

The result contains the new project's name and URL. For example:

```text
Created project "Browser Automation Demo":
https://connic.co/projects/PROJECT_ID
```

The response is ordinary text; its wording can vary.

## Credential handling

The email and project-title requests use normal text fields. The password input uses `sensitive: true`: its field is masked, its response is encrypted at rest for pause and resume, and its exact value is redacted from captured traces and logs, including later browser-tool calls that use it. The model and the sign-in page still receive the password so they can complete the requested login. Use a dedicated, least-privilege test account rather than an administrator account.

Do not place real credentials in the initial payload, prompt, project title, or repository files.

The demo collects an email and password. Accounts that need additional sign-in steps may require adapting the workflow. Browser state is not persisted between runs.

## Checking a run

Validate the agent configuration locally:

```bash
connic lint
```

This checks the configuration without signing in or creating a project. To check the browser workflow, run the agent with a test account, answer the three input requests, and open the returned URL to confirm that the new project has the requested name. The run trace shows the browser actions and their results.

## Structure

```
browser-automation-demo/
  agents/
    browser-automation-demo.yaml
  README.md
  requirements.txt
```

## Adapting the workflow

- Change the target website and task in the agent prompt.
- Adjust the human inputs to collect the values that task needs.
- Keep `web_browser_*` to make the full browser toolkit available.
