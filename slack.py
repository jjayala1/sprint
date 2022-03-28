import logging
#logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
#slack_user_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_bot_token)


def test_message():
    try:
        response = client.chat_postMessage(
            channel="C01N6K5RFN1",
            text="Hello from your app! :tada:"
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'




def get_users():
    users_store = {}

    # Put users into the dict
    def save_users(users_array):
        for user in users_array:
            # Key user info on their unique user ID
            user_id = user["id"]
            if 'first_name' not in user['profile']:
                user['profile']['first_name'] = ''
                user['profile']['last_name'] = ''

            # Store the entire user object (you may not need all of the info)
            users_store[user_id] = {'name': user['name'],
                                    'real_name': user['profile']['real_name'],
                                    'display_name': user['profile']['display_name'],
                                    'complete_name': user['profile']['first_name'] + "" + user['profile']['last_name']
                                   }

    try:
        # Call the users.list method using the WebClient
        # users.list requires the users:read scope
        result = client.users_list()
        print('------------------------------------------------------------------')
        save_users(result["members"])
        print(users_store)
        print('------------------------------------------------------------------')

    except SlackApiError as e:
        print(f'Error: {e}')

def get_profile():
    #result = client.users_info(user='U02UY929J86')
    result = client.users_profile_get(user='U02UY929J86')
    print(result)



get_profile()


