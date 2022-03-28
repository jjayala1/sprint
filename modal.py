

def get_view_posts(day, links):

    #linksP = [[60,'Rodney Daut P','https://www.linkedin.com/posts/rodneydaut_failuretosuccess-linkedin30daysprint-activity-6886695645353127936-sRQx'],[61,'Rosey Hwang P','https://www.linkedin.com/posts/roseyhwang_coaching-business-entrepreneurship-activity-6886698097083224064-Lvdi']]
    #linksC = [[60,'Rodney Daut C','https://www.linkedin.com/posts/rodneydaut_failuretosuccess-linkedin30daysprint-activity-6886695645353127936-sRQx'],[61,'Rosey Hwang C','https://www.linkedin.com/posts/roseyhwang_coaching-business-entrepreneurship-activity-6886698097083224064-Lvdi']]
    #linksP = links

    linksP = []
    linksC = []
    auth_com = 0

    for l in links:
        if l[5] is None or l[5] == '' or l[5] == '0':
            linksP.append(l)
        else:
            linksC.append(l)
            auth_com += int(l[5])

    tot_posts = len(links)
    progress = f"{auth_com}/{tot_posts}"

    view = {
        "type": "modal",
        "clear_on_close": True,
        "title": {
            "type": "plain_text",
            "text": f"Day # {day}. Progress {progress}",
            "emoji": True
            },
        "close": {
            "type": "plain_text",
            "text": "Close",
            "emoji": True
            },
        "blocks": [
            {
                "type": "divider"
            },

            {
                "type": "context",
                "elements": [
                    {
                        "type": "image",
                        "image_url": "https://api.slack.com/img/blocks/bkb_template_images/highpriority.png",
                        "alt_text": "Pending"
                        },
                    {
                        "type": "mrkdwn",
                        "text": "*Pending*"
                        }
                    ]
            }
            ]
        }

    for i,l in enumerate(linksP):

        view['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":white_check_mark: <{l[3]}|{l[2]}> ({l[4]})"
                        },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Commented",
                        "emoji": True
                        },
                    "value": f"{day}",
                    "action_id": f"{l[0]}",
                    "style": "primary"
                    },
            })

    view['blocks'].append({
                "type": "divider"
            })

    view['blocks'].append({
                "type": "context",
                "elements": [
                    {
                        "type": "image",
                        "image_url": "https://api.slack.com/img/blocks/bkb_template_images/mediumpriority.png",
                        "alt_text": "Completed"
                        },
                    {
                        "type": "mrkdwn",
                        "text": "*Completed*"
                        }
                    ]
            })

    for i,l in enumerate(linksC):

        view['blocks'].append({
                 "type": "section",
                 "text": {
                     "type": "mrkdwn",
                     "text": f":white_check_mark: <{l[3]}|{l[2]}>"
                     },
                })

    print(view)
    print('---------------------------')

    return view



def get_view_new_post(day):

    options = []

    for i in range(int(day),0,-1):
        options.append({
			"text": {
				"type": "plain_text",
				"text": f"{i}",
				"emoji": True
			},
			"value": f"{i}"
		       })

    view = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": f"New Post",
            "emoji": True
            },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
            },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
            },
        "blocks": [
            {
                "type": "divider"
            },
            {
		"type": "input",
		"element": {
			"type": "static_select",
			"placeholder": {
				"type": "plain_text",
				"text": "Select day",
				"emoji": True
			},
			"options": options, 
			"action_id": "static_select-action",
                        "initial_option": options[0]
		},
		"label": {
			"type": "plain_text",
			"text": "Day:",
			"emoji": True
		},
                "block_id": "combo_day",
    	    },
            {
	    	"type": "input",
    		"element": {
	    		"type": "plain_text_input",
    			"action_id": "plain_text_input-action",
			"placeholder": {
				"type": "plain_text",
				"text": "Write the URL of your LinkedIn post",
				"emoji": True
			},
		    },
	    	"label": {
    			"type": "plain_text",
		    	"text": "Link:",
	    		"emoji": True
        		},
                "block_id": "link",
	    },
        ]
        }
    return view


def get_view_new_post_status(status):

    if status == 'link':
        message = '*You must write your link, for example:\n\n /np https://www.linkedin.com/feed/update/urn:li:activity:6889597796/\n\nor\n\n/np https://www.linkedin.com/posts/michael-nixon-a05265211_marines-marinecorps-incentives-activity-6889595644080603137-Td_Y*'

    elif status == 'ok':
        message = '*Link registered successfully*'

    elif status == 'error':
        message = '*Error: Contact admin please*'

    else:
        message = '*Error: Contact admin please*'

    view = {
            "type": "modal",
            "clear_on_close": True,
            "title": {
                "type": "plain_text",
                "text": "Save status"
            },
            "close": {
                "type": "plain_text",
                "text": "Close",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{message}"
                    }
                }
                ]
            }
    return view

if __name__ == "__main__":

    links = [[60,1,'Rodney Daut P','https://www.linkedin.com/posts/rodneydaut_failuretosuccess-linkedin30daysprint-activity-6886695645353127936-sRQx',3,1],[61,1,'Rosey Hwang P','https://www.linkedin.com/posts/roseyhwang_coaching-business-entrepreneurship-activity-6886698097083224064-Lvdi',4,None]]
    #print(get_view_posts(1, links))
    print(get_view_new_post_status('ok'))
