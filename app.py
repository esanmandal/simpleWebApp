import web
import pymongo
import json
from web import form
from user_model import UserModel

# How many records to show per page.
# TODO: ideally this should be a user input on each page.  
PER_PAGE_COUNT = 10


render = web.template.render('templates/')
urls = (
    r'/status', 'Status',
    r'/', 'Index',
    r'/index', 'Index',
    r'/login', 'Login',
    r'/list', 'List',
    r'/delete_all', 'Delete_All',
    r'/register', 'Register',
    r'/user_info', 'User_info',
    r'/list_dir', 'List_dir',
    r'/group_by', 'Group_by',

)

app = web.application(urls, globals())

connection = pymongo.MongoClient('localhost', 27017)
db = connection.test
model = UserModel(db)


#Default page
class Index():
    def GET(self):
        return render.index()


#Get status of the mongo server
class Status:
    def GET(self):
        try:
            res = db.last_status()
            res['location'] = 'localhost'
            res['port'] = 27017
            return render.status(mongo=res)
        except:  
            res = {}
            res['location'] = 'localhost'
            res['port'] = 27017
            res['status'] = 'Mongo DB is down'            
            return render.status(mongo=res)


#list all the entries in the database
#TODO: This should be only available to admin  
class List:

    def GET(self ):
        params = web.input()
        page = params.page if hasattr(params, 'page') else 1
        page = int(page)
        perpage = PER_PAGE_COUNT
        
        offset = (page - 1) * perpage
        users = model.get_all()
        
        userscount = len(users)
        if userscount:
            pages = userscount / perpage
            if userscount % perpage > 0:
                pages += 1
            if page > pages:
                raise web.seeother('/list')
            else:
                return render.list(users=users[offset:offset+perpage], pages=pages)
        else:
            return web.seeother('/index')
            
#remove all the entries in the database
#TODO: This should be only available to admin  
class Delete_All:
    def GET(self):
        model.delete_all()
        return web.seeother('/index')


#Login form
#This is just checking for valid username password combinations in the database
#TODO: Login should be implemented with sessions to really make sense 
login_form = form.Form(
    form.Textbox("username", description="Username"),
    form.Password("password", description="Password"),
    form.Button("submit", type="submit", description="Login"),
)

class Login:
    def GET(self):

        f = login_form()
        return render.login(f, failedmsg='')
    
    def POST(self):
        f = login_form()
        if not f.validates():
            return render.register(f)
        else:
            payload = web.data()
            # If there is a payload then try to json decode it 
            #Test it like so:
            #curl -vX POST http://localhost:8080/login -d  '{"username":"apriltitus","password":"April"}' --header "Content-Type: application/json"  
            if payload:
                try:
                    data = json.loads(str(payload))
                    res = model.validate_login(data)
                # if it fails then use the form input
                except ValueError:
                    res = model.validate_login(f.d)
            if res:
                return render.user_info(user=res)
            else:
                return render.login(f, failedmsg='Username and Password do not match')


#Registration form
# Add new data to the database

vpass = form.regexp(r".{3,20}$", 'must be between 3 and 20 characters')
vemail = form.regexp(r".*@.*", "must be a valid email address")
vzip = form.regexp(r".[0-9]", "must be a valid ZIP")

register_form = form.Form(
    form.Textbox("username", description="Username"),
    form.Textbox("firstname", description="First Name"),
    form.Textbox("lastname", description="Last Name"),
    form.Dropdown('sex', ['Male', 'Female'], description = "Sex "),              
    form.Textbox("email", vemail, description="E-Mail"),
    form.Password("password", vpass, description="Password"),
    form.Password("password2", description="Repeat password"),
    
    form.Textbox("city", description="City"),
    form.Textbox("state", description="State"),
    form.Textbox("zip",vzip, description="Zip"),
    form.Button("submit", type="submit", description="Register"),
    validators = [
        form.Validator("Passwords did't match", lambda i: i.password == i.password2)]

)
class Register:
    def GET(self):
        # do $:f.render() in the template
        f = register_form()
        return render.register(f)

    def POST(self):
        f = register_form()
        if not f.validates():
            return render.register(f)
        else:
            model.create(f.d)
            return web.seeother('/index')



#list directories
file_form = form.Form(
    form.Textbox("pick_directory", description = "Input directory to list contents"),
    form.Button("list", type="submit", description="List Contents")
    )

class List_dir:
 
    def GET(self):

        perpage = PER_PAGE_COUNT
       
        params = web.input()
        page = params.page if hasattr(params, 'page') else 1
        page = int(page)
        dir = params.directory if hasattr(params, 'directory') else None
        
        if dir:
            res = model.list_dir_contents(dir)
        else : 
            res = None
        
        if res:
            offset = (page - 1) * perpage
            count = len(res)
            pages = count / perpage
            if count % perpage > 0:
                pages += 1
                
            if page > pages:
                render.list_dir(lform=f, dir = '')
            else:
                #Get content for display 
                return render.list_dir(lform = file_form(), 
                                       dir=res[offset:offset+perpage], 
                                       pages = pages, 
                                       directory=dir)
        else:
            return render.list_dir(lform=file_form(), 
                                   dir = '', 
                                   pages = 1, 
                                   directory='')            
        

    #TODO: On submit the url parameters do not get updated to reflect the new query. This should be fixed    
    def POST(self):
        
        perpage = PER_PAGE_COUNT

        f = file_form()
        if not f.validates():
            return render.index(f)
        else:
            dir = f.d['pick_directory']
            if dir:
                res = model.list_dir_contents(dir)
            else : 
                res = None
                
            #If there are valid inputs from the url then process the data
            if res:
                page = 1

                offset = (page - 1) * perpage
                count = len(res)
                pages = count / perpage
                if count % perpage > 0:
                    pages += 1
                    
                if page > pages:
                    render.list_dir(lform=f, dir = '')
                else:

                    #Get content for display 
                    return render.list_dir(lform = f, 
                                           dir=res[offset:offset+perpage], 
                                           pages = pages, 
                                           directory=dir)
            else:
                return render.list_dir(lform=f, 
                                       dir = '',  
                                       pages = 1, 
                                       directory='')            


# Filter and group records in the database based on user input

groupby_form = form.Form(
        form.Dropdown('filter_by', ['firstname', 'lastname','sex','city', 'state', 'zip'], description = "Filter by "),              
        form.Textbox("filter_by_value", description = "Filter value "),
        form.Dropdown('group_by', ['firstname', 'lastname','sex','city', 'state', 'zip'], description = "Group by "),              
        form.Button("submit", type="submit", description="Submit query")
        )


class Group_by:
        
    def GET(self):

        perpage = PER_PAGE_COUNT

        
        #Get input from the url
        params = web.input()
        page = params.page if hasattr(params, 'page') else 1
        page = int(page)
        filter_by = params.filter_parm if hasattr(params, 'filter_parm') else None
        filter_by_value = params.filter_value_parm if hasattr(params, 'filter_value_parm') else None
        group_by = params.group_parm if hasattr(params, 'group_parm') else None
        
        #If there are valid inputs from the url then process the data
        if filter_by_value and filter_by and group_by:
            #query the model for results
            d = {"filter_by":filter_by, "filter_by_value":filter_by_value, "group_by":group_by}
            queryData, recordcount = model.group_by(d , perpage)

            if queryData:
                #calculate page for pagination
                offset = (page - 1) * perpage                
                
                pages = recordcount / perpage
                                                   
                if recordcount % perpage > 0:
                    pages += 1
                    
                if page > pages:
                    raise web.seeother('/group_by')
                else :
                    
                    #sort the results
                    sortedkeys = queryData[page].keys()
                    sortedkeys.sort()
                    
                    # render the page
                    return render.group_by(lform = groupby_form(), 
                                           grouping=queryData[page], 
                                           sortedkeys = sortedkeys,
                                           pages=pages,
                                           filter_by=filter_by,
                                           filter_by_value=filter_by_value, 
                                           group_by=group_by)
            else:
                #render default page
                
                return render.group_by(lform=groupby_form(),  
                                       grouping= '', 
                                       sortedkeys = '',
                                       pages=0,
                                       filter_by='',
                                       filter_by_value='', 
                                       group_by='')     
        
        else:
            #render default page
            return render.group_by(lform=groupby_form(),  
                                   grouping= '', 
                                   sortedkeys = '',
                                   pages=0,
                                   filter_by='',
                                   filter_by_value='', 
                                   group_by='')     
        

    #TODO: On submit the url parameters do not get updated to reflect the new query. This should be fixed
    def POST(self):
        perpage = PER_PAGE_COUNT
        
        f = groupby_form()

        if not f.validates():
            return render.group_by(lform=f,  
                                       grouping= '', 
                                       sortedkeys = '',
                                       pages=0,
                                       filter_by='',
                                       filter_by_value='', 
                                       group_by='')     
        else: 
            
            filter_by = f.d[ 'filter_by']
            filter_by_value = f.d[ 'filter_by_value']
            group_by = f.d[ 'group_by']
            
            queryData, recordcount = model.group_by(f.d , perpage)
            
            if queryData:
                #calculate page for pagination
   
                page = 1
                offset = (page - 1) * perpage                
                
                pages = recordcount / perpage                   
                
                if recordcount % perpage > 0:
                    pages += 1
                if page > pages:
                    raise web.seeother('/group_by')
                else :
                    #sort the results

                    sortedkeys = queryData[page].keys()
                    sortedkeys.sort()
                    
                    # render the page
                    return render.group_by(lform = f, 
                                           grouping=queryData[page], 
                                           sortedkeys = sortedkeys,
                                           pages=pages,
                                           filter_by=filter_by,
                                           filter_by_value=filter_by_value, 
                                           group_by=group_by)
            else:
                #render default page
                return render.group_by(lform=f,  
                                       grouping= '', 
                                       sortedkeys = '',
                                       pages=0,
                                       filter_by='',
                                       filter_by_value='', 
                                       group_by='')     


application = app.wsgifunc()

if __name__=="__main__":
    model.init_db()
    app.run()