Make changes in a branch
When everything is right, Initiate a merge request to the main branch.

Perform the following inside the st_mgt folder(upon running ls,if it should show README.md ; manage.py  ; st_mgt ; student ; task  ;users ===> right directory).
This is required especially for first clone as the Database (db.sqlite3) file must be missing / to be created 
1. "python manage.py check" (You can run this to check for any kind errors whenever you like)
2. "python manage.py makemigrations"
3. "python manage.py migrate" 

The default superuser is admin (pwd:admin123) ,
Incase absent create one by using "python manage.py createsuperuser"
u can access it by http://127.0.0.1:8000/admin as now on running "python manage.py runserver", the webpage is now directed to default login page 
