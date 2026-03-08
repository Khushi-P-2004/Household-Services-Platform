from flask import Flask, request, render_template,redirect,url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import cast, Date
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key='hehehe'

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///C:/Users/khush/OneDrive/Desktop/Project Root Folder/Code/instance/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"]=True
db=SQLAlchemy(app)

#database model

class User(db.Model):
    __tablename__ = 'user'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(25), unique=True, nullable=False)
    password=db.Column(db.String(150), nullable=False)
    role=db.Column(db.String(20), nullable=False)
    phone=db.Column(db.Integer, unique=True, nullable=False)
    city=db.Column(db.String)
    address=db.Column(db.String(150), nullable=False)
    specialization=db.Column(db.String, nullable=True)
    cv=db.Column(db.String(150), nullable=True)
    status=db.Column(db.String(150), nullable=False, default='pending')
    booking=db.relationship('Booking', back_populates='customer',lazy='dynamic')
    customer=db.relationship('Customer',uselist=False, back_populates='user')
    professional=db.relationship('Professional',uselist=False, back_populates='user')

class Customer(db.Model):
    __tablename__='customer'
    id=db.Column(db.Integer, primary_key=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    name=db.Column(db.String(25), unique=True, nullable=False)
    user=db.relationship('User',back_populates='customer')

class Professional(db.Model):
    __tablename__='professional'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    specialization=db.Column(db.String, nullable=False)
    professional_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status=db.Column(db.String(150), nullable=False, default='pending')
    user=db.relationship('User',back_populates='professional',cascade='all,delete')
    service=db.relationship('Service', back_populates='professional',lazy='dynamic')

    

class Service(db.Model):
    __tablename__="service"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    price=db.Column(db.Float, nullable=False)
    prof_id=db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    
    package=db.relationship('Package',back_populates='service')
    professional=db.relationship('Professional', back_populates='service')

class Package(db.Model):
    __tablename__="package"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    price=db.Column(db.Float, nullable=False)
    description=db.Column(db.Text, nullable=False)
    service_id=db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service=db.relationship('Service',back_populates='package')

    
class Booking(db.Model):
    __tablename__="booking"
    id=db.Column(db.Integer, primary_key=True)
    package_id=db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    customer_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location=db.Column(db.String(50))
    professional_id=db.Column(db.Integer, db.ForeignKey('professional.id', ondelete='CASCADE'))
    service_date=db.Column(db.DateTime, nullable=False)
    booking_status=db.Column(db.String(25), default='Pending', nullable=False)
    rating=db.Column(db.Integer,default=0)

    package=db.relationship('Package', backref='booking')
    customer=db.relationship('User', back_populates='booking')
    professional=db.relationship('Professional', backref='booking')


class Review(db.Model):
    __tablename__="review"
    id=db.Column(db.Integer, primary_key=True)
    booking_id=db.Column(db.Integer, db.ForeignKey('booking.id',ondelete='CASCADE'), nullable=True)
    professional_id=db.Column(db.Integer, db.ForeignKey('professional.id',ondelete='CASCADE'), nullable=False)
    customer_id=db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
    service_pkg=db.Column(db.Text, nullable=False)
    date=db.Column(db.DateTime, nullable=False)
    review=db.Column(db.Text, nullable=True)
    rating=db.Column(db.Integer,nullable=False)

    booking=db.relationship('Booking', backref='review')
    customer=db.relationship('User', backref='review')
    professional=db.relationship('Professional', backref='review')


@app.route("/")
def pristine():
    return render_template("start.html")

@app.route("/get_started",methods=["GET"])
def getstarted():
    return render_template("index.html")

@app.route('/admin')
def admin():
    service=Service.query.all()
    professionals=User.query.filter_by(role='professional').all()
    bookings=Booking.query.all()
    reviews=Review.query.all()
    return render_template('admin.html',service=service, professionals=professionals, bookings=bookings,reviews=reviews)

@app.route('/admin/stat')
def admin_stat():
    bookings=Booking.query.all()
    services=Service.query.all()
    ratings=Booking.rating
    service_name=[service.name for service in services]
    booking_counts=[sum(1 for booking in bookings if booking.package.service_id==service.id) for service in services]
    professionals=Professional.query.all()
    fig1,ax1=plt.subplots()
    ax1.bar(service_name,booking_counts,color='blue')
    ax1.set_title('Bookings per service')
    ax1.set_xlabel('services')
    ax1.set_ylabel('No. of bookings')
    img1=BytesIO()
    plt.savefig(img1,format='png')
    img1.seek(0)
    graph1_url=base64.b64encode(img1.getvalue()).decode()
    img1.close()

    ratings=[]
    for service in services:
        service_bookings=[booking for booking in bookings if booking.package.service_id==service.id]
        if service_bookings:
            avg_rating=sum(booking.rating for booking in service_bookings)/len(service_bookings)
        else:
            avg_rating=0
        ratings.append(avg_rating)
    fig2,ax2=plt.subplots()
    ax2.pie(ratings,labels=service_name,autopct='%1.1f%%',startangle=140)
    ax2.set_title('Avg Rating')
    img2=BytesIO()
    plt.savefig(img2,format='png')
    img2.seek(0)
    graph2_url=base64.b64encode(img2.getvalue()).decode()
    img2.close()
    return render_template('admin_stat.html',graph1_url=f'data:image/png;base64,{graph1_url}',graph2_url=f'data:image/png;base64,{graph2_url}')

@app.route("/admin_search",methods=["POST"])
def admin_search():
    error=None
    prof_id=request.form.get('prof_id')
    query=User.query.filter_by(role='professional')
    profs=query.filter(User.id==prof_id).all()
    if not profs:
            error="no results found"
        
    return render_template("admin_search.html", profs=profs,error=error)

@app.route('/services/add', methods=["GET","POST"])
def add_service():
    if request.method=="POST":
        name=request.form.get('name')
        price=request.form.get('price')
        
        prof_id=request.form.get('prof_id')
        
        if name and prof_id and price:
            service=Service(name=name, price=price,prof_id=prof_id)
            db.session.add(service)
            db.session.commit()
            
            return redirect(url_for('admin'))
        return render_template('addservice.html')
    return render_template('addservice.html')

@app.route('/services/<int:id>/packages/add', methods=["GET","POST"])
def add_package(id):
    service=Service.query.get(id)
    if request.method=="POST":
        package=request.form.get('package')
        desc=request.form.get('desc')
        price=request.form.get('price')
        package=Package(name=package,description=desc,price=price,service_id=service.id)
        db.session.add(package)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('addpackage.html')
            
@app.route('/services/<int:id>/packages', methods=["GET"])
def view_package(id):
    service=Service.query.get(id)
    if service:
        package=Package.query.filter_by(service_id=id).all()
        return render_template('view_pkg.html',service=service,package=package)
    return redirect(url_for('admin'))


@app.route('/services/edit/<int:id>', methods=["GET","POST"])
def edit_service(id):
    service=Service.query.get(id)
    if not service:
        return redirect(url_for('admin'))
    if request.method=="POST":
        name=request.form.get('name')
        price=request.form.get('price')
        prof_id=request.form.get('prof_id')
        if name:
            service.name=name
            service.price=price
            service.prof_id=prof_id
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template('editservice.html',service=service)
    return render_template('editservice.html',service=service)


@app.route('/services/delete/<int:id>')
def del_service(id):
    service=Service.query.get(id)
    if not service:
        return redirect(url_for('admin'))
    return render_template('delete.html', service=service)

@app.route('/services/delete/<int:id>', methods=["POST"])
def del_service_post(id):
    service=Service.query.get(id)
    if not service:
        return redirect(url_for('admin'))
    packages=Package.query.filter_by(service_id=id).all()
    for package in packages:
        bookings=Booking.query.filter_by(package_id=package.id).all()
        for booking in bookings:
            db.session.delete(booking)
        db.session.delete(package)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/approve_prof/<int:prof_id>', methods=["POST"])
def approve_prof(prof_id):
    user=User.query.get(prof_id)
    if user and user.role=='professional':
        user.status="approved"
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/reject_prof/<int:prof_id>', methods=["POST"])
def reject_prof(prof_id):
    user=User.query.get(prof_id)
    if user and user.role=='professional':
        user.status="rejected"
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/del_prof/<int:prof_id>')
def del_prof(prof_id):
    user=User.query.get(prof_id)
    if not user:
        return redirect(url_for('admin'))
    return render_template('deleteprof.html', user=user)
    
@app.route('/del_prof/<int:prof_id>', methods=["POST"])
def del_prof_post(prof_id):
    user=User.query.get(prof_id)
    if not user:
        return redirect(url_for('admin'))
    reviews=Review.query.filter_by(professional_id=prof_id).all()
    for review in reviews:
        db.session.delete(review)
    bookings=Booking.query.filter_by(professional_id=prof_id).all()
    for booking in bookings:
        db.session.delete(booking)
    professionals=Professional.query.filter_by(professional_id=prof_id).all()
    for professional in professionals:
        db.session.delete(professional)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin'))



@app.route("/c_dashboard")
def c_dashboard():
    username=request.args.get('username')
    customer_id=session.get('user_id')
    service=Service.query.all()
    bookings=Booking.query.filter_by(customer_id=customer_id).all()
    return render_template("c_dashboard.html", username=username, service=service, bookings=bookings)

@app.route('/cust_stat')
def cust_stat():
    customer_id=session.get('user_id')
    bookings=Booking.query.filter_by(customer_id=customer_id).all()
    booking_status_c={'rejected':0,'pending':0,'closed':0}
    for booking in bookings:
        if booking.booking_status=='rejected':
            booking_status_c['rejected']+=1
        elif booking.booking_status=='pending':
            booking_status_c['pending']+=1
        elif booking.booking_status=='closed':
            booking_status_c['closed']+=1
    status=list(booking_status_c.keys())
    count=list(booking_status_c.values())
    fig1,ax1=plt.subplots()
    ax1.bar(status,count,color=['blue','red','yellow'])
    ax1.set_title('Bookings')
    ax1.set_xlabel('Booking Status')
    ax1.set_ylabel('No. of bookings')
    img1=BytesIO()
    plt.savefig(img1,format='png')
    img1.seek(0)
    graph1_url=base64.b64encode(img1.getvalue()).decode()
    img1.close()
    return render_template('cust_stat.html',graph1_url=f'data:image/png;base64,{graph1_url}')


@app.route("/edit_profile",methods=["GET","POST"])
def edit_profile():
    user_id=session.get("user_id")
    user=User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    if request.method=='POST':
        user.username=request.form['username']
        user.address=request.form['address']
        user.phone=request.form['phone']
        db.session.commit()
        return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html',user=user)



@app.route("/services/<int:id>")
def services_details(id):
    service=Service.query.get(id)
    if not service:
        return redirect(url_for('c_dashboard'))
    package=Package.query.filter_by(service_id=service.id).all()
    return render_template("services_details.html", service=service,package=package)

@app.route("/search_service",methods=["POST"])
def search_service():
    error=None
    service_name=request.form.get('service_name')
    services=Service.query.filter(Service.name.ilike(f'%{service_name}%')).all()
    if not services:
        error="no results found"
    return render_template("search_service.html", services=services,error=error)


@app.route("/services/<int:service_id>/package/<int:package_id>/book")
def book_package(service_id,package_id):
    package=Package.query.get(package_id)
    service=Service.query.get(service_id)
    professionals=User.query.filter_by(role='professional',specialization=service.name, status='approved').all()
    if not package or not service:
        return redirect(url_for('c_dashboard'))
    
    return render_template('booking_form.html',package=package,service=service,professionals=professionals)


@app.route("/book",methods=["POST"])
def booking():
    package_id=request.form.get("package_id")
    professional_id=request.form.get("professional_id")
    service_date_str=request.form.get("service_date")
    location=request.form.get("location")
    customer_id=session.get("user_id")
    if not customer_id:
        return redirect(url_for("login"))
    if not package_id or not professional_id or not service_date_str:
        return redirect(url_for('book_package'))
    try:
        service_date=datetime.datetime.strptime(service_date_str,"%Y-%m-%dT%H:%M")
    except ValueError:
        return "invalid date",400
    try:
        booking=Booking(package_id=package_id,customer_id=customer_id,professional_id=professional_id, booking_status='pending',service_date=service_date,location=location)
        db.session.add(booking)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    finally:
        db.session.close()
    return f"Please wait for confirmation"


@app.route('/accept_booking/<int:booking_id>', methods=["POST"])
def accept_booking(booking_id):
    booking=Booking.query.get(booking_id)
    if booking:
        booking.booking_status="accepted"
        db.session.commit()
    return redirect(request.referrer)

@app.route('/reject_booking/<int:booking_id>', methods=["POST"])
def reject_booking(booking_id):
    booking=Booking.query.get(booking_id)
    if booking:
        booking.booking_status="rejected"
        db.session.commit()
    return redirect(request.referrer)


@app.route('/close_booking/<int:booking_id>',methods=['GET','POST'])
def close_booking(booking_id):
    booking=Booking.query.get(booking_id)
    customer_id=session.get('user_id')
    if not booking or booking.booking_status!='accepted':
        return redirect(url_for('c_dashboard'))
    if request.method=='POST':
        professional_id=booking.professional_id
        service_pkg=request.form['service_pkg']
        date_str=request.form['date']
        date=datetime.datetime.strptime(date_str,"%Y-%m-%dT%H:%M")
        review_w=request.form['review']
        rating=int(request.form['rating'])
        review=Review(booking_id=booking_id,professional_id=professional_id,customer_id=customer_id,date=date,review=review_w,rating=rating,service_pkg=service_pkg)
        db.session.add(review)
        booking.booking_status='closed'
        booking.rating=rating
        db.session.commit()
        return redirect(url_for('c_dashboard'))
    return render_template('review.html',booking=booking)



@app.route("/p_dashboard")
def p_dashboard():
    username=session.get('username')
    professional_id=session.get("user_id")
    if not professional_id:
        return redirect(url_for("login"))
    bookings=Booking.query.filter_by(professional_id=professional_id).all()
    return render_template("p_dashboard.html", username=username,bookings=bookings)

@app.route("/edit_prof_profile",methods=["GET","POST"])
def edit_prof_profile():
    user_id=session.get("user_id")
    user=User.query.get(user_id)
    if user.role!='professional':
        return redirect(url_for('login'))
    if request.method=='POST':
        user.username=request.form['username']
        user.address=request.form['address']
        user.phone=request.form['phone']
        db.session.commit()
        return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html',user=user)

@app.route('/prof_stat')
def prof_stat():
    professional_id=session.get('user_id')
    bookings=Booking.query.filter_by(professional_id=professional_id).all()
    booking_status_c={'rejected':0,'pending':0,'closed':0}
    for booking in bookings:
        if booking.booking_status=='rejected':
            booking_status_c['rejected']+=1
        elif booking.booking_status=='pending':
            booking_status_c['pending']+=1
        elif booking.booking_status=='closed':
            booking_status_c['closed']+=1
    status=list(booking_status_c.keys())
    count=list(booking_status_c.values())
    fig1,ax1=plt.subplots()
    ax1.bar(status,count,color=['blue','red','yellow'])
    ax1.set_title('Bookings')
    ax1.set_xlabel('Booking Status')
    ax1.set_ylabel('No. of bookings')
    img1=BytesIO()
    plt.savefig(img1,format='png')
    img1.seek(0)
    graph1_url=base64.b64encode(img1.getvalue()).decode()
    img1.close()

    reviews=Review.query.filter_by(professional_id=professional_id).all()
    r_count={1:0, 2:0, 3:0, 4:0, 5:0}
    for review in reviews:
        if review.rating is not None:
            r_count[review.rating]+=1
    ratings=list(r_count.keys())
    counts=list(r_count.values())
    fig2,ax2=plt.subplots()
    ax2.pie(counts,labels=ratings,autopct='%1.1f%%',startangle=140)
    ax2.set_title('Ratings')
    img2=BytesIO()
    plt.savefig(img2,format='png')
    img2.seek(0)
    graph2_url=base64.b64encode(img2.getvalue()).decode()
    img2.close()
    return render_template('prof_stat.html',graph1_url=f'data:image/png;base64,{graph1_url}',graph2_url=f'data:image/png;base64,{graph2_url}')

@app.route('/prof_search',methods=["POST"])
def prof_search():
    location=request.form.get('location')
    professional_id=session.get('user_id')
    if not location:
        return 'no results found'
    bookings=Booking.query.filter_by(location=location,professional_id=professional_id).all()
    if not bookings:
        return 'No result'
    return render_template('prof_search.html',location=location,bookings=bookings)


#customerlogin
@app.route("/login", methods=["GET","POST"])
def login():
    #collect info from the form
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()
        if user and user.password==password:
            session['user_id']=user.id
            session['username']=user.username
            session['role']=user.role
            if user.role=='admin':
                return redirect(url_for("admin"))
            elif user.role=='customer':
                return redirect(url_for("c_dashboard", username=username))
            elif user.role=='professional':
                if user.status=='pending':
                    return render_template("pendingreg.html")
                elif user.status=='rejected':
                    return render_template("rejectedreg.html")
                else:
                    return redirect(url_for("p_dashboard", username=username))
        else:                
            return render_template("index.html",error="Please check your username and password")
    return render_template("index.html")

@app.route("/logout",methods=["GET","POST"])
def logout():
    session.pop('user.id',None)
    return redirect(url_for('login'))



#create new account
@app.route("/newaccount",methods=['GET','POST'])
def newaccount():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        phone=request.form['phone']
        address=request.form['address']
        user=User.query.filter_by(username=username).first()
        if user:
            return render_template('index.html', error= 'Account already exists! Please login')
        new_user = User(username=username, password=password,role='customer', phone=phone, address=address)
        db.session.add(new_user)
        db.session.commit()
        customer=Customer(customer_id=new_user.id, name=new_user.username)
        db.session.add(customer)
        db.session.commit()

        #session['username']=username
        return redirect(url_for('c_dashboard',username=username))
    return render_template("newacc.html")

#register as prof
@app.route("/register",methods=['GET','POST'])
def register():
    #check if they already in db
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        phone=request.form['phone']
        city=request.form['city']
        address=request.form['address']
        specialization=request.form['specialization']
        cv=request.form['cv']
        user=User.query.filter_by(username=username).first()
        if user:
            return render_template('index.html', error="Account already exists! Please login")
        new_prof = User(username=username, password=password, role='professional',phone=phone, city=city, address=address, specialization=specialization, cv=cv)
        db.session.add(new_prof)
        db.session.commit()
        prof=Professional(professional_id=new_prof.id,name=new_prof.username,specialization=new_prof.specialization,status=new_prof.status)
        db.session.add(prof)
        db.session.commit()
        return render_template('index.html', error="Login to check your registration status")
    return render_template("register.html")


if __name__=="__main__":
    app.run(debug=True) 