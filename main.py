from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import psycopg2

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        dbname='employee_db',
        user='postgres',
        password='postgres123',
        port=5432
    )
    return conn

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/register")
async def post_register(
    EId: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: int = Form(...),
    password: str = Form(...),
    designation: str = Form(...),
):
    # Open database connection
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert the user into the database
        sql_insert_query = '''INSERT INTO employee (id, name, email, phone, password, designation) 
                              VALUES (%s, %s, %s, %s, %s, %s)'''
        cur.execute(sql_insert_query, (EId, name, email, phone, password, designation))
        conn.commit()

    except Exception as error:
        print(f"Database Error: {error}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return RedirectResponse("/", status_code=303)

def create_employee_table():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql_create_query = ''' CREATE TABLE IF NOT EXISTS employee (
                                id INT PRIMARY KEY,
                                name VARCHAR(40) NOT NULL,
                                email VARCHAR(40),
                                phone INT,
                                password VARCHAR(40),
                                designation VARCHAR(40)
                              )'''
        cur.execute(sql_create_query)
        conn.commit()
    except Exception as error:
        print(f"Table Creation Error: {error}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.post("/login")
async def post_login(email: str = Form(...), password: str = Form(...)):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query to check the login credentials
        sql_select_query = '''SELECT id, name, email, phone, designation FROM employee WHERE email = %s AND password = %s'''
        cur.execute(sql_select_query, (email, password))
        employee = cur.fetchone()

        if employee:
            # Store the logged-in employee details
            global logged_in_employee
            logged_in_employee = {
                "id": employee[0],
                "name": employee[1],
                "email": employee[2],
                "phone": employee[3],
                "designation": employee[4]
            }
            # Redirect to details page
            return RedirectResponse(url="/details", status_code=303)
        else:
            return {"error": "Invalid email or password"}
        
    except Exception as error:
        print(f"Database Error: {error}")
        return {"error": "An error occurred during login"}
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.get("/details", response_class=HTMLResponse)
async def get_employee_details(request: Request):
    # Display the logged-in employee's details
    if logged_in_employee:
        return templates.TemplateResponse("details.html", {"request": request, "employee": logged_in_employee})
    else:
        return {"error": "No employee is logged in."}
    
#--------------------------------------------------------------------
