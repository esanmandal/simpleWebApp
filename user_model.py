import datetime
import os
"""
/rel/third_party/mongo/current/bin/mongod --config /usr/pic1/work/scripts/dataStructure/webApp/mongo.config
/rel/third_party/mongo/current/bin/mongod --dbpath /usr/pic1/work/mongodb_test/mongo-data --logpath /usr/pic1/work/mongodb_test/mongodb.log --logappend
/rel/third_party/mongo/current/bin/mongo localhost:27017

"""

class UserModel:
    def __init__(self, db=None):
        self._db = db
        self._collection = self._db.test
        
    # Create database tables
    def init_db(self):
        """
        Initialize the database
        """
        # Name of the collection is "test"
        # If the collection is empty then populate it
        if self._collection.count() < 1:
            self.populate_data()
        

    def create(self, data):
        """
        Add data to the database
        """
        now = str(datetime.datetime.now())
        # Do some validation on the data and then insert it.
        mongoData = {}
        mongoData['username'] = data['username'].lower()
        mongoData['firstname'] = data['firstname'].lower()
        mongoData['lastname'] = data['lastname'].lower()
        mongoData['sex'] = data['sex'].lower()
        mongoData['password'] = data['password']
        mongoData['email'] = data['email'].lower()
        mongoData['city'] = data['city'].lower()
        mongoData['state'] = data['state'].lower()
        mongoData['zip'] = data['zip']
        mongoData['creation time'] = now
        self._collection.insert(mongoData)
    def delete_all(self):
        """
        Delete the current collection in the database
        """
        self._collection.remove()
        

    def get_all(self):
        result = list(self._collection.find().sort(u'firstname'))
        return result

        
    def validate_login(self,data):
        """
        Validate Username and Password for login 
        """
        uname = data['username'].lower()
        pword = data['password']
        res = self._collection.find_one({'username':uname, 'password':pword})
        if not res:
            return None
        if res['username'] == uname and res['password'] == pword:
            return res
        else: return None
                 

    def list_dir_contents(self,dir):
        """
        List contents of a directory
        """
        try:
            return os.listdir(dir)
        except OSError, e:
            return (e)
       

    def group_by(self,data, perpage):
        """
        Filter and group data in the database
        """
        
        filter = data['filter_by'].lower()
        filter_value = data['filter_by_value'].lower()
        group = data['group_by'].lower()
        
        #query the data base
        if filter_value == '*':
            filter_result = self._collection.find().sort(u'firstname')
        else:
            filter_result = self._collection.find({filter:filter_value}).sort(u'firstname')
        
        #group by the group parameter
        groupd = {}
        perpageGrouped = {}
        page  = 1
        cnt = 1
        
        # group results in per page chunks 
        for r in filter_result:
            parm = r[group]
            if parm in groupd.keys():
                groupd[parm].append(r)
            else:
                groupd[parm] = [r]
            if cnt < perpage:
                cnt += 1
            else:
                perpageGrouped[page] = groupd.copy()
                page += 1
                cnt = 1
                groupd.clear()
        
        # any left over data that only partially fills a page
        if len(groupd.keys()):
            perpageGrouped[page] = groupd.copy()
        
        return (perpageGrouped,filter_result.count())
        

        
    
    def populate_data(self):
        """
        Populate the database with random data
        """
        import random
        names = ['James', 'Jack', 'Helen', 'Marge', 'Tom', 'Dick', 'Harry', 'Chris', 'Matt', 'May', 'April', 'John', 'Tim', 'Donald']
        lastnames = ['Littlejohn', 'Kruger', 'Titus', 'Wlaters', 'Holmes', 'Lee', 'Kim', 'Hatfield', 'Head', 'Williamson']
        cities = ['Los angeles','Las Vegas','New York City','Portland','San Francisco', 'Orlando', 'Miami', 'Columbus']
        states = ['California', 'Nevada', 'Oregon', 'New York', 'Illinois', 'Virginia','Florida', 'Ohio', 'Texas']
        zips = [10000, 20000,30000,40000,50000,60000,70000,80000, 90000]
        sexs = ['Male','Female']
        packet ={}
        
        for i in range (200):
            n = random.randrange(len(names))    
            l = random.randrange(len(lastnames))    
            c = random.randrange(len(cities))    
            s = random.randrange(len(states))    
            z = random.randrange(len(zips)) 
            x = random.randrange(2)
            e = str(random.randrange(1000))
            packet['username'] = names[n]+lastnames[l]
            packet['firstname'] = names[n]
            packet['lastname'] = lastnames[l]
            packet['password'] = names[n]
            packet['sex'] = sexs[x]
            packet['email'] = names[n]+'.'+lastnames[l]+'_'+e+'@gmail.com'
            packet['city'] = cities[c]
            packet['state'] = states[s]
            packet['zip'] = zips[z]
            
            self.create(packet)