

def view(day, progress):

    linksP = [[60,'Rodney Daut P','https://www.linkedin.com/posts/rodneydaut_failuretosuccess-linkedin30daysprint-activity-6886695645353127936-sRQx'],[61,'Rosey Hwang P','https://www.linkedin.com/posts/roseyhwang_coaching-business-entrepreneurship-activity-6886698097083224064-Lvdi']]
    linksC = [[60,'Rodney Daut C','https://www.linkedin.com/posts/rodneydaut_failuretosuccess-linkedin30daysprint-activity-6886695645353127936-sRQx'],[61,'Rosey Hwang C','https://www.linkedin.com/posts/roseyhwang_coaching-business-entrepreneurship-activity-6886698097083224064-Lvdi']]


    view = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": f"Posts Day {day} {progress}",
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
        },

    for i,l in enumerate(linksP):

        view['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":white_check_mark: <{l[2]}|{l[1]}>"
                        },
            },
            {
                "type": "section",
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Commented",
                        "emoji": True
                        },
                    "value": "Commented",
                    "action_id": f"{l[0]}"
                    },
            },
        )


    view['blocks'].append({
                "type": "divider"
            },
            {
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
                        "text": f":white_check_mark: <{l[2]}|{l[1]}>"
                        },
                })

    return view

print(view(1,'asasa'))
