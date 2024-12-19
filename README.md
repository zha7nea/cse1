CALL CENTRE MANAGEMENT 

1. Call Centre Management is a system to streamline customer interactions, ensure efficient call tracking, and provide actionable insights for performance analysis. It includes functionalities for call tracking, customer management,reference data management, and reports.  
2. Packages that need to be installed:  
   Pip install \-r requirements.txt

3. Configuration  
   app.config\['SQLALCHEMY\_DATABASE\_URI'\] \= 'mysql+pymysql://root:root@127.0.0.1/callcenterdb'  
     
4. Database\_url   
   [https://fordnox.github.io/databaseanswers/data\_models/crm/call\_centre\_conceptual\_erd.htm](https://fordnox.github.io/databaseanswers/data_models/crm/call_centre_conceptual_erd.htm)  
   Secret key \= “”  
   

API ENDPOINTS:  
Here’s the table of endpoints based on the uploaded documentation:

| Method | Endpoint | Description | Roles Required |
| ----- | ----- | ----- | ----- |
| **GET** | `/customers` | Fetch all customers. | `admin`, `agent` |
| **GET** | `/customers/<customer_id>` | Fetch details of a specific customer by ID. | `admin`, `agent` |
| **POST** | `/customers` | Create a new customer. | `admin`, `agent` |
| **PUT** | `/customers/<customer_id>` | Update details of a specific customer. | `admin`, `agent` |
| **DELETE** | `/customers/<customer_id>` | Delete a specific customer. | `admin` |
| **POST** | `/customer_calls` | Log a new call for a customer. | `admin`, `agent` |
| **GET** | `/customer_calls/<call_id>` | Fetch details of a specific call by ID. | `admin`, `agent` |
| **DELETE** | `/customer_calls/<call_id>` | Delete a specific call. | `admin` |
| **GET** | `/ref_call_outcomes` | Fetch all possible call outcomes. | `admin`, `agent` |
| **GET** | `/ref_call_status` | Fetch all possible call statuses. | `admin`, `agent` |

TESTING============================================================

1. Make sure the pytest package\[pip install pytest\] is installed  
2. Run the tests: Run the following command to execute the test suite: pytest \--cov

Git Commit Guidelines  
feat: add customer API endpoint  
fix: resolve database connection issue  
docs: update API documentation  
test: add user registration tests

Use conventional commits:  
feat:  Implement GET, POST, and DELETE routes for customer management.  
\- Add validation for input fields.  
fix:  Fix intermittent database connection errors during high load  
docs: Include examples for new authentication endpoints.  
test:  Add unit tests for user registration validation.

