# Household-Services-Platform

## Project Statement 
It is a muti-user app (requires one admin and other service professionals/customers) which acts as a 
platform for providing comprehensive home servicing and solutions. 
## Project Overview 
The core functionality of the project revolves around facilitating the booking of services. Customers 
can search for services, select a professional, and make a booking. The professional can then 
approve or reject the booking based on their availability. The admin has the capability to manage 
professionals, services, and track the status of bookings. 
## Technologies Used 
• Backend: The project uses Python with the Flask framework for the backend.  

• Database: SQLAlchemy is used to interact with the SQLite database. The database stores 
information about users, services, packages, bookings, and professionals. 

• Frontend: The frontend is built using HTML, CSS, and Jinja2 templating to display dynamic 
content and forms. 

• Routing and Forms: Flask routes handle requests and pass necessary data to templates. 
Forms allow customers to submit booking information.

### Database Model

<img width="1061" height="560" alt="Screenshot 2026-03-08 112435" src="https://github.com/user-attachments/assets/c811f4a4-a7d4-4eb3-9370-2b373f42dac1" />

## Functionalities 

### User Authentication:

o Registration: Users can create accounts for the roles of customer, professional, or 
admin.

o Login: After registering, users can log in to their respective dashboards.

o Role-based Access Control: Different roles (customer, professional, admin) have 
specific access to different parts of the application. Admins manage users, services, 
and bookings, while professionals manage their accepted bookings. 

### Service Booking: 

o Customer Dashboard: Customers can view available services, search professionals 
and book a service. After a booking is made, it enters a "pending" state, awaiting 
professional approval. 

o Professional Dashboard: Professionals can view incoming booking requests, and 
they can approve or reject bookings. Only approved professionals are able to work 
with customers.

o Admin Dashboard: Admins can manage the system by approving , removing 
professionals or tracking booking statuses.

### Booking System: 

o Once a booking request is accepted and closed, customers get to submit a review of 
the service. 

### Admin Functionality: 

o Manage Services: The admin can view, add, or remove services & packages that are 
offered through the platform. 

o Approve/Reject Professional Registrations: Professionals cannot access the 
platform without admin approval. 

o Track Booking Statuses: Admins can monitor the status of all bookings (pending, 
accepted, or rejected). 

<img width="1843" height="835" alt="Screenshot 2026-03-08 113444" src="https://github.com/user-attachments/assets/1df34e45-6697-429a-96b4-2ee0e8879507" />

<img width="1893" height="896" alt="Screenshot 2026-03-08 113607" src="https://github.com/user-attachments/assets/18227daa-bf59-4ea6-a2b9-5b7e2c3d9036" />

<img width="988" height="508" alt="Screenshot 2026-03-08 113646" src="https://github.com/user-attachments/assets/62a5a38f-6a36-44bd-a482-a256261f600f" />




