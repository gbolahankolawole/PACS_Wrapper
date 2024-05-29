# PACS_Wrapper
Wrapper for PACS server on Xcel Solutions project implemented as a flask web service 

## STEPS TO REPLICATE
- clone the repo
    ``` 
    git clone https://github.com/gbolahankolawole/PACS_Wrapper.git
    ```
- create a virtual environment
    ```
    python3.9 -m venv venv
    ```
- activate the virtual environment
    ```
    source venv/bin/activate
    ```
- install the dependencies and libraries
    ```
    pip install -r requirements.txt
    ```
- run the application
    ```
    python run.py
    ```
    You should see the homepage as below

    ![homepage image][homepage]

- Clicking the API Documentation link displays the Swagger documentation that the user can test the endpoints with

    ![documentationpage image][documentationpage]

[homepage]: home_page.png
[documentationpage]: documentation_page.png