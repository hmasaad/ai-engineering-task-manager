# Contract: Model files on the task detail page

Extends the feature 007 task detail page. No new page.

## Task detail

An assistant change that has a model shows the model name and the returned text, in addition to the file line. Changes with no model show no model line.

| Action | Shown when | Command |
|---|---|---|
| Ask the model for a file, with a project, a class, an account, a file path, a stored file read, and a stop choice | The task is In Progress | Ask the model |

The form has no file-text field. The file-read choice lists the stored reads on that task. A refusal redisplays the API message. A success redisplays the detail. A Cancelled task shows a stored model line and does not offer the form.

The assistant-change form still submits the engineer's file text and does not call the model.

## What the pages do not do

The pages do not call the model except through this command. They do not call it again when the task is opened, approved, or declined. They do not let the assistant approve or decline.
