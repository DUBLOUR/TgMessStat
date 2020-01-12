import math
import datetime
import numpy as np
import matplotlib.pyplot as plt

def draw_chat(
    id, smooth_id, main_mode, 
    my_name, chat_day_data, 
    main_plot, pie_plot, list_chats_plot):

    min_in_day = 1440
    possible_smooth = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30, 32, 36, 40, 45, 48, 60]
    possible_smooth = [10, 12, 15, 16, 18, 20, 24, 30, 32, 36, 40, 45, 48, 60] #divisors of 1440 (min in day)
    

    count_of_chats = len(chat_day_data)
    id = (id + count_of_chats) % count_of_chats
    smooth_id = (smooth_id + len(possible_smooth)) % len(possible_smooth)
    
    smooth = possible_smooth[smooth_id]
    sum_score = chat_day_data[id][2]
    calendar = chat_day_data[id][3]
    companion_name = chat_day_data[id][0]
    
    def draw_main_plot_as_all():
        first_day = 0
        def gen_data():
            nonlocal first_day
            
            calendar_dates = list(calendar.keys())
            ind = [0]
            now = min(calendar_dates)
            first_day = now
            last = max(calendar_dates)
            duration = (last - now).days + 1
            need_space_btw_labels = duration // 25
            labels = [now]
            last_label = 0
            t = 0
            vals = [0] * duration
            vals[0] = calendar[now]
            
            while now != last:
                now += datetime.timedelta(days=1)
                t += 1
                if now in calendar_dates:
                    ind.append(t)
                    vals[t] = calendar[now]
                    if t-last_label >= need_space_btw_labels:
                        last_label = t
                        labels.append(str(now))
                    else:
                        labels.append("")
            
            def make_smoothie(a, shift):
                n = len(a)
                res = [0] * n
                
                koef = []
                for i in range(shift+1):
                    koef.append( max(0, math.cos(i/(shift+1))**2*2 - 1) )
                    
                for i in range(n):
                    sum = 0
                    sum_k = 0
                    for j in range(-shift, shift+1):
                        if 0 <= i+j < n:
                            k = koef[abs(j)]
                            sum += a[i+j] * k
                            sum_k += k
                    res[i] = sum / sum_k
                return res

            s = int((duration/50)**0.5) #random.randint(0,10)
            print(duration, s)
            vals = make_smoothie(vals, s)

            return ind,labels,vals

        width = 1 # default value
        plot = main_plot
        
        plot.clear()
        ind, labels, vals = gen_data()
        plot.set_xticks(ind)
        plot.set_xticklabels(labels)
        plot.xaxis.set_tick_params(rotation=90)
        #plot.bar(ind, vals, width)
        plot.bar(range(len(vals)), vals, width)
                
        def format_coord(x, y):
            day = int(x + 0.5)
            day = first_day + datetime.timedelta(days=day)
            #print(day,y)
            val = 0
            if day in calendar:
                val = calendar[day]
                if val > 512:
                    val = str(val // 1024) + "." + str(int((val % 1024 / 102.4 + 0.5)))
                    val += "Kb"
                return str(day) + "   " + str(val)
            return str(day)

        plot.format_coord = format_coord
        #plot.set_yscale('log')


    def draw_main_plot_as_day():
        N = min_in_day // smooth
    
        def set_smooth(score, smooth):
            res = [0] * N
            for i in range(min_in_day):
                res[i//smooth] += score[i]
                #res[i] = sum(score[i*smooth:(i+1)*smooth])
            return res

        me_score = set_smooth(sum_score[0], smooth)
        he_score = set_smooth(sum_score[1], smooth)

        ind = np.arange(N)
        width = 1 
        def gen_time_labels():
                # Set step between labels for they count of be near the 24
            k = int(N / 24 + 0.5) 

            def time(t):
                # get time in format `h:mm` from `t` as minute
                return str(t//60) + ":" + str(t//10%6)+str(t%10)
            labels = [time(x*smooth) if x % k == 0 else "" 
                      for x in range(N)]
            return labels    

        width = 0.8 # default value
        plot = main_plot
        
        plot.clear()
        plot.set_xticks(ind)
        plot.set_xticklabels(gen_time_labels())
        plot.xaxis.set_tick_params(rotation=90)
        p1 = plot.bar(ind, me_score, width)
        p2 = plot.bar(ind, he_score, width, bottom=me_score)
        plot.legend((p1[0], p2[0]), (my_name, companion_name))

        def format_coord(x,y):
            x = int(x+0.5)
            if 0 <= x < len(me_score) and me_score[x] + he_score[x]:
                rate = me_score[x] / (me_score[x] + he_score[x])
                return f"rate: {rate*100:.2f}%"
                
            return None

        plot.format_coord = format_coord

    def draw_main_plot(mode):
        if mode == 0:
            draw_main_plot_as_day()
        else:
            draw_main_plot_as_all()


    def draw_pie():
        sizes = chat_day_data[id][1]
        explode = [0, 0, 0.1] 
        pie_plot.clear()

        def get_angle():
            # Set green part (forwarded message) in central bottom part
            return -90 + 360*(sizes[2]/(2*sum(sizes)))

        pie_plot.pie(sizes, explode=explode, autopct='%1.1f%%',
                shadow=True, startangle=get_angle())
        pie_plot.format_coord = lambda x,y: None
    
    def draw_list_chats(id):
        chats_above = 4
        chats_bottom = 5

        if count_of_chats < chats_above + 1 + chats_bottom:
            chats_above = id
            chats_bottom = count_of_chats - id - 1

        if id < chats_above:
            chats_bottom += chats_above - id
            chats_above = id
        if id + chats_bottom >= count_of_chats:
            chats_bottom = count_of_chats - id - 1

        plot = list_chats_plot
        N = chats_above + 1 + chats_bottom
        people = []
        scores = []
        for i in range(-chats_above, chats_bottom+1):
            people.append(chat_day_data[i+id][0])
            scores.append(sum(chat_day_data[i+id][1]))

        selected_chat = [0] * N
        selected_chat[chats_above] = scores[chats_above]

        plot.clear()
        plot.set_yticks(range(N))
        plot.set_yticklabels(people)
        plot.invert_yaxis() 
        plot.yaxis.tick_right()
        plot.invert_xaxis()
        plot.axes.get_xaxis().set_visible(False)
        #plot.axes.get_yaxis().set_ticks([])

        bars = plot.barh(range(N), scores)
        plot.barh(range(N), selected_chat)
        plot.format_coord = lambda x,y: None

        for bar in bars:
            continue
            height = bar.get_y() + bar.get_height() / 2
            width = bar.get_x() + bar.get_width()
            plot.annotate(f' {str(width)[:]}',
                        xy=(width, height),
                        ha='left', va='center')


    draw_main_plot(main_mode)
    draw_pie()
    draw_list_chats(id)
    plt.draw()


