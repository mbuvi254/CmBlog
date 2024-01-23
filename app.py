from flask import Flask, request, render_template, redirect, session, flash ,url_for
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask_mail import Mail, Message

app=Flask(__name__)
app.config['SECRET_KEY'] = "cybermaishasolutions2023@"
app.config['UPLOAD_FOLDER'] = 'static/blogImages'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg',''}

# MySQL Connector configuration
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1994410Mbuvi@',
    database='cm_blog'
)

cursor = db.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


##############################Admin##################################################################
@app.route('/admin/')
def admin_dashboard():
    if 'admin_email' in session:
        return render_template('/admin/dashboard.html')
    else:
        return render_template('/admin/login.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName =request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        picture = request.files['picture']

        # Check if the user is already registered
        query = "SELECT * FROM admin WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user:
           flash('Username already exists. Please choose a different username.', 'error')
           return redirect(url_for('login'))

        if picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save the user and picture information in the database
            query = "INSERT INTO admin (firstName,lastName,email,password,picture) VALUES (%s, %s, %s,%s,%s)"
            values = (firstName,lastName,email,password,filename)
            cursor.execute(query, values)
            db.commit()

            return redirect(url_for('login'))

    return render_template('/admin/register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the user credentials are valid
        query = "SELECT * FROM admin WHERE email = %s AND password = %s"
        values = (email, password)
        cursor.execute(query, values)
        admin = cursor.fetchone()
        
        if admin:
            # Create a session for the user
            session['admin_id'] = admin[0]
            session['admin_firstname'] = admin[1]
            session['admin_lastname'] = admin[2]
            session['admin_email'] = admin[3]
            session['admin_image'] = admin[5]
        
            
            return render_template('/admin/dashboard.html')
        else:
            return 'Invalid username or password'
    
    return render_template('/admin/login.html')

@app.route('/admin/logout',methods=['POST','GET'])
def admin_logout():
    # Clear the session and redirect to the login page
    session.clear()
    return render_template('/admin/login.html')

# Route for adding a new category
@app.route('/admin/add_category')
def add_category():
    return render_template('/admin/add_category.html')


# Route for handling the form submission for adding a new category
@app.route('/admin/category/add', methods=['POST'])
def add_category_post():
    categoryName = request.form['categoryName']
    categoryDesc = request.form['categoryDesc']
    sql = "INSERT INTO category (categoryName, categoryDesc) VALUES (%s, %s)"
    val = (categoryName, categoryDesc)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()
    return redirect('/admin/categories')


# Route for displaying categories
@app.route('/admin/categories')
def categories():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM category")
    cat = cursor.fetchall()
    return render_template('/admin/categories.html', cat=cat)


# Route for editing a category
@app.route('/admin/category/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute("SELECT * FROM category WHERE cid = %s", (category_id,))
        category = cursor.fetchone()
        return render_template('/admin/edit_category.html', category=category)
    elif request.method == 'POST':
        categoryName = request.form['categoryName']
        categoryDesc = request.form['categoryDesc']
        sql = "UPDATE category SET categoryName = %s, categoryDesc = %s WHERE cid = %s"
        val = (categoryName, categoryDesc, category_id)
        cursor = db.cursor()
        cursor.execute(sql, val)
        db.commit()
        return redirect('/admin/categories')


# Route for deleting a category
@app.route('/admin/category/delete/<int:category_id>', methods=['GET'])
def delete_category(category_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM category WHERE cid = %s", (category_id,))
    db.commit()
    return redirect('/admin/categories')

# Route for about list
@app.route('/admin/about_list')
def about_list():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM about")
    about=cursor.fetchall()
    return render_template('/admin/about_list.html',about=about)

# Route for add about 
@app.route('/admin/add_about')
def add_about():
    cursor = db.cursor()
    return render_template('/admin/add_about.html')

# Route for handling the form submission for adding a new about
@app.route('/admin/about/add', methods=['POST'])
def about_add():
    title = request.form['title']
    description = request.form['description']
  
  # Check if a file is uploaded
    if 'aboutImage' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['aboutImage']

    # Check if the file has a valid extension

    # Secure the filename and save it to the upload folder
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Insert the blog post into the database
    sql = "INSERT INTO about (title,description,aboutImage) VALUES (%s, %s, %s)"
    val = (title,description,filename)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()

    return redirect('/admin/about_list')

# Route for reading about
@app.route('/admin/about/<int:about_id>')
def read_about(about_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM about WHERE id= %s",(about_id,))
    about = cursor.fetchall()

    return render_template('/admin/read_about.html', about=about)

# Route for deleting a about
@app.route('/admin/about/delete/<int:about_id>', methods=['GET'])
def delete_about(about_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM about WHERE id = %s", (about_id,))
    db.commit()
    return redirect('/admin/about_list')


# Route for editing about
@app.route('/admin/about/edit/<int:about_id>', methods=['GET', 'POST'])
def edit_about(about_id):
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM about WHERE id = %s",
            (about_id,))
        about = cursor.fetchall()
        return render_template('/admin/edit_about.html', about=about)

    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        aboutImage = request.files['aboutImage']
        filename = None
       
        if aboutImage:
            
            # Secure the filename and save it to the upload folder
            filename = secure_filename(aboutImage.filename)
            blogImage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
                flash('Invalid file extension')
                return redirect(request.url)

        # Update the blog post
        sql = "UPDATE about SET title = %s, description = %s"
        if filename:
            sql += ",aboutImage = %s"
            val = (title,description,filename)
        else:
            val = (title, description)
            
        sql += " WHERE id = %s"
        val += (about_id,)

        cursor = db.cursor()
        cursor.execute(sql, val)
        db.commit()
        return redirect('/admin/about_list')

# Route for adding a new blog post
@app.route('/admin/add_blog')
def admin_add_blog():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()
    return render_template('/admin/add_blog.html', categories=categories)


# Route for handling the form submission for adding a new blog post
@app.route('/admin/blog/add', methods=['POST'])
def admin_add_blog_post():
    authorID = request.form['authorID']
    blogTitle = request.form['blogTitle']
    blogContent = request.form['blogContent']
    categoryID = request.form['categoryID']

    # Check if a file is uploaded
    if 'blogImage' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['blogImage']

    # Check if the file has a valid extension

    # Secure the filename and save it to the upload folder
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Insert the blog post into the database
    sql = "INSERT INTO blog (blogTitle, blogContent, categoryID, blogImage,authorID) VALUES (%s, %s, %s, %s,%s)"
    val = (blogTitle, blogContent, categoryID, filename, authorID)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()

    return redirect('/admin/blogs')


# Route for editing a blog post
@app.route('/admin/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
def admin_edit_blog(blog_id):
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute(
            "SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,a.id,a.firstName,a.lastName,a.email FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN admin AS a ON b.authorID=a.id WHERE b.bid = %s",
            (blog_id,))
        blog = cursor.fetchone()
        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()
        cursor.execute("SELECT * FROM admin")
        admin = cursor.fetchall()
        return render_template('/admin/edit_blog.html', blog=blog, categories=categories, admin=admin)

    elif request.method == 'POST':
        authorID = request.form['authorID']
        blogTitle = request.form['blogTitle']
        blogContent = request.form['blogContent']
        categoryID = request.form['categoryID']
        blogImage = request.files['blogImage']
        filename = None
       

        if blogImage:
            
            # Secure the filename and save it to the upload folder
            filename = secure_filename(blogImage.filename)
            blogImage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
                flash('Invalid file extension')
                return redirect(request.url)

        # Update the blog post
        sql = "UPDATE blog SET blogTitle = %s, blogContent = %s, categoryID = %s"
        if filename:
            sql += ",blogImage = %s"
            val = (blogTitle, blogContent, categoryID, filename)
        else:
            val = (blogTitle, blogContent,categoryID,filename)
            
        sql += " WHERE bid = %s"
        val += (blog_id,)

        cursor = db.cursor()
        cursor.execute(sql, val)
        db.commit()
        return redirect('/admin/blogs')



# Route for deleting a blog post
@app.route('/admin/blog/delete/<int:blog_id>', methods=['GET'])
def admin_delete_blog(blog_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM blog WHERE bid = %s", (blog_id,))
    db.commit()
    return redirect('/admin/blogs')


# Route for displaying all blog posts
@app.route('/admin/blogs')
def admin_blogs():
    cursor = db.cursor()
    cursor.execute("SELECT b.bid,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.status,c.cid,c.categoryName FROM blog AS b JOIN category AS c ON b.categoryID = c.cid")
    blogs = cursor.fetchall()
    return render_template('/admin/blogs.html', blogs=blogs)


# Route for reading a blog post and its comments
@app.route('/admin/blog/<int:blog_id>')
def admin_read_blog(blog_id):
    cursor = db.cursor()
    cursor.execute(
        "SELECT b.bid, b.blogTitle, b.blogContent,b.blogImage,c.categoryName FROM blog AS b JOIN category AS c ON b.categoryID = c.cid WHERE b.bid= %s",
        (blog_id,))
    blog = cursor.fetchone()
    # Fetch comments for the blog post
    cursor.execute("SELECT id, commentName, commentContent FROM comments WHERE blogID = %s", (blog_id,))
    comments = cursor.fetchall()

    return render_template('/admin/read_blog.html', blog=blog, comments=comments)


# Route for adding a comment to a blog post
@app.route('/admin/comment/add/<int:blog_id>', methods=['POST'])
def add_admin_comment(blog_id):
    commentName = request.form['commentName']
    commentContent = request.form['commentContent']

    cursor = db.cursor()
    sql = "INSERT INTO comments (commentName, commentContent, blogID) VALUES (%s, %s, %s)"
    val = (commentName, commentContent, blog_id)
    cursor.execute(sql, val)
    db.commit()

    return redirect('/admin/blog/{}'.format(blog_id))

@app.route('/admin/blog/publish/<int:blog_id>')
def publish_blog(blog_id):
    # Update the blog post
        sql = "UPDATE blog SET status = %s WHERE bid = %s"
        val = (1,blog_id)
    

        cursor = db.cursor()
        cursor.execute(sql, val)
        db.commit()

        cursor.execute("SELECT b.bid,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.status,c.cid,c.categoryName FROM blog AS b JOIN category AS c ON b.categoryID = c.cid")
        blog = cursor.fetchall()
        return redirect('/admin/blogs')
   

  

########################AUTHORS############################
@app.route('/staff')
def staff_dashboard():
    if 'staff_email' in session:
        return render_template('/staff/dashboard.html')
    else:
        return render_template('/staff/login.html')

@app.route('/staff/logout',methods=['POST','GET'])
def logout():
    # Clear the session and redirect to the login page
    session.clear()
    return render_template('/staff/login.html')

@app.route('/staff/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName =request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        picture = request.files['picture']

        # Check if the user is already registered
        query = "SELECT * FROM staff WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user:
           flash('Username already exists. Please choose a different username.', 'error')
           return redirect(url_for('login'))

        if picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save the user and picture information in the database
            query = "INSERT INTO staff (firstName,lastName,email,password,picture) VALUES (%s, %s, %s,%s,%s)"
            values = (firstName,lastName,email,password,filename)
            cursor.execute(query, values)
            db.commit()

            return redirect(url_for('login'))

    return render_template('/staff/register.html')

@app.route('/staff/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the user credentials are valid
        query = "SELECT * FROM staff WHERE email = %s AND password = %s"
        values = (email, password)
        cursor.execute(query, values)
        staff = cursor.fetchone()
        
        if staff:
            # Create a session for the user
            session['staff_id'] = staff[0]
            session['staff_firstname'] = staff[1]
            session['staff_lastname'] = staff[2]
            session['staff_email'] = staff[3]
            session['staff_image'] = staff[5]
        
            
            return render_template('/staff/dashboard.html')
        else:
            return 'Invalid username or password'
    
    return render_template('/staff/login.html')

@app.route('/staff/profile/', methods=['GET', 'POST'])
def profile():
    # Check if the user is logged in
    if 'staff_email' in session:
        if request.method == 'POST':
            firstName=request.form['firstName']
            lastName=request.form['lastName']
            email = request.form['email']
            password = request.form['password']
            picture = request.files['picture']
            
            # Retrieve the user information from the database or wherever it's stored
            query = "SELECT * FROM staff WHERE email = %s"
            values = (session['staff_email'],)
            cursor.execute(query, values)
            staff = cursor.fetchone()
            
            if picture and allowed_file(picture.filename):
                # Remove the old picture from the filesystem
                old_picture_filename = staff[5]
                if old_picture_filename:
                    old_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], old_picture_filename)
                    os.remove(old_picture_path)
                
                # Save the new picture
                filename = secure_filename(picture.filename)
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Update the user's information in the database
                query = "UPDATE staff SET firstName = %s,lastName= %s,email = %s, password = %s, picture = %s WHERE email = %s"
                values = (firstName,lastName,email,password,filename, session['staff_email'])
                cursor.execute(query, values)
                db.commit()
            else:
                # Update the user's information in the database without changing the picture
                query = "UPDATE staff SET firstName= %s, lastName=%s, email = %s, password = %s WHERE email = %s"
                values = (firstName,lastName,email,password, session['staff_email'])
                cursor.execute(query, values)
                db.commit()
            
            # Update the session with the new details if it changed
            session['staff_id'] = staff[0]
            session['staff_firstName'] = staff[1]
            session['staff_lastName'] = staff[2]
            session['staff_email'] = staff[3]
            session['staff_image'] = staff[5]
            session['staff_password'] = staff[4]
            
            return redirect(url_for('profile'))
        
        # Retrieve the user information from the database or wherever it's stored
        query = "SELECT * FROM staff WHERE email = %s"
        values = (session['staff_email'],)
        cursor.execute(query, values)
        staff = cursor.fetchone()
        
        return render_template('/staff/profile.html', staff=staff)
    
    return redirect(url_for('login'))

# Route for displaying all blog posts
@app.route('/staff/blogs')
def blogs():
    title='blogs'
    cursor = db.cursor()
    cursor.execute("SELECT b.bid,b.blogTitle,b.blogContent,b.blogImage,b.status,c.cid,c.categoryName FROM blog AS b JOIN category AS c ON b.categoryID = c.cid")
    #cursor.execute("SELECT * FROM blog")
    blogs = cursor.fetchall()
    return render_template('/staff/blogs.html', blogs=blogs,title=title)

# Route for deleting a blog post
@app.route('/staff/blog/delete/<int:blog_id>', methods=['GET'])
def delete_blog(blog_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM blog WHERE bid = %s", (blog_id,))
    db.commit()
    return redirect('/staff/blogs')



# Route for adding a new blog post
@app.route('/staff/add_blog')
def add_blog():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()
    return render_template('/staff/add_blog.html', categories=categories)


# Route for handling the form submission for adding a new blog post
@app.route('/staff/blog/add', methods=['POST'])
def add_post():
    authorID = request.form['authorID']
    blogTitle = request.form['blogTitle']
    blogContent = request.form['blogContent']
    categoryID = request.form['categoryID']

    # Check if a file is uploaded
    if 'blogImage' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['blogImage']

    # Check if the file has a valid extension

    # Secure the filename and save it to the upload folder
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Insert the blog post into the database
    sql = "INSERT INTO blog (blogTitle, blogContent, categoryID, blogImage,authorID) VALUES (%s, %s, %s, %s,%s)"
    val = (blogTitle, blogContent, categoryID, filename, authorID)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()

    return redirect('/staff/blogs')

# Route for editing a blog post
@app.route('/staff/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute(
            "SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,a.id,a.firstName,a.lastName,a.email FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN staff AS a ON b.authorID=a.id WHERE b.bid = %s",
            (blog_id,))
        blog = cursor.fetchone()
        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()
        cursor.execute("SELECT * FROM staff")
        staff = cursor.fetchall()
        return render_template('/staff/edit_blog.html', blog=blog, categories=categories, staff=staff)

    elif request.method == 'POST':
        authorID = request.form['authorID']
        blogTitle = request.form['blogTitle']
        blogContent = request.form['blogContent']
        categoryID = request.form['categoryID']
        blogImage = request.files['blogImage']
        filename = None
       

        if blogImage:
            
            # Secure the filename and save it to the upload folder
            filename = secure_filename(blogImage.filename)
            blogImage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
                flash('Invalid file extension')
                return redirect(request.url)

        # Update the blog post
        sql = "UPDATE blog SET blogTitle = %s, blogContent = %s, categoryID = %s"
        if filename:
            sql += ",blogImage = %s"
            val = (blogTitle, blogContent, categoryID, filename)
        else:
            val = (blogTitle, blogContent,categoryID,filename)
            
        sql += " WHERE bid = %s"
        val += (blog_id,)

        cursor = db.cursor()
        cursor.execute(sql, val)
        db.commit()
        return redirect('/staff/blogs')

################################################################################################### 
#############################################User Side ############################################

@app.route('/')
def index():
    title='Home'
    cursor = db.cursor()
    cursor.execute("SELECT * FROM category")
    category = cursor.fetchall()
    cursor.execute("SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,s.id,s.firstName,s.lastName,s.email,s.picture FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN staff AS s ON b.authorID=s.id ORDER BY  blogDate LIMIT 3")
    b = cursor.fetchall()
    cursor.execute("SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,s.id,s.firstName,s.lastName,s.email,s.picture FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN staff AS s ON b.authorID=s.id ORDER BY  blogDate LIMIT 6")
    blog = cursor.fetchall()
    cursor.execute("SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,s.id,s.firstName,s.lastName,s.email,s.picture FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN staff AS s ON b.authorID=s.id ORDER BY  blogDate DESC LIMIT 1;")
    b1 = cursor.fetchall()
    return render_template('index.html', category=category, blog=blog,b1=b1,b=b,title=title)


# Route for reading a blog post and its comments
@app.route('/read/<int:blog_id>')
def read(blog_id):
    title='Read'
    cursor = db.cursor()
    cursor.execute(
        "SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,s.id,s.firstName,s.lastName,s.email,s.picture FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN staff AS s ON b.authorID=s.id WHERE b.bid= %s",
        (blog_id,))
    blog = cursor.fetchone()
    # Fetch comments for the blog post
    cursor.execute("SELECT id, commentName, commentContent FROM comments WHERE blogID = %s", (blog_id,))
    comments = cursor.fetchall()
    query = "SELECT COUNT(*) FROM comments"
    cursor.execute(query)
    comment_count = cursor.fetchone()[0] 
    cursor.execute("SELECT * FROM category")
    cat=cursor.fetchall()

    return render_template('/read.html', blog=blog,comments=comments,comment_count=comment_count,cat=cat,title=title)

# Route for adding a comment to a blog post
@app.route('/comment/add/<int:blog_id>', methods=['POST'])
def comment(blog_id):
    commentName = request.form['commentName']
    commentContent = request.form['commentContent']

    cursor = db.cursor()
    sql = "INSERT INTO comments (commentName, commentContent, blogID) VALUES (%s, %s, %s)"
    val = (commentName, commentContent, blog_id)
    cursor.execute(sql, val)
    db.commit()

    return redirect('/read/{}'.format(blog_id))

@app.route('/category/<int:category_id>')
def category(category_id):
    title='Category'
    cursor=db.cursor()
    cursor.execute("SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,a.id,a.firstName,a.lastName,a.email,a.image FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN admin AS a ON b.authorID=a.id WHERE b.categoryID= %s",(category_id,))
    blog=cursor.fetchall()
    cursor.execute("SELECT * FROM category WHERE cid= %s",(category_id,))
    cat=cursor.fetchall() 
    cursor.execute("SELECT * FROM category")
    category=cursor.fetchall() 
    return render_template('/category.html',blog=blog,category=category,cat=cat,title=title)


    
@app.route('/search', methods=['GET', 'POST'])
def search():
    title='Search'
    if request.method == 'POST':
        # Handle the search query and perform the search logic
        query = request.form['query']
        cursor=db.cursor()
        # Execute the search query
        sql="SELECT b.bid,b.categoryID,b.authorID,b.blogTitle,b.blogContent,b.blogImage,b.blogDate,c.cid,c.categoryName,a.id,a.firstName,a.lastName,a.email,a.image FROM blog AS b JOIN category AS c ON b.categoryID = c.cid JOIN admin AS a WHERE b.blogTitle LIKE %s OR b.blogContent LIKE %s"
        #sql = "SELECT * FROM blog WHERE  blogTitle LIKE %s OR blogContent LIKE %s"
        params = (f"%{query}%", f"%{query}%")
        cursor.execute(sql, params)
        
        # Fetch the search results
        blogs = cursor.fetchall()
        cursor.execute("SELECT * FROM category")
        category = cursor.fetchall()
        
        # Return the search results to the template
        return render_template('search-results.html', query=query, blogs=blogs,category=category,title=title)
    
    return render_template('search.html')

# Route for displaying about
@app.route('/about')
def about():
    title='About'
    cursor = db.cursor()
    cursor.execute("SELECT * FROM about ORDER BY aboutDate LIMIT 1")
    about = cursor.fetchall()
    cursor.execute("SELECT * FROM staff")
    staff = cursor.fetchall()
    return render_template('about.html', about=about,staff=staff,title=title)

#Route for Contact Page
@app.route('/contact')
def contact():
    title='Contact'
    return render_template('contact.html',title=title)

@app.route('/contact/message',methods=['POST'])
def send_message():
    title='Contact'
    name=request.form['name']
    email=request.form['email']
    sub=request.form['sub']
    message=request.form['message']


   #msg = Message('Contact Form Submission',
                 # sender='admin@cybermaisha.co.ke',
                 # recipients=['info@cybermaisha.co.ke'])
    #msg.body = f"Name: {name}\nEmail: {email}\n\n{message}"

    #mail.send(msg)

 

    cursor=db.cursor()
    sql="INSERT INTO messages(name,email,sub,message)VALUES(%s,%s,%s,%s)"
    val= (name,email,sub,message)

    cursor.execute(sql,val)
    db.commit()

    
    return render_template('contact.html',title=title)







if __name__ == '__main__':
	app.run(debug=True)
	