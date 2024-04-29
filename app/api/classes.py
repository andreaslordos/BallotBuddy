from peewee import Model, CharField, DateTimeField, ForeignKeyField, BooleanField
from datetime import datetime
from .clients import db, openai_client
from .civic_api_wrapper import get_voter_info, updateElections


# editable args passed to OpenAI function params later on
editableArgsDescriptions = {'street_address': {'type': 'string', 'description': 'The users street address. This must be filled before the getPollingPlace function is called'},
                            'state': {'type': 'string', 'description': 'The two letter description of the users state (e.g. CA = California, etc.). This must be filled before the getPollingPlace function is called'},
                            'postcode': {'type': 'string', 'description': "The users postcode, 5 digits. This must be filled before the getPollingPlace function is called"},
                            'city': {'type': 'string', 'description': 'The users city. This must be filled before getPollingPlace function is called'},
                            }


class User(Model):
    '''
    Represents a user in the system
    '''
    phone = CharField() # user's phone number
    street_address = CharField(null=True)
    state = CharField(null=True)
    postcode = CharField(null=True)
    city = CharField(null=True)
    essentials = ['street_address', 'state', 'postcode', 'city'] # essential attributes that must be filled before sending a polling location request in
    editableArgs = list(editableArgsDescriptions) # args that can be edited by the AI
    assert(all(map(list(editableArgsDescriptions).__contains__, essentials))) # check: all essential args must also be editable args

    # TODO: add messaging service attribute here. Then search based on phone + messaging service. will allow for multi platform

    class Meta:
        database = db


    @staticmethod
    def getEditables():
        '''
        Return editable args descriptions
        '''
        return editableArgsDescriptions    

    def updateDetails(self, details):
        '''
        Update attributes. Guaranteed to be only editable arguments since that's what the GPT can call this function on.
        '''
        for key, value in details.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return True
    
    def getInfo(self):
        '''
        Return a dictionary representation of the user's address, along with an entry of the attributes that are still missing
        '''
        dict = {'fields': {}}
        for publicArg in self.editableArgs:
            dict['fields'][publicArg] = getattr(self, publicArg)
        dict['missing'] = self.still_missing()
        return dict
    
    def still_missing(self):
        '''
        Figure out what optional and mandatory attributes are still missing.
        '''
        print("Trying to figure out what attributes are still missing")
        optional_missing = []
        mandatory_missing = []
        editable_attributes = self.getEditables().keys()
        for attribute in editable_attributes:
            value = getattr(self, attribute, None)
            print(attribute, value)
            if attribute in self.essentials and value is None:
                mandatory_missing.append(attribute)
            elif value is None:
                optional_missing.append(attribute)
        print("Mandatory attributes still missing:",str(mandatory_missing))
        print("Optional attributes still missing:",str(optional_missing))
        return {'mandatory_address_fields_missing': mandatory_missing, 'optional_address_fields_missing': optional_missing}
    

    def can_send(self):
        '''
        Check if you can send the polling location request (i.e. if all essentials have been fulfilled)
        '''
        for essential in self.essentials:
            if getattr(self, essential) is None:
                return False
        return True

    def createNewThread(self):
        '''
        Creates new thread for the user, returns thread instance
        '''
        print("Creating new thread object")
        new_thread = Thread.create(user=self)
        print("New thread object created")
        print("Adding system message with elections data")
        new_thread.systemMessage(f"These are the upcoming elections and their relevant IDs: {str(updateElections())}") 
        return new_thread

    def addToThread(self, message):
        '''
        Fetches users latest thread and adds the user's message to it. Returns thrad ID
        '''
        # fetch latest thread that isn't expired
        latest_thread = self.getLatestThread()
        print("Adding new message to thread belonging to",self.phone)
        latest_thread.addMessage(message)
        return latest_thread.threadId

    def getLatestThread(self):
        '''
        Get latest thread's ID, or return a new thread ID if the latest is expired
        '''
        if self.threads.count() > 0:
            latest_thread = self.threads.order_by(Thread.lastAccessed.desc()).get()
            if not latest_thread.threadIsExpired():
                print("Thread not expired, returning old thread")
                return latest_thread
        return self.createNewThread()
    
    def getPollingPlace(self, arguments):
        '''
        Get user polling place based on address
        '''
        if not self.can_send():
            return "Do not have sufficient user info to get polling location. Check missing address arguments"
        formatted_addr = f"{self.street_address}, {self.city}, {self.state} {self.postcode}"
        electionId = arguments['electionId']
        return get_voter_info(formatted_addr, electionId)        

class Thread(Model):
    threadId = CharField(unique=True, default=lambda: openai_client.beta.threads.create().id) # openAI thread ID
    user = ForeignKeyField(User, backref='threads') # user that the thread belongs to
    lastAccessed = DateTimeField(default=datetime.now) # timestamp of last access to thread by user
    createdAt = DateTimeField(default=datetime.now) # timestamp for creation date

    class Meta:
        database = db

    def addMessage(self, message):
        '''
        Add a message to the thread, update last accessed
        '''
        print("Adding message to thread")
        thread_message = openai_client.beta.threads.messages.create(thread_id = self.threadId, role="user", content=message)
        print("Updating last accessed of thread")
        self.lastAccessed = datetime.now()
        print("Saving update")
        self.save()
    
    def systemMessage(self, message):
        '''
        Add a system message when creating the thread
        '''
        print("Adding system message to thread")
        print("System message:", message)
        system_message = openai_client.beta.threads.messages.create(thread_id = self.threadId, role="user", content=message)

    def threadIsExpired(self, EXPIRE_DAY_LIMIT=2):
        '''
        Returns true if the thread is expired (default 2 days expiry)
        '''
        print("Checking if thread is expired")
        DAY_IN_UNIX_TIME = 86400
        return (datetime.now() - self.lastAccessed).total_seconds() > EXPIRE_DAY_LIMIT * DAY_IN_UNIX_TIME