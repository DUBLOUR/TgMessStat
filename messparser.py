import datetime
import time
import json
import numpy as np
from random import shuffle  


def prepare_data(file_name="result.json", summary=True, privacy_mode=False):

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
            
        def get_his_name_and_id():
            if chat["type"] == "saved_messages":
                return my_name, my_id
        
            his_name = chat["name"]
            his_id = 0

            for mess in chat["messages"]:
                if mess["type"] == "service":
                    continue

                if "forwarded_from" not in mess and mess["from_id"] != my_id:
                    #If message in not forwarded then is can be only I or he
                    his_name = mess["from"]
                    his_id = mess["from_id"]
                    break
            
            #if isinstance(his_id, str) and len(his_id) >= 4 and his_id[:4] == "user":
            #    his_id = int(his_id[4:])
            
            return his_name, his_id


        his_name,his_id = get_his_name_and_id()
        print(his_name,his_id)

        sum_all = np.zeros(3, dtype=np.intc)
        sum_score = np.zeros((2, 24*60), dtype=np.intc)
        calendar = dict()

        for mess in chat["messages"]:
            if mess["type"] == "service":
                continue

            time = datetime.datetime.fromisoformat(mess["date"])
            minute_of_day = time.hour * 60 + time.minute 
            day = time.date()
            
            score = get_score(mess)

            if day not in calendar:
                calendar[day] = score
            else:
                calendar[day] += score


            author_id = mess["from_id"]
            #if isinstance(author_id, str) and len(author_id) >= 4 and author_id[:4] == "user":
            #    author_id = int(author_id[4:])
            if "forwarded_from" in mess:
                author_id = 0

            #print(my_id, his_id, author_id)

            author = [my_id, his_id, author_id].index(author_id)

            sum_all[author] += score
            if author != 2:
                sum_score[author, minute_of_day] += score

        if his_name == my_name:
            his_name = "Saved messages"
        if str(his_name) == "None":
            his_name = "Deleted"

        #TODO: add check on emoji in name

        return [his_name, sum_all, sum_score, calendar]


    def add_summary():
        sum_all = np.zeros(3, dtype=np.intc)
        sum_score = np.zeros((2, 24*60), dtype=np.intc)
        calendar = dict()

        for chat in chats_data:
            sum_all += chat[1]
            sum_score += chat[2]

            for x in chat[3].keys():
                if x not in calendar:
                    calendar[x] = 0
                calendar[x] += chat[3][x]

        chats_data.append(["Summary", sum_all, sum_score, calendar])



    def change_names_to_random():
        def gen_rand_names(n):
                #Thank to github.com/sindresorhus/supervillains for this list
            fh = open("random_names.json", "r")
            names = json.load(fh)

            while len(names) < n:
                names.append(*names)
            shuffle(names)
            print(n, names)
            return names[:n]


        nonlocal chats_data
        count_of_chats = len(chats_data)
        random_names = gen_rand_names(count_of_chats)
        for i in range(count_of_chats):
            chats_data[i][0] = random_names[i]



    fh = open(file_name, "r")
    base = json.load(fh)
    fh.close()

    me = base["personal_information"]
    my_name = me["first_name"] + " " + me["last_name"]
    my_id = "user" + str(me["user_id"])

    chats_data = []
    for chat in base["chats"]["list"]:
        if chat["type"] in ["saved_messages", "personal_chat"]:
            chats_data.append(parse_chat(chat))

    if summary:
        add_summary()

    chats_data.sort(key=lambda a: sum(a[1]), reverse=True) 

    if privacy_mode:
        change_names_to_random()

    return my_name, chats_data
