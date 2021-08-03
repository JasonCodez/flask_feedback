from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "mysupersecretkey"

connect_db(app)

@app.route('/')
def home():

   return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register():
   """Show registration form and handle form submission"""
   if "user_name" in session:
      return redirect(f"/users/{session['user_name']}")

   form = RegisterForm()

   if form.validate_on_submit():
      name = form.username.data
      pwd = form.password.data
      email = form.email.data
      first_name = form.first_name.data
      last_name = form.last_name.data

      user = User.register(name, pwd, email, first_name, last_name)
      db.session.add(user)
      db.session.commit()

      session["user_name"] = user.username

      return redirect(f"/users/{user.username}")

   else:
      return render_template('users/register.html', form=form)

@app.route('/login', methods=["GET", "POST"])  
def login():

   if "user_name" in session:
      return redirect(f"/users/{session['user_name']}")
   
   form = LoginForm()

   if form.validate_on_submit():
      name = form.username.data
      pwd = form.password.data

      user = User.authenticate(name, pwd)

      if user:
         flash(f"Welcome Back, {user.first_name}!", "success")
         session["user_name"] = user.username
         return redirect(f"/users/{user.username}")

      else:
         form.username.errors = ["Bad name/password"]
         return render_template("users/login.html", form=form)

   return render_template("users/login.html", form=form)

@app.route("/users/<username>")
def profile(username):

   if "user_name" not in session or username != session['user_name']:
      flash("You must be logged in to view this page", "danger")
      return redirect('/register')
   else:
      user = User.query.get(username)
      form = DeleteForm()

      return render_template("users/show.html", user=user, form=form)
   

@app.route('/logout')
def logout():

   session.pop("user_name")

   return redirect('users/login')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):

   if "user_name" not in session:
      flash("You must be logged in to view this page", "danger")
      return redirect('users/login')
   else:
      user = User.query.get(username)
      db.session.delete(user)
      db.session.commit()
      session.pop("user_name")
      flash("User deleted", "danger")

      return redirect("/login")

@app.route('/users/<username>/feedback/new', methods=["GET", "POST"])
def new_feedback(username):

   if "user_name" not in session:
      flash("You must be logged in to view that page", "danger")
      redirect('users/login')

   form = FeedbackForm()

   if form.validate_on_submit():
      title = form.title.data
      content = form.content.data

      feedback = Feedback(title=title, content=content, username=username)
      db.session.add(feedback)
      db.session.commit()

      return redirect(f"/users/{feedback.username}")

   else:
      return render_template("feedback/new.html", form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=["GET","POST"])
def delete_feedback(feedback_id):

   feedback = Feedback.query.get(feedback_id)

   if "user_name" not in session:
      flash("You must be logged in to do this!", "danger")

   form = DeleteForm()

   if form.validate_on_submit():
      db.session.delete(feedback)
      db.session.commit()
      flash("Feedback deleted!", "success")

   return redirect(f"/users/{feedback.username}")

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def edit_feedback(feedback_id):

   feedback = Feedback.query.get(feedback_id)

   if "user_name" not in session:
      flash("You must be logged in to do this", "danger")

   form = FeedbackForm(obj=feedback)

   if form.validate_on_submit():
      feedback.title = form.title.data
      feedback.content = form.content.data
      
      db.session.commit()

      return redirect(f"/users/{feedback.username}")

   return render_template("/feedback/edit.html", form=form, feedback=feedback)


   
   
   

   