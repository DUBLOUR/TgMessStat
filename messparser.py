#def prepare_data(file_name="result.json"):
def prepare_data(file_name="result_short.json"):
    import datetime
    import time
    import json
    import numpy as np

    min_in_day = 1440
    my_name = str()
    peoples_name = dict()

    def get_contacts_data():
        nonlocal peoples_name

        me = base["personal_information"]
        nonlocal my_name
        my_name = me["first_name"] + " " + me["last_name"]
        peoples_name[me["user_id"]] = my_name
        
        contacts = base["frequent_contacts"]["list"]
        for x in contacts:
            if "category" in x and x["category"] == "people":
                peoples_name[x["id"]] = str(x["name"])

        

    def parse_chat(chat):

        def get_score(mess):
            def get_len(text):
                if isinstance(text, str):
                    return len(text)
                res = 0
                for x in text:
                    if isinstance(x, str):
                        res += len(x)
                    else:
                        res += len(x["text"])
                return res


            text_len = get_len(mess["text"]) #can be string or list of object
            photo = int("photo" in mess)
            voice_len = 0
            sticker = 0
            
            if "media_type" in mess:
                tp = mess["media_type"]
                if (tp == "voice_message" or tp == "animation") \
                        and "duration_seconds" in mess:
                    voice_len = mess["duration_seconds"]
                    
                if tp == "sticker":
                    sticker = 1

                if tp == "audio_file" or tp == "video_file":
                    pass

            score = (
                text_len * 1 + 
                voice_len * 10 + 
                photo * 25 +
                sticker * 5)

            if score > 2000: 
                # As usually is a big part of copy-paste; 
                # Exclude for selection cleannes
                score = 1
                #print(str(mess)[:200])

            return score
            

        if chat["type"] == "saved_messages":
            companion_name = my_name
        else:
            if chat["id"] in peoples_name:
                companion_name = peoples_name[chat["id"]]
            else:
                companion_name = chat["name"] # BUG!!!
        
        sum_all = np.zeros(3, dtype=np.intc)
        sum_score = np.zeros((2,min_in_day), dtype=np.intc)
        calendar = dict()

        for mess in chat["messages"]:
            if mess["type"] == "service":
                continue

            time = datetime.datetime.fromisoformat(mess["date"])
            minute_of_day = time.hour * 60 + time.minute 
            day = time.date()
            
            author_id = mess["from_id"]
            
            if author_id in peoples_name:
                author = peoples_name[author_id]
            else:
                author = mess["from"]
            if "forwarded_from" in mess:
                author = mess["forwarded_from"]
            if author not in [my_name, companion_name]:
                author = "other"

            score = get_score(mess)

            if day not in calendar:
                calendar[day] = score
            else:
                calendar[day] += score

            if author == my_name:
                sum_score[0,minute_of_day] += score
                sum_all[0] += score
            elif author == companion_name:
                sum_score[1,minute_of_day] += score
                sum_all[1] += score
            else:
                sum_all[2] += score
            

        if companion_name == my_name:
            companion_name = "Saved messages"
        if str(companion_name) == "None":
            companion_name = "Deleted"
        return companion_name,sum_all,sum_score,calendar



    fh = open(file_name, "r")
    base = json.load(fh)

    get_contacts_data()

    chats_data = []
    for chat in base["chats"]["list"]:
        chats_data.append(parse_chat(chat))
    chats_data.sort(key=lambda a: sum(a[1]), reverse=True) 


    return my_name,chats_data
