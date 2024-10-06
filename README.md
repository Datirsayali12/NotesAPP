
# NotesApp

NotesApp is a simple API-based application that allows users to create notes, search notes, summarize notes, and ask questions based on stored information. The app used ChromaDB for efficient search  and postgresql for data storage and  also supports file uploads for question answering.

## Features
- **Create Notes**: Add new notes with title and content.
- **Search Notes**: Perform searches on stored notes and retrieve relevant results.
- **Summarize Notes**: Summarize the content of specific notes based on their ID.
- **Get Information**: Search for information or answers to user queries on any topic.
- **Question-Answer**: Upload a file and ask questions based on the content of the file.

## Prerequisites
Before running the application, ensure that you have the following installed:
- Python 3.x
- PostgreSQL (or any other supported database)
- ChromaDB (for handling data storage and search functionality)
- Required Python packages (see `requirements.txt`).


## Getting Started

To get started with this repository, follow these steps:

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Datirsayali12/NotesAPP.gite 

2. Navigate to the cloned repository:

    ```bash
    cd NotesAPP
    ```

3. Create virtual enviroment and activate 
     ```bash
    python -m venv venv
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

  
## API Reference


```http
    POST /create-note

```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `title` | `string` | **Required**. title of note |
|   `notes`|  `string` |  **Required**. content of note |


```http
  POST /search-notes

```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `query`   |  `string` | **Required**. Search query term |

```http
  POST /summarize-notes


```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `note_id`      | `int` | **Required**. id of note |

```http
  POST /get-info

```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `query`      | `string` | **Required**. search query term |



```http
  POST /question-answer


```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `file`      | `file` | **Required**. file to upload |
 | `question`  | `string`  | **Required**. question on file |






