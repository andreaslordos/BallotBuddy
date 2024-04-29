from api.messageHandler import getReply

# Manual test in terminal
if __name__ == '__main__':
    phoneNo = input("Phone number: ")
    while True:
        message = input(f"{phoneNo}: ")
        returnMsg = '\n'.join(getReply(phoneNo, message))
        print(f"BallotBuddy: {returnMsg}")