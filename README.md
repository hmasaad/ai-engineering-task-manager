# AI Engineering Task Manager

A local page for giving one task to a model. The model reads one file and returns the new text of one file. An existing file stays unchanged until you approve the reply.

The server listens on `127.0.0.1` only.

## When to start it

Start the task manager when you want a model to work on a project that already exists on this machine.

Start it from inside that project. A relative project name, including `.`, is resolved from the directory where the server was started. `~` is not expanded.

Keep the workspace file outside that project. The workspace is the SQLite file that stores the model service, the tasks, and the replies.

Leave the server running while you review the reply, approve it, and mark the task completed. Stop it when you are finished with that project. Start it again after you change this repository, so the running process loads the new code.

One start works on one file. Start the server once, then use Instructions for each task.

## First-time setup

From this repository:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Start the server

From the project you want to change:

```bash
cd /path/to/the/project

"$HOME/Documents/GitHub/ai-engineering-task-manager/.venv/bin/python" -m task_manager \
  --workspace "$HOME/task-workspaces/my-project.db" \
  --engineer "Your name" \
  --assistant "Guide" \
  --port 8000
```

Then open [http://127.0.0.1:8000/instructions](http://127.0.0.1:8000/instructions).

Leave `--model-name` and `--model-text` off. Those flags return one fixed sentence and ignore the model service saved on the Instructions page.

| Flag | Meaning |
|---|---|
| `--workspace` | Path to the SQLite file. The folder is created if it does not exist. |
| `--engineer` | Name stored on your approvals and checks. |
| `--assistant` | Name stored on the model's change. |
| `--port` | Port on this machine. The default is `8000`. |

## Save the model

On Instructions, fill in the model section and press **Save model** before starting work.

| Field | What to enter |
|---|---|
| Model name | The model id the service expects. |
| Model address | The service address, ending in `/v1`. A local Ollama service is `http://127.0.0.1:11434/v1`. |
| API key | Leave this blank for a local service that does not require a key. |

The address must start with `http://` or `https://`. The key is sent only to that service. It is not stored in the prompt.

## Start one task

Still on Instructions, fill in the task and press **Start work**.

| Field | What to enter |
|---|---|
| Title | Short name of the task. |
| Goal | What the change should achieve. |
| Acceptance criterion | The check you will verify later. |
| Project | `.` when the server was started inside the project. Otherwise the full path of an existing directory. |
| File to read | A file that already exists inside the project, such as `lib/main.dart`. |
| File to change | The file the model should return. Use the same path to revise an existing file. A new path creates a new file. |
| Ordinary or consequential | Choose one. Replacing an existing file still waits for approval. |
| What changed | The edit, in plain language. The model receives this with the current file text. Example: `Change the heading to Mark Attendance`. |

Starting work reads the file once and asks the model once. The task opens In Progress.

- A new ordinary file is written with the model's reply.
- An existing file is left as it is. The task shows the reply and waits for approval.

Read the reply on the task page before you approve. Approval replaces the whole file with that reply. It does not call the model again. If the reply is wrong, press **Mark not carried out** and give a reason.

## Finish the task

On the task page, after a reply you accept:

1. In **Evidence reviewed**, write what you checked, then press **Approve change**.
2. On the acceptance criterion, fill in **What was observed**, **Verification method**, and **Test-run identifier**, check **This criterion passed**, and press **Verify criterion**.
3. On the carried-out change, record a check that passed.
4. Press **Mark completed**.

The task stays In Progress until the criterion is verified and the carried-out change has a passing check.

## Paths

- **Project** is a directory. `lib/main.dart` is not a project.
- **File to read** and **File to change** are paths inside that directory. `lib/main.dart` is a file. `main.dart` is a different file, at the project root.
- The project directory must already exist. The file to read must already exist. The file to change may be new.

## Messages

| Message | What to fix |
|---|---|
| `The project must already exist.` | Project is not an existing directory. Use `.` or a full path. |
| `The file must already exist.` | File to read is not a file inside that project. |
| `Choose the model this change uses.` | Press **Save model** before **Start work**. |
| `Name the model service.` | Model address is blank or does not start with `http://` or `https://`. |
| `The model service could not be reached.` | The address is wrong, or the model service is not running. |
| `The model did not return file text.` | The service answered, but the reply was empty. |

## Checks

From this repository:

```bash
.venv/bin/pytest
```
