import psycopg2
try:
    conn = psycopg2.connect("dbname='201701055' user='201701055' host='10.100.71.21' password='sanskari'")
    #print("Yes i m in database")
    cur=conn.cursor()
    cur.execute("""set search_path to sm""")
    
    print("""Here we begin's\n
             select the queries from the below options : \n
             1. Trend Worldwide
             2. Trend for respective country
             3. List of Posts of a given trend Number
             4. Number of Active users             
             5. Feed of the given user
             6. list of post in which you were tagged
             7. Which month has highest number of messaging
             8. Most Number of messages by country and month
             9. No of users joined according to there age
             10.No of users joined according to there age and country
             11.No of users joined according to country and year of joining
             12.Country having the maxmimum number of verified users
             13.List users followed by the given user havn't posted yet
             14.List of users which is followed back for a given user
             15.Exit

""")
    while 1:
        choice=int(input('Enter the Query number from above table : '))
        if choice == 1:
            str_query="""select * from trend limit 20"""
            cur.execute(str_query)
            rows=cur.fetchall()
            print("Trend's Worldwide")
            for row in rows:
                print(row[0],row[1],"\n  with ",row[2]," post's" )
                print('\n')
        elif choice == 2:
            region=input("Enter the region : ")
            str_query="""select row_number()over(order by count(tags)DESC) as trend_num,unnest(tags),count(tags) from hash_extract
			natural join post where region='"""+region+"""'
			group by tags
			order by count(tags) DESC limit 20;"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[0],row[1],"\n  with ",row[2]," post's" )
                print('\n')
        elif choice == 3:
            print("Enter the Trend_num : ")
            num=input()
            print("""Enter the sorting type : \n
                     1. Top tweets
                     2. Latest
                     3. Most liked
                """)
            print("Enter the choice: ")
            tmp=int(input())
            if tmp==1:
                str_query="""select C.first_name,C.last_name,B.tweet,B.post_time,B.num_likes from hash_tags A, post B,users C, verified D
                            where A.unnest=(select unnest from trend where trend_num="""+num+""") and A.post_id=B.post_id and B.user_id=C.user_id
                            and C.user_id=D.user_id order by is_verified DESC;"""
            elif tmp==2:
                str_query="""select C.first_name,C.last_name,B.tweet,B.post_time,B.num_likes from hash_tags A, post B,users C, verified D
                             where A.unnest=(select unnest from trend where trend_num="""+num+""") and A.post_id=B.post_id and B.user_id=C.user_id
                             and C.user_id=D.user_id order by  B.post_time DESC;
                             """
            elif tmp==3:
                str_query="""select C.first_name,C.last_name,B.tweet,B.post_time,B.num_likes from hash_tags A, post B,users C, verified D
                             where A.unnest=(select unnest from trend where trend_num="""+num+""") and A.post_id=B.post_id and B.user_id=C.user_id
                             and C.user_id=D.user_id order by  B.num_likes DESC;
                            """
            else:
                print('Invaild!!!!')
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[0],row[1],'posted : ',row[2],'\n','on',row[3],'Likes:',row[4])
                print('\n \n')
        elif choice == 4:
            str_query="""select count(*) from users where exists(select user_id from post where post.user_id = users.user_id 
								 and( post.post_time between (current_date - interval '1' month)
									 and current_date + interval '1' year))
                        or
                        (exists(select user_id from messaging where  messaging.sender_id = users.user_id 
                                   and exists (select message_time from message where message.message_id = messaging.message_id 
                                           and(message_time between(current_date - interval '1' year) and current_date +
                                                   interval '1' day )))  )
                        or
                        exists(select user_id from comments where comments.commentor_id = users.user_id
                                  and (comments.comment_time between(current_date - interval '1' year) and current_date
                        + interval '1' day ))"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print('Active users over the last year',row[0])
                print()
        elif choice == 5:
            uname=input("Enter the username : ")
            str_query="""select distinct A.tweet,A.post_time,A.user_id,case when true then 'promoted post' end as post_type
                                from post A,advertisements B, profile C where A.post_id=B.post_id and
                                exists (select target_audience(B.advert_id) = C.user_id)


                                Union


                                select distinct A.tweet,A.post_time,A.user_id,case when true then 'retweeted post' end as post_type
                                from post A, ret_table C where C.post_id=A.post_id
                                and C.user_id = any(select following_id from followings where user_id=any(select to_get_id('"""+uname+"""')))

                                UNION

                                select distinct A.tweet,A.post_time,A.user_id,case when true then 'not retweeted post' end as post_type
                                from post A, followings B where
                                 A.user_id = any(select following_id from followings where user_id=any(select to_get_id('"""+uname+"""')))
                                order by post_time desc;"""
            cur.execute(str_query)
            rows=cur.fetchall()
            c=1
            for row in rows:
                print("Tweet #",c,": ",row[0],"\n","date & time:",row[1]," user id:",row[2]," case:",row[3])
                print()
                c = c+1
        elif choice == 6:
            uname=input('Enter the username : ')
            str_query="""with main as(
                                select unnest(regexp_matches(tweet,'@([A-Za-z0-9_]+)','g')) as u_name,post_id from post
                        )

                        select C.username,A.tweet from post A,profile B,profile C,main D where B.username='"""+uname+"""' and B.username=D.u_name
                        and A.post_id=D.post_id and A.user_id=C.user_id;
                        """
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print("username : ",row[0],"\n","Tweet :",row[1])
                print()
        elif choice == 7:
            str_query="""with main as (
                        select count(message_id) as mess_count , extract(month from message_time) as month from 
                                                 messaging natural join message
                                                 group by month
                                                 order by count(message_id) desc
                                )
                        select month_name,mess_count from main A,months B where B.month_id=A.month order by mess_count DESC"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[1],"messages in ",row[0])
                print()
        elif choice == 8:
            str_query="""with main as(
                            select count(message_id) , extract(month from message_time) as month , profile.country from 
                                                        profile join messaging on messaging.sender_id = profile.user_id natural join message
                                                        group by month,country
                                                        order by count(message_id) desc
                            )

                            select A.count,B.month_name,A.country from main A,months B where A.month=B.month_id
                            order by count DESC;"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[0],"messages in ",row[1],"from ",row[2])
                print()
        elif choice == 9:
            str_query="""select count(user_id) ,extract(year from age(current_date,date_of_birth))
                         as age from users natural join profile 
                         group by  extract(year from age(current_date,date_of_birth))
                         order by count(user_id) desc

                         """
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[0],"users of age",int(row[1]))
                print()
        elif choice == 10:
            str_query="""select count(user_id) ,2019 - extract(year from date_of_birth) as age,
                         country from users natural join profile 
                         group by extract(year from date_of_birth),
                         country order by count(user_id) desc"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[0],"users of age ",int(row[1]),"and from ",row[2])
                print()
        elif choice == 11:
            str_query="""select count(user_id) ,extract(year from date_of_join),
                         country from users natural join profile 
                         group by extract(year from date_of_join),country
                         order by count(user_id) desc
"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[0],"users with date of join ",int(row[1]),"from ",row[2])
                print()
        elif choice == 12:
            str_query="""select count(A.user_id),country from verified A,profile B where 
                        A.user_id=B.user_id and A.is_verified=true
                        group by B.country order by count(A.user_id)DESC;"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print(row[0],"verified users from",row[1])
                print()
                
        elif choice == 13:
            uname=input('Enter the username : ')
            str_query="""with main as(
                        select following_id from followings where user_id=any(select to_get_id('"""+uname+"""'))
                                                except
                                                select user_id from post where  user_id=any(select following_id from
                                                                    followings where user_id=any(select to_get_id('"""+uname+"""')))
                                                group by user_id
                        )
                        select B.username from main A,profile B where A.following_id=B.user_id;
"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print("User",row[0],"haven't posted yet")
                print()
        elif choice == 14:
            uname=input('Enter the user name : ')
            str_query="""with main as(
                        select A.following_id from followings A where A.user_id=any(select to_get_id('"""+uname+"""'))
                                                 and exists (select user_id from followings where following_id=A.user_id
                                                 and user_id=A.following_id)
                        )

                        select A.username from profile A,main B where A.user_id=B.following_id
"""
            cur.execute(str_query)
            rows=cur.fetchall()
            for row in rows:
                print("User",row[0],"follows back you")
                print()
        elif choice == 15:
            exit('THanks')
        elif choice == 987:                           # just for test                                                     
            cur.execute("select username from profile")
            rows=cur.fetchall()
            for row in rows:
                print(row[0])
        else:
            print('Invaild!!!')
except:
    print ("I am unable to connect to the database")
