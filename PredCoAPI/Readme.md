# PredCoAPI

This repository contains the source code for the PredCoAPI project, which is an API implementation for the PredCo application.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)

## Description

PredCoAPI is a Django-based API project that serves as the backend for the PredCo application. It provides endpoints to manage and retrieve data related to predictions.

The main features of PredCoAPI include:

- User authentication and authorization using JSON Web Tokens (JWT)
- Endpoints for creating, updating, and retrieving prediction data
- Integration with external data sources

## Installation

To set up and run PredCoAPI locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/PriyanshNegi/PredCoAPI.git
   ```

2. Change into the project directory:

   ```bash
   cd PredCoAPI
   ```

3. (Optional) Create and activate a virtual environment :
   
   For MAC OS
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   For Windows
   ```bash
   python -m venv venv
   venv/Scripts/activate
   ```

5. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Apply the database migrations:

   ```bash
   python manage.py migrate
   ```

7. Create Superuser
   
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server:

   ```bash
   python manage.py runserver
   ```

The API should now be accessible at `http://localhost:8000/`.


For detailed API documentation and usage examples, please refer to the [API documentation](API_DOCUMENTATION.md) file.

## Contributing

Contributions to PredCoAPI are welcome! If you would like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add your commit message"
   ```
4. Push the branch to your forked repository:
   ```bash
   git push 
   ```
5. Open a pull request on the main repository.

Please make sure to follow the existing code style and include tests and documentation for your changes.

