import togglws
import asyncio
import requests

currentTimerEndpoint = "https://api.track.toggl.com/api/v8/time_entries/current"
token = "api_token" # PUT HERE YOUR API TOKEN, BRO
password = "api_token" # DO NOT CHANGE THIS

def turnOn():
    print('Turned on')

def turnOff():
    print('Turned off')

timerId = -1

async def main():
    async with togglws.TogglClient(token) as tc:
        
        # Set a handler for any time a time entry is created or updated
        tc.handle(
            actions=[togglws.A_INSERT, togglws.A_UPDATE],
            models=[togglws.M_TIME_ENTRY],
            handler=message_handler
        )
        
        # Continuously listen for messages, and call the handler whenever
        # a matching message is received.
        await tc.run()


async def message_handler(action: str, model: str, msg: togglws.TogglSocketMessage):
    print(f'Received message: {action} {model} - {msg.to_dict()}')
    global timerId
    if action == togglws.A_INSERT:
        running = msg.to_dict()['data']['time_entry']['stop'] is None
        if running:
            turnOn()
            timerId = msg.to_dict()['data']['time_entry']['id']
            print(f'New timer with id {timerId} started')
    elif action == togglws.A_UPDATE:
        running = msg.to_dict()['data']['time_entry']['stop'] is None
        if timerId == msg.to_dict()['data']['time_entry']['id'] and not running:
            print(f'Timer with id {timerId} stopped')
            turnOff()
            timerId = -1
    else:
        print(f'Ignoring msg: {action} {model} - {msg.to_dict()}')

def getRunningTimerId():
    print('Checking is timer already running..')
    response = requests.get(currentTimerEndpoint, auth=(token, password), headers={'Connection':'close'})
    if (response.status_code == 200):
        json_data = response.json()
        response.close()
        if json_data['data'] is not None:
            return json_data['data']['id']
    else:
        print("error response code not ok ", response.status_code)
    
    return -1

if __name__ == '__main__':
    print('Starting..')
    timerId = getRunningTimerId()
    if timerId != -1:
        print(f"Found running timer with id {timerId}")
        turnOn()
    else:
        print("No running timer, bro")
        turnOff()
    asyncio.run(main())