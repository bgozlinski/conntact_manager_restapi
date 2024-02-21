# FastAPI and SQLAlchemy project
This project is a web-based application designed for managing contacts. It leverages modern Python frameworks and 
libraries to provide a robust backend system that handles CRUD operations (Create, Read, Update, Delete) for 
contact entities. Utilizing SQLAlchemy for database operations, Pydantic for data validation, and FastAPI for 
the web framework, it offers a scalable solution for contact management.

## Dependencies
* SQLAlchemy
* Pydantic
* FastAPI
* JSON Web Token

## Features

* Contact Management: Create, read, update, and delete contacts with fields such as name, email, and phone number.
* Database Integration: Uses SQLAlchemy for efficient database management and operations.
* Data Validation: Implements schemas for request and response validation, ensuring data integrity.
* Contacts are viewed and managed only by authorized User.

Clone the project repository:
```bash
git clone https://github.com/bgozlinski/django-quotes.git
cd django-quotes
```

Install the required packages:
```bash
pip install -r requirements.txt
```

Run docker-compose
```bash
sudo docker-compose up -d
```

## Configuration

### Environment Variables

For security reasons, it's recommended to use environment variables for sensitive information like database credentials:
For more view visit [.env Template](.env.dist)

## Usage

To start program run main.py file

```bash
python main.py
```

Navigate to the URL (e.g., `http://localhost:8000/docs `).


## License

This project is licensed under the [MIT License](LICENSE).

