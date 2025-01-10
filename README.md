# Venom Project README ✨🔧🚀

Follow these steps to set up and run the Venom project on your local machine. 🌟👨‍💻

---

## 1. Check Prerequisites ⚙️✅🔍  
Ensure the following commands work in your terminal to verify that the necessary tools are installed. If not, download and install them:

- Python: `python --version`  
- Pip: `pip --version`  
- Git: `git --version`

---

### If Prerequisites Are Missing 🛠️💡
If any of the prerequisites are not installed, follow these links to install them:

- [Download Python](https://www.python.org/downloads/) 🐍
- [Download Pip (included with Python)](https://pip.pypa.io/en/stable/installation/) 📦
- [Download Git](https://git-scm.com/downloads) 🌐

After installing, recheck the commands to ensure everything works.

---

## 2. Clone the Repository 🐍📦💻  
If you haven’t already, clone the repository:  
```bash
git clone https://github.com/YousefZahran1/venom_project.git
```
Navigate to the project directory: 🚀📁✨  
```bash
cd Django-Poll-App
```

---

## 3. Set Up a Virtual Environment 🛠️🌐💻  

Create a virtual environment:  
```bash
python -m venv venv
```

Activate the virtual environment:  
- **Windows:**  
  ```bash
  venv\\Scripts\\activate
  ```  
- **macOS/Linux:**  
  ```bash
  source venv/bin/activate
  ```

---

## 4. Install Dependencies 📥📚⚙️  
Ensure you are in the project directory and install the required packages:  
```bash
pip install -r requirements.txt
```

---

## 5. Apply Migrations 🗂️📊🔄  
Run the migrations to set up the Django database:  
```bash
python manage.py migrate
```

---

## 6. Create a Superuser (for Admin Access) 👤🔐⚙️  
To access the admin panel, create a superuser account:  
```bash
python manage.py createsuperuser
```
You will be prompted to enter a username, email, and password. Remember these credentials. 📝✅🔒

---

## 7. Start the Django Server 🌐🚀⚡  
Start the Django development server:  
```bash
python manage.py runserver
```

---

## 8. Access the Web Application 🌍🖥️🔗  
- Open your browser and navigate to:  
  - **Normal website:** [http://127.0.0.1:8000](http://127.0.0.1:8000)  
  - **Admin panel:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)  

You can now use the application as a normal user or log in to the admin panel using the superuser credentials you created. 🔑👨‍💻🎉

---

Follow these instructions carefully, and you will have the Venom project up and running successfully. 🎯🚀💪
