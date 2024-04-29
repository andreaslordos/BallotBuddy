import json
import time
from .clients import openai_client as client
from .agent_instructions import buildInstruction

# Get the previous messages in a chat/Thread
def get_messages_in_chat(threadID):
    messages = client.beta.threads.messages.list(thread_id=threadID)
    return messages

# Run the thread with the assistant and custom user specific instructions
def run_chat(threadID, assistantID, user):
    customInstructions = buildInstruction(user) # TODO: If this isn't the first time building the instruction, add customInstruction = '' so you're not resending the base prompt each time.
    run = client.beta.threads.runs.create(thread_id=threadID, assistant_id=assistantID, instructions=customInstructions)
    return run

# Main Assistant thread
def askBallotBuddy(threadID, assistantID, user):
    # input: threadID, assistantID, user instance
    # return: list of messages to return to user

    # handles Function calling, return output of GPT-called functions
    def process_run_object(run_object):
        tool_calls = run_object.required_action.submit_tool_outputs.tool_calls
        outputs = []
        for call in tool_calls:
            tool_call_id = call.id
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)  # Assuming arguments are already in the form of a dictionary
            print(f"{tool_call_id}: calling {function_name} with arguments: {arguments}")
            
            # Based on the function name, decide which Python function to call.
            if function_name == "getPollingPlace":
                result = user.getPollingPlace(arguments)
            if function_name == "updateDetails":
                assert(user.updateDetails(arguments))
                result = user.getInfo()
            # Append the output for this function call to the outputs list
            outputs.append({"tool_call_id": tool_call_id, "output": str(result)})
        print(f"Returning outputs {outputs}")
        return outputs

    print("-----")
    print("Asking BallotBuddy for a response")
    # Poll the Assistants API for a completed response from an assistant run
    run = run_chat(threadID, assistantID, user)
    while True:
        print("askBallotBuddy response status: %s", run.status)
        if run.status == 'completed':
            print("Received completed response from askBallotBuddy")
            break
        elif run.status == 'failed':
            # something went wrong
            print("Failed")
            return ["Something went wrong, please try again later."]
        elif run.status == 'requires_action':
            print("askBallotBuddy response requires action")

            # Get the action prompt from the run
            toolId = run.required_action.submit_tool_outputs.tool_calls[0].id
            runId = run.id

            print("Tool ID: {} and Run ID: {} and Thread ID: {}".format(toolId, runId, threadID))

            toolOutputs = process_run_object(run)

            client.beta.threads.runs.submit_tool_outputs(
                run_id=runId,
                thread_id=threadID,
                tool_outputs=toolOutputs
            )

            print("askBallotBuddy response action submitted")


        time.sleep(1)  # wait for 1 second before polling the status again
        run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=threadID)         
    
    response = get_messages_in_chat(threadID) # load all messages in chat
    response_modified = list(response)[0] # get latest response
    response_content = response_modified.content # get content of latest response
    response_list = []
    
    for r in response_content:
        # TODO: Check that r has .text.value
        response_list.append(r.text.value)
    
    # print("Returning: ", response_list)
    print("-----")
    return response_list
