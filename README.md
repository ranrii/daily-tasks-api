# Project: Daily Task API
An api for creating todo-list like thingy. user can create Topic and Task that associated with topic, with due time and task's status for tracking tasks progression.

For other programming language see: [Postman documentation](https://documenter.getpostman.com/view/28747988/2s9Xy2NBm2)

# Introduction:
This project is an exercise for creating a Flask-based RESTful api server.

# 📁 Collection: Topic 


## End-point: All Topic
returns ALL topic
### Method: GET
>```
>{{api-server}}/topic
>```
### Response: 200
```json
{
    "no_of_topic": 4,
    "topics": [
        {
            "created_at": "2023-08-08T17:07:32+00:00",
            "description": "Just some chores",
            "id": 1,
            "no_of_tasks": 0,
            "tasks": [],
            "title": "Tomorrow's todos"
        },
        {
            "created_at": "2023-08-08T17:34:10+00:00",
            "description": "some description",
            "id": 2,
            "no_of_tasks": 0,
            "tasks": [],
            "title": "2nd Topic"
        },
        {
            "created_at": "2023-08-08T17:34:58+00:00",
            "description": "lorem ipsum....",
            "id": 3,
            "no_of_tasks": 1,
            "tasks": [
                {
                    "created_at": "2023-08-08T23:22:24+00:00",
                    "due_time": "2023-08-09T02:00:00+00:00",
                    "id": 4,
                    "status": "ongoing",
                    "title": "work",
                    "topic_id": 3,
                    "topic_title": "3rd Topic"
                }
            ],
            "title": "3rd Topic"
        },
        {
            "created_at": "2023-08-08T20:54:56+00:00",
            "description": "just chores",
            "id": 4,
            "last_update": "2023-08-08T20:56:44+00:00",
            "no_of_tasks": 3,
            "tasks": [
                {
                    "created_at": "2023-08-08T21:37:46+00:00",
                    "due_time": "2023-08-09T00:00:00+00:00",
                    "id": 1,
                    "last_update": "2023-08-08T23:17:07+00:00",
                    "status": "next",
                    "title": "wake up at 7:00",
                    "topic_id": 4,
                    "topic_title": "Today's TODOs"
                },
                {
                    "created_at": "2023-08-08T22:27:58+00:00",
                    "due_time": "2023-08-09T01:30:00+00:00",
                    "id": 2,
                    "status": "ongoing",
                    "title": "cook food",
                    "topic_id": 4,
                    "topic_title": "Today's TODOs"
                },
                {
                    "created_at": "2023-08-08T22:29:22+00:00",
                    "due_time": "2023-08-09T02:00:00+00:00",
                    "id": 3,
                    "status": "ongoing",
                    "title": "work",
                    "topic_id": 4,
                    "topic_title": "Today's TODOs"
                }
            ],
            "title": "Today's TODOs"
        }
    ]
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Search Topic
returns topic with the title of `title` if exist
### Method: GET
>```
>{{api-server}}/topic/search?title={{topic-title}}
>```
### Query Params

|Param|value|
|---|---|
|title|{{topic-title}}|


### Response: 200
```json
{
    "no_of_topic": 1,
    "topics": [
        {
            "created_at": "2023-08-08T20:54:56+00:00",
            "description": "just chores",
            "id": 4,
            "last_update": "2023-08-08T20:56:44+00:00",
            "no_of_tasks": 3,
            "tasks": [
                {
                    "created_at": "2023-08-08T21:37:46+00:00",
                    "due_time": "2023-08-09T00:00:00+00:00",
                    "id": 1,
                    "last_update": "2023-08-08T23:17:07+00:00",
                    "status": "next",
                    "title": "wake up at 7:00",
                    "topic_id": 4,
                    "topic_title": "Today's TODOs"
                },
                {
                    "created_at": "2023-08-08T22:27:58+00:00",
                    "due_time": "2023-08-09T01:30:00+00:00",
                    "id": 2,
                    "status": "ongoing",
                    "title": "cook food",
                    "topic_id": 4,
                    "topic_title": "Today's TODOs"
                },
                {
                    "created_at": "2023-08-08T22:29:22+00:00",
                    "due_time": "2023-08-09T02:00:00+00:00",
                    "id": 3,
                    "status": "ongoing",
                    "title": "work",
                    "topic_id": 4,
                    "topic_title": "Today's TODOs"
                }
            ],
            "title": "Today's TODOs"
        }
    ]
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Create New Topic
creates new topic

returns new `topic_id` set `include=true` to return said topic.
### Method: POST
>```
>{{api-server}}/topic
>```
### Headers

|Content-Type|Value|
|---|---|
|Content-Type|application/x-www-form-urlencoded|


### Response: 200
```json
{
    "success": "successfully add new topic",
    "topic": {
        "created_at": "2023-08-08T20:54:56+00:00",
        "description": "just chores",
        "id": 4,
        "no_of_tasks": 0,
        "tasks": [],
        "title": "Todat's todos"
    }
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Update Topic
update topic with `topic_id` need to provide either `title` or `description` to update, both could not be the same value as the pre-updated values.

returns updated `topic_id`, set `include=true` to include said topic
### Method: PUT
>```
>{{api-server}}/topic
>```
### Headers

|Content-Type|Value|
|---|---|
|Content-Type|application/x-www-form-urlencoded|


### Response: 200
```json
{
    "success": "successfully updated a topic",
    "topic": {
        "created_at": "2023-08-08T20:54:56+00:00",
        "description": "just chores",
        "id": 4,
        "last_update": "2023-08-08T20:56:44+00:00",
        "no_of_tasks": 0,
        "tasks": [],
        "title": "Today's TODOs"
    }
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Delete Topic
deletes **Topic and Tasks** associated with `topic_id`, the `title` is required to prevent accidental removal

returns `topic_id`,`title`, number of tasks removed and `orphaned_tasks` if there's any child task(s) left
### Method: DELETE
>```
>{{api-server}}/topic
>```
### Headers

|Content-Type|Value|
|---|---|
|Content-Type|application/x-www-form-urlencoded|


### Response: 200
```json
{
    "removed_topic": {
        "id": 3,
        "title": "3rd Topic"
    },
    "success": "successfully removed a topic and all tasks associated with it",
    "tasks_removed": 1
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃
# 📁 Collection: Task 


## End-point: Search Task
search task by `title`, can be narrowed down with `topic_id`

returns task
### Method: GET
>```
>{{api-server}}/task/search?title={{task-title}}&topic_id={{topic-id}}
>```
### Query Params

|Param|value|
|---|---|
|title|{{task-title}}|
|topic_id|{{topic-id}}|


### Response: 200
```json
{
    "results": 2,
    "tasks": [
        {
            "created_at": "2023-08-08T22:29:22+00:00",
            "due_time": "2023-08-09T02:00:00+00:00",
            "id": 3,
            "status": "ongoing",
            "title": "work",
            "topic_id": 4,
            "topic_title": "Today's TODOs"
        },
        {
            "created_at": "2023-08-08T23:22:24+00:00",
            "due_time": "2023-08-09T02:00:00+00:00",
            "id": 4,
            "status": "ongoing",
            "title": "work",
            "topic_id": 3,
            "topic_title": "3rd Topic"
        }
    ]
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: All task
returns ALL tasks in the topic: `topic_id`
### Method: GET
>```
>{{api-server}}/topic/{{topic-id}}/task
>```
### Response: 200
```json
{
    "num_of_tasks": 3,
    "tasks": [
        {
            "created_at": "2023-08-08T21:37:46+00:00",
            "due_time": "2023-08-09T00:30:00+00:00",
            "id": 1,
            "status": "ongoing",
            "title": "Wake up early",
            "topic_id": 4,
            "topic_title": "Today's TODOs"
        },
        {
            "created_at": "2023-08-08T22:27:58+00:00",
            "due_time": "2023-08-09T01:30:00+00:00",
            "id": 2,
            "status": "ongoing",
            "title": "cook food",
            "topic_id": 4,
            "topic_title": "Today's TODOs"
        },
        {
            "created_at": "2023-08-08T22:29:22+00:00",
            "due_time": "2023-08-09T02:00:00+00:00",
            "id": 3,
            "status": "ongoing",
            "title": "work",
            "topic_id": 4,
            "topic_title": "Today's TODOs"
        }
    ]
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Create New Task
### Method: POST
>```
>{{api-server}}/topic/{{topic-id}}/task
>```
### Headers

|Content-Type|Value|
|---|---|
|Content-Type|application/x-www-form-urlencoded|


### Response: 200
```json
{
    "success": "successfully added a new task with task id=3 for topic id=4",
    "task": {
        "created_at": "2023-08-08T21:33:50+00:00",
        "due_time": "2023-08-09T00:30:00+00:00",
        "id": 3,
        "status": "ongoing",
        "title": "Wake up early",
        "topic_id": 4,
        "topic_title": "Today's TODOs"
    }
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Update task
update task with `task_id` need to provide at least one of the following: `title`, `due_time` or `status` to update, all could not be the same as pre-updated values.
### Method: PUT
>```
>{{api-server}}/topic/{{topic-id}}/task
>```
### Headers

|Content-Type|Value|
|---|---|
|Content-Type|application/x-www-form-urlencoded|


### Response: 200
```json
{
    "success": "successfully updated a task",
    "task": {
        "created_at": "2023-08-08T21:37:46+00:00",
        "due_time": "2023-08-09T00:00:00+00:00",
        "id": 1,
        "last_update": "2023-08-08T23:17:07+00:00",
        "status": "next",
        "title": "wake up at 7:00",
        "topic_id": 4,
        "topic_title": "Today's TODOs"
    }
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃

## End-point: Delete task
remove task inside topic: `topic_id` with the `task_id` value
### Method: DELETE
>```
>{{api-server}}/topic/{{topic-id}}/task
>```
### Headers

|Content-Type|Value|
|---|---|
|Content-Type|application/x-www-form-urlencoded|


### Response: 200
```json
{
    "success": "successfully removed a task",
    "task": {
        "id": 4,
        "title": "work"
    }
}
```


⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃ ⁃
_________________________________________________
Powered By: [postman-to-markdown](https://github.com/bautistaj/postman-to-markdown/)
