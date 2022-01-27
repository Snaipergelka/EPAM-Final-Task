# EPAM-Final-Task: API for indexing folders and files

#About
The main idea of this project is to implement a service which can collect 
aggregated statistics for a particular folder.

You can get the following statistics: 
- list of files and folders,
- number of files,
- most and least frequent words,
- average word length,
- vowels and consonants statistics,
- syllables statistics.

#How to start
To start this application you need to start docker compose by command: 
```
docker-compose up
```

#Supported features and examples of use
The service provides an API you can interact with
## Show supported extensions 
```
GET /api/supported_extensions
```
## Start folder analyze 
```
POST api/start
```
You should pass JSON in the following format 
```
{
    "directory": "str", 
    "extensions": ["str"]
}

Example:
{
    "directory": "test\final_task",
    "extensions": [".py", ".txt"]
}
```
## Show information about all folders: 
```
GET /api/directory
```
## Show specific folder information
```
GET /api/directory/slugged_directory_path
```
### How to get slug for a directory 
If you use Python:
```
path.replace(".", "/").replace("/", "_")
```
Also, you can get an example of a slug via `GET /api/directory`

## Show information about all files 
```
GET /api/file
```
## Show information about specific file: 
```
GET /api/file/slugged_file_path
```
### How to make slug?
If you use Python:
```
path.replace(".", "/").replace("/", "_")
```
Also, you can get an example of a slug via `GET /api/file`

## Show word statistics
```
GET /api/word/word
```

# Implementation details
It is A Django project, which consists of two applications 
- Background parser `final_task\background_parser`
- API for files and dirs `final_task\api_for_files_and_dirs`

## Background parser
Application consists of
- **Walker** `final_task\background_parser\walker.py` - this file includes function that 
returns generator of paths of files and folder from top folder.
- **Opener** `final_task\background_parser\opener.py` - this file consists of a function that 
opens files with different extensions.
- **Aggregators** `final_task\background_parser\aggregators.py` - this file consists of functions 
that aggregates all files statistics into folder statistic and pushes it into database. 
- **File analyzer** `final_task\background_parser\file_analyzer.py` - this file consists of functions 
that takes file statistics from parser.py and pushes it to database. 
- **FS analyzer** `final_task\background_parser\fs_analyzer.py` - contain function to start analysis 
- **Parser** `final_task\background_parser\parser.py` - collects all info about files
