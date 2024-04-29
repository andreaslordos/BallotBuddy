import os
from .classes import User

# Base instruction for model
BASE_INSTRUCTION = "You are an assistant who helps users find their closest polling location for upcoming elections that they can vote using the Google Civic API. You will be provided the IDs and dates of upcoming elections in the first message of the thread, which you will then use to call the API (to find out polling place, you need full address). You have instructions on how to register to vote, voter registration deadlines and checking voter registration for each state in your files, you can access that using file search - to give that kind of information, you only need their state."

def buildInstruction(user, initial=BASE_INSTRUCTION):
    '''
    Append user specific instructions to base instruction, return user specific model instruction
    '''
    info = user.getInfo()
    initial += f"User's provided address so far: {str(info['fields'])} \n \n"
    initial += f"The following MANDATORY fields are missing from the address: {str(info['missing']['mandatory_address_fields_missing'])} \n \n"
    initial += f"The following OPTIONAL fields are missing from the address: {str(info['missing']['optional_address_fields_missing'])} \n \n"
    return initial

def createAssistant(client):
    '''
    Create the assistant and return it
    '''
    print("Uploading RAG file")
    # Create a vector store caled "All States - Voter Registration Instructions"
    vector_store = client.beta.vector_stores.create(name="Voter Registration Instructions")
    
    # Ready the files for upload to OpenAI 
    file_paths = ["app/get_rag_data/all_states_data.md"]
    file_streams = [open(path, "rb") for path in file_paths]
    
    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    print("Creating assistant")
    assistant = client.beta.assistants.create(
        name="BallotBuddy",
        instructions=BASE_INSTRUCTION,
        tools=[
            {"type": "file_search"},
            {"type": "function",
                "function": {
                    "name": "getPollingPlace",
                    "description": "Fetch information about the polling place. ONLY CALL THIS FUNCTION IF YOU HAVE THE FULL ADDRESS, DO NOT TRY TO INFER THE ADDRESS",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "electionId": {
                                "type": "string",
                                "description": "The ID of the election you're querying about. This can be inferred from the user's address and looking at which elections you have information about."
                            }
                        },
                        "required": ["electionId"]
                    }
                }
            },
            {"type": "function",
                "function": {
                    "name": "updateDetails",
                    "description": "Update the User's address with relevant info.",
                    "parameters": {
                        "type": "object",
                        "properties": User.getEditables(),
                        "required": []
                    }
                }
            },
        ],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        model="gpt-4-turbo-preview"
    )
    print(f"Created new assistant with ID: {assistant.id}")
    return assistant


