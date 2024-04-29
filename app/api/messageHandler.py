from .agent_utils import askBallotBuddy
from .clients import ASSISTANT_ID, db
from .classes import User
from .moderation import check_response

def getReply(phone, message):

    if not check_response(message):
        return "FAILED MODERATION CHECK"
    
    # connect to db
    db.connect()

    # check if user exists
    # if user exists, load user and store in var user
    print("Searching for user")
    user = User.select().where(User.phone == phone).first()
    
    
    # otherwise create new user with phone number, and store in var user
    if not user:
        print("User not found, creating now")
        user = User.create(phone=phone)
        print("User created")
    
    print("User loaded:", user)

    # add message to latest thread (created if it does not exist)
    currentThreadId = user.addToThread(message)
    print("Users latest thread ID:", currentThreadId)
    
    # at this point, you have currentThreadId which contains the ID of the most recent, with the newest message added
    # get response from AI
    returnedMessage = askBallotBuddy(currentThreadId, ASSISTANT_ID, user)
    
    # close db
    db.close()

    if not check_response('\n'.join(returnedMessage)):
        return "FAILED MODERATION CHECK"
    
    # return message from AI
    return '\n'.join(returnedMessage)