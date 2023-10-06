import tkinter as t
import tkinter.ttk


import mysql.connector as mysql
import os, sys, shutil
from win32com.client import Dispatch #########


sqldetails = []

def init_tables():
    try:
        curs.execute('create table tag_data ( data_id int primary key, data_link varchar(200) not null);')
        curs.execute('create table tag_group ( tag_name varchar(50) primary key, group_id int);')
        curs.execute('create table group_order ( group_id int primary key, group_name varchar(50), order_of_group int);')
    except:
        print("error: init_tables")
        
def initialization():
    global sqldetails
    
    if True:
        m = t.Tk()
        t.Label(m, text = 'username').grid(row = 0)
        t.Label(m, text = 'password').grid(row = 1)
        t.Label(m, text = 'database').grid(row = 2)
        t.Label(m, text = 'output dir').grid(row = 3)

        username_var=t.StringVar()
        password_var=t.StringVar()
        database_var = t.StringVar()
        output_dir_var = t.StringVar()
        
        u = t.Entry(m,textvariable=database_var)
        p = t.Entry(m,textvariable=password_var)
        d = t.Entry(m,textvariable=username_var)
        o = t.Entry(m,textvariable=output_dir_var)
        
        u.grid(row=0,column=1)
        p.grid(row=1,column=1)
        d.grid(row=2, column = 1)
        o.grid(row=3, column = 1)
       
        def submit_sql_details():
            global sqldetails
            
            sqldetails.append( database_var.get())
            sqldetails.append( password_var.get() )
            sqldetails.append( username_var.get())
            sqldetails.append( output_dir_var.get())
            #print(sqldetails)
            m.destroy()
            
        bt=t.Button(m,text='Submit',command=submit_sql_details)
        bt.grid(row=4)
        m.mainloop()
        
check = 0

try:
    with open('credentials.txt', 'r') as f:
        sqldetails = eval( f.readlines()[0] )
        if len(sqldetails) == 4:
            check = 1
    if check == 0:
        initialization()
        with open('credentials.txt', 'w') as f:
            f.write( str(sqldetails))
except:
    if check == 0:
        initialization()
        with open('credentials.txt', 'w') as f:
            f.write( str(sqldetails))

   
print("Disclaimer: win32com.client and mysql must be installed")

con = mysql.connect(host = 'localhost', user=sqldetails[0], passwd = sqldetails[1], database = sqldetails[2]) 
curs = con.cursor()
parent_dir = sqldetails[3]

try:
    init_tables()
except:
    pass

Tags=[] #very important lists
Groups=[]
Links=[]

m=t.Tk()

'''--------------------------------------------------------------------------------------------'''    
def init_lists():
    global Tags, Groups, Links
    curs.execute('select data_link from tag_data;')    
    data = curs.fetchall()
    Links = []
    for i in data:
        Links.append(i[0])
    
    curs.execute('select tag_name from tag_group;')
    data = curs.fetchall()
    Tags = []
    for i in data:
        Tags.append(i[0])
    
    curs.execute('select group_name from group_order;')
    data = curs.fetchall()
    Groups = [] 
    for i in data:
        Groups.append(i[0])
        
def createShortcut(path, target='', wDir='', icon=''):    
    ext = path[-3:]
    if ext == 'url':
        shortcut = file(path, 'w')
        shortcut.write('[InternetShortcut]\n')
        shortcut.write('URL=%s' % target)
        shortcut.close()
    else:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        if icon == '':
            pass
        else:
            shortcut.IconLocation = icon
        shortcut.save()
        

    
    
def clear():
    try:
        curs.execute('drop table tag_data;')
        curs.execute('drop table tag_group;')
        curs.execute('drop table group_order;')
    except:
        print("error: clear")
        
'''--------------------------------------------------------------------------------------------'''
        
#create new tag: add column in tag_data and row in tag_group, accepts tag_name(req) and group_id(optional)
def create_tag(tag_name):   
    try:
        curs.execute('insert into tag_group(tag_name) values (\'{0}\');'.format(tag_name))
        con.commit()
        curs.execute('alter table tag_data add {0} int;'.format(tag_name))
        con.commit()
    except:
        print("error: create_tag")
        
#deletes tag column from tag_data and tag row from tag_group    
def delete_tag(tag_name):
    try:
        curs.execute('delete from tag_group where tag_name = \'{0}\' ;'.format(tag_name))
        curs.execute('alter table tag_data drop column {0};'.format(tag_name))
    except:
        print("error: delete_tag")

def add_tag_to_group(tag_name, group_name):
    try:
        curs.execute('select group_id from group_order where group_name = \'{0}\';'.format(group_name))
        group_id = curs.fetchall()[0][0]
        
        curs.execute('update tag_group set group_id = {0} where tag_name = \'{1}\';'.format(group_id, tag_name))
        con.commit()
    except:
        print("error: add_tag_to_group")

def remove_tag_from_group(tag_name):
    try:
        curs.execute('update tag_group set group_id = null where tag_name = \'{0}\';'.format(tag_name))
        con.commit()
    except:
        print('error: remove_tag_from_group')


'''--------------------------------------------------------------------------------------------'''        
#generates next natural number id for data
def generate_data_id():
    current_max_s = 'select max(data_id) from tag_data;'
    curs.execute(current_max_s)
    current_max = curs.fetchall()[0][0]
    if current_max == None:
        data_id = 1
    else:
        data_id = current_max + 1
    return data_id
    
#adds data_id and data_link to tag_data    
def add_data(data_link_notraw):
    
    data_link = data_link_notraw.replace("\\", "/")
    data_id = generate_data_id()
    
    try:
        curs.execute('insert into tag_data(data_id, data_link) values ({0}, \'{1}\');'.format(data_id, data_link))
        con.commit()
    except:
        print("add_data: Invalid path for data")
    
#removes data_id and data_link from tag_data
def delete_data(data_link):
    try:
        curs.execute('delete from tag_data where data_link = \'{0}\';'.format(data_link))
        con.commit()
    except:
        print("error: delete_data")
    
#changes path for the data
def change_data_link(old_data_link, new_data_link):
    try:
        curs.execute('update tag_data set data_link = \'{0}\' where data_link = \'{1}\';'.format(new_data_link, old_data_link))
        con.commit()
    except:
        print("error: change_data_link")
        
#add tags by changing 0 to 1 in their respective field        
def add_tag_to_data(tag_name, data_link):
    try:
        curs.execute('update tag_data set {0} = 1 where data_link = \'{1}\';'.format(tag_name, data_link))
        con.commit()
    except:
        print("error: add_tag_to_data")
        
#remove tags similarly
def remove_tag_from_data(tag_name, data_link):
    try:
        curs.execute('update tag_data set {0} = 0 where data_link = \'{1}\';'.format(tag_name, data_link))
        con.commit()
    except:
        print("error: remove_tag_from_data")
    
'''--------------------------------------------------------------------------------------------'''
def generate_group_id():
    current_max_s = 'select max(group_id) from group_order;'
    curs.execute(current_max_s)
    current_max = curs.fetchall()[0][0]
    if current_max == None:
        group_id = 1
    else:
        group_id = current_max + 1
    return group_id

def generate_default_order():
    current_max_s = 'select max(order_of_group) from group_order;'
    curs.execute(current_max_s)
    current_max = curs.fetchall()[0][0]
    if current_max == None:
        order_of_group = 1
    else:
        order_of_group = current_max + 1
    return order_of_group

def add_group(group_name):
    group_id = generate_group_id()
    order = generate_default_order()
    try:
        curs.execute('insert into group_order(group_id, group_name, order_of_group) values ({0}, \'{1}\', {2});'.format(group_id, group_name, order))
        con.commit()
    except:
        print("error: add_group")
        
def rename_group(old_group_name, new_group_name):
    try:
        curs.execute('update group_order set group_name = \'{0}\' where group_name = \'{1}\';'.format(new_group_name, old_group_name))
        con.commit()
    except:
        print("error: rename_group")

def delete_group(group_name):
    curs.execute('select group_id from group_order where group_name = \'{0}\';'.format(group_name))
    group_id = curs.fetchall()[0][0]
    
    curs.execute('delete from group_order where group_id = {0};'.format(group_id))
    curs.execute('update tag_group set group_id = null where group_id = {0}'.format(group_id))
    con.commit()
    
def swap_group_order(group_name_1, group_name_2):
    curs.execute('select group_id from group_order where group_name = \'{0}\';'.format(group_name_1))
    group_id_1 = curs.fetchall()[0][0]
    curs.execute('select group_id from group_order where group_name = \'{0}\';'.format(group_name_2))
    group_id_2 = curs.fetchall()[0][0]
    
    s = 'select order_of_group from group_order where group_id = {};'
    p = 'update group_order set order_of_group = {0} where group_id = {1};'
    try:
        curs.execute(s.format(group_id_1))
        order_1 = curs.fetchall()[0][0]
        curs.execute(s.format(group_id_2))
        order_2 = curs.fetchall()[0][0]
        
        curs.execute(p.format(order_2, group_id_1))        
        curs.execute(p.format(order_1, group_id_2))
        
        con.commit()
    except:
        print("swap_group_order: group_id invalid")
        
#------------------------------------------------------------------------------------------------------------------------------------#
       
output_dir = ""
filter_list = []

#set output directory
def init_out(op):
    
    global output_dir
    
    a = 0
    while a == 0:
        if op == 'perm':
            output_dir = os.path.join(parent_dir, input("Enter unique folder name: "))
            a = 1
        
        elif op == 'temp':
            output_dir_name = 'output'
            output_dir = os.path.join(parent_dir, output_dir_name)
            try:
                shutil.rmtree(output_dir)
            except:
                pass
            a = 1
    try:
        os.mkdir(output_dir)
    except:
        pass   
   
'''----------------------------------------------internal function below, not for use-------------------------------------------------'''

#recursively generate all folders according to tags grouped according to group_id in order_of_group
def gen(location, folder_list, depth=0, filter_list = []):

    if depth == 0:
        filter_list = []
    filter_prime = []
    cur_filter_list =[]
    
    #test for base case
    base = 0       
    try:
        
        folder_list[depth + 1]
        base = 0
    except:
        base = 1
        
    #if base case: create folders and shortcuts and then terminate,no need to call function again.
    if base == 1:
        for i in folder_list[depth]:
            #create the current folder and all shortcuts that match exclusively this folder
                      
            #create folder
            os.mkdir(location + i)
            
            #create list of all filters that data must satisfy 
            cur_filter_list = filter_list + [i]  
            
            #construct query to find data matching above
            root = 'select data_id, data_link from tag_data where'
            for j in range(len(cur_filter_list)):
                if j == len(cur_filter_list) - 1: 
                    root = root + " (" + cur_filter_list[j] + " = 1);"
                else: 
                    root = root + " (" + cur_filter_list[j] + " = 1) and"
            
            curs.execute(root)
            dat = curs.fetchall()
            
            for j in dat:
                createShortcut(location + i + '/' + j[1].split('/')[-1][:-5]  + '.lnk', target = j[1] ,wDir = j[1][:j[1].find(j[1].split('/')[-1])])
                #createShortcut(location + i + '/' + str(j[0]) + '.lnk', j[1], location + i + '/' + str(j[0]) + '.txt')
                '''
                try:
                    createShortcut(location + i + '/' + str(j[0]) + '.lnk', j[1], location + i + '/' + str(j[0]) + '.txt')
                except:
                    with open(location + i + '/' + str(j[0]) + '.txt', 'w') as f:
                        f.write(j[1])'''
            
    #create folders and shortcuts like above, only difference here being calling this function to continue recursion
    else:
        for i in folder_list[depth]:
            
            #create current folder
            os.mkdir(location + i)
            
            #list of all tags that must be satisfied
            cur_filter_list = filter_list + [i]
            
            #list of all tags that must be not satisfied
            filter_prime = []
            for j in range(depth+1, len(folder_list)):
                filter_prime.extend(folder_list[j])          
            
            #construct relevant query
            root = 'select data_id, data_link from tag_data where'
            for j in cur_filter_list:
                root = root + " (" + j + " = 1) and"
            for j in range(len(filter_prime)):
                if j == len(filter_prime) - 1: 
                    root = root + " (" + filter_prime[j] + " is null or 0);"
                else: 
                    root = root + " (" + filter_prime[j] + " is null or 0) and"
            
            curs.execute(root)
            dat = curs.fetchall()
            
            for j in dat:      
                createShortcut(location + i + '/' + j[1].split('/')[-1][:-5]  + '.lnk', target = j[1] ,wDir = j[1][:j[1].find(j[1].split('/')[-1])])
            
            #call function again with slightly modified data
            gen(location + i + '/', folder_list, depth + 1, cur_filter_list) 
            
'''-------------------------------------------------use these functions below-(also init_out() needs to be used)--------------------------------------------------------------'''

#initialize output directory. if op == perm output in a unqiue folder, if op == temp output in a common folder that cen get rewritten


#generates list that contain all tags grouped by group_id in order of order_of_group and calls gen function that does all the work
def create_folders(tablename ='tag_group', outp = output_dir, ):
    init_out('temp')                                                              ####################################
    
    curs.execute('select group_id from group_order order by order_of_group;')
    data = curs.fetchall()
    ordered_groups = []

    for i in data:
        ordered_groups.append(i[0])

    gen_folder_list = []
    for i in ordered_groups:
        curs.execute('select tag_name from {0} where group_id = {1};'.format(tablename,i))
        data = curs.fetchall()
        if len(data) == 0:
            continue
        data_2 = []
        for j in data:
                data_2.append(j[0])
        gen_folder_list.append(data_2)

    gen(output_dir + '/', gen_folder_list)

#filter folders by passing a filtered version of tag_group - tag_group_prime to above folder creating functions   
def filter_folder_with_tag(tag_list, outp = output_dir):
        
    tag_tuple = tuple(tag_list)
    try:
        curs.execute('drop table tag_group_prime;')
        con.commit()
    except:
        pass
    
    curs.execute('create table tag_group_prime ( tag_name varchar(50) primary key, group_id int);')
    if len(tag_tuple) == 1:
        curs.execute('insert into tag_group_prime select * from tag_group where tag_name = \'{0}\';'.format(tag_tuple[0]))
    else:
        curs.execute('insert into tag_group_prime select * from tag_group where tag_name in {0};'.format(tag_tuple))
    
    con.commit()    
    create_folders('tag_group_prime')


######################################################################################################################


#def open_new_window():   #pop-up function
    #newWindow=t.Toplevel(m)
    #newWindow.title='window name'
    
def manage_data_button():
    window2=t.Toplevel(m)
    def add_data_button():
        newWindow=t.Toplevel(window2)
        newWindow.title='Add Data'

        link_var=t.StringVar()
    
        t.Label(newWindow, text='link').grid(row=0)
    
        el=t.Entry(newWindow, textvariable=link_var)
    
        el.grid(row=0, column=1)
        
        def add_data_func():
            link=link_var.get()
           
            '''if link in Links:
                pass
            else:'''
            add_data(link)
            ##Links.append(link)
                
        bt=t.Button(newWindow,text='Add',command=add_data_func)
        bt.grid(row=2,column=0)
        
    ba=t.Button(window2,text='add data', width=45, command= add_data_button)  #add data button
    ba.pack()
    
    def delete_data_button():     # may have to change this to take link instead of dataid
        newWindow=t.Toplevel(window2)
        newWindow.title='Delete Data'

        link_var=t.StringVar()
        t.Label(newWindow, text='link').grid(row=0)
        ed=t.Entry(newWindow, textvariable=link_var)
        ed.grid(row=0, column=1)

        def delete_data_func():
            #global Links
            link=link_var.get()
            delete_data(link)
            '''for i in Links:
                if link==i:
                    Links.remove(link)'''

    #insert delete data function definition here
    #dataid=dataid_var
        bt=t.Button(newWindow, text='Delete' ,command=delete_data_func)
        bt.grid(row=2,column=0)
    bd=t.Button(window2,text='delete data', width=45, command= delete_data_button) #delete data button on mainscreen    
    bd.pack()
    def change_data_link_button():
        newWindow=t.Toplevel(window2)
        newWindow.title='change data link Data'

        NewLink_var=t.StringVar()
        OldLink_var=t.StringVar()
        NewLink=NewLink_var.get()
        OldLink=OldLink_var.get()
        t.Label(newWindow, text='new link').grid(row=0)
        t.Label(newWindow, text='old link').grid(row=1)
        eo=t.Entry(newWindow, textvariable=NewLink_var)
        en=t.Entry(newWindow, textvariable=OldLink_var)
        eo.grid(row=0, column=1)
        en.grid(row=1, column=1)
    #insert change data link function definition here
    #      OldLink=OldLink_var
    #      NewLink=NewLink_var
        def change_data_link_func():
            #global Links
            NewLink=NewLink_var.get()
            OldLink=OldLink_var.get()
            '''if OldLink not in Links:
                pass
            else:'''
            change_data_link(OldLink,NewLink)
            '''for i in range(0,len(Links)):
                if Links[i]==OldLink:
                   Links[i]==NewLink'''
        
        bt=t.Button(newWindow, text='Change Link', command=change_data_link_func)
        bt.grid(row=2,column=0)   
    bc=t.Button(window2,text='change data link', width=45, command= change_data_link_button) #change data link button on mainscreen    
    bc.pack()


    def view_links_button():
        global Links
        init_lists()
        
        newWindow=t.Toplevel(window2)
        for i in range(0,len(Links)):
            mytext = t.StringVar()
            mytext.set(Links[i])
            
            t.Entry(newWindow, bd = 0, state="readonly",  textvariable=mytext).grid(ipadx = 300) #######
            
            
    bvl=t.Button(window2, text='view links',width=45, command=view_links_button)
    bvl.pack()

    
bmd=t.Button(m,text='Manage data', width=25, command=manage_data_button)
bmd.pack()

def manage_tags_button():
    window2=t.Toplevel(m)
    def create_tag_button():
        newWindow=t.Toplevel(window2)

        newtag_var=t.StringVar()
        t.Label(newWindow, text='Tag Name').grid(row=0)
        et=t.Entry(newWindow, textvariable=newtag_var)
        et.grid(row=0, column=1)
        #insert new function which appends tag to tags[] and also contains create_tag function
        def create_tag_func():
            #global Tags
            tag=newtag_var.get()
            '''if tag in Tags:
                pass
            else:'''
            create_tag(tag)
            #Tags.append(tag)
        
        bt=t.Button(newWindow, text='Create tag', command=create_tag_func)
        bt.grid(row=2, column=0)
    bct=t.Button(window2,text='create tag', width=45, command= create_tag_button)
    bct.pack()
    def delete_tag_button():
        newWindow=t.Toplevel(window2)

        deltag_var=t.StringVar()
        t.Label(newWindow, text='Delete tag').grid(row=0)
        edt=t.Entry(newWindow, textvariable=deltag_var)
        edt.grid(row=0, column=1)
        #insert new function which removes deltag from tags[] and also contains delete_tag function
        def delete_tag_func():
            #global Tags
            tag=deltag_var.get()
            delete_tag(tag)
            '''for i in Tags:
                if i==tag:
                    Tags.remove(i)'''
        
        bt=t.Button(newWindow, text='Delete tag', command=delete_tag_func)
        bt.grid(row=2, column=0)
    bdt=t.Button(window2,text='delete tag', width=45, command= delete_tag_button)
    bdt.pack()
    def add_tag_to_group_button():
        newWindow=t.Toplevel(window2)
        tagtogroup_var=t.StringVar()
        groupName_var=t.StringVar()

        t.Label(newWindow,text='Tag name').grid(row=0)
        t.Label(newWindow,text='Group name').grid(row=1)
        etg=t.Entry(newWindow, textvariable=tagtogroup_var)
        eg=t.Entry(newWindow, textvariable=groupName_var)
        etg.grid(row=0,column=1)
        eg.grid(row=1,column=1)

        #insert new function which checks if tagtogroup is in tags[] and also contains add_tag_to_group function if tagtogroup not in tags[],button passes
        def add_tag_to_group_func():
            '''global Tags
            global Groups'''
            tag=tagtogroup_var.get()
            group=groupName_var.get()

            '''if tag in Tags and group in Groups:
                add_tag_to_group(tag,group)
            else:
                pass'''
                
            add_tag_to_group(tag,group)
            
        bt=t.Button(newWindow, text='add tag to group', command= add_tag_to_group_func)
        bt.grid(row=2, column=0)
    batg=t.Button(window2,text='add tag to group', width=45, command=add_tag_to_group_button)
    batg.pack()
    
    def remove_tag_from_group_button():
        newWindow=t.Toplevel(window2)
        deltagfromgroup_var=t.StringVar()

        t.Label(newWindow,text='Tag name').grid(row=0)
        edtg=t.Entry(newWindow, textvariable=deltagfromgroup_var)
        edtg.grid(row=0,column=1)

        #insert new function which checks if deltagfromgroup is in tags[] and also contains remove_tag_from_group function,else button passes
        def remove_tag_from_group_func():
            #global Tags
            
            tag=deltagfromgroup_var.get()
            '''if tag in Tags:
                remove_tag_from_group(tag)
            else:
                pass'''
            remove_tag_from_group(tag)
            
        bt=t.Button(newWindow, text='remove tag from group') # command=new remove tag from group function
        bt.grid(row=2,column=0)
    brtg=t.Button(window2,text='remove tag from group',width=45,command=remove_tag_from_group_button)
    brtg.pack()

    def add_tag_to_data_button():
        L=[]
        global Tags
        init_lists()
        #print(Tags)
        
        newWindow=t.Toplevel(window2)
        linktotag_var=t.StringVar()
        t.Label(newWindow,text='Link').grid(row=0)
        eatd=t.Entry(newWindow, textvariable=linktotag_var)
        eatd.grid(row=0,column=1)
        for i in range(0,len(Tags)):
            L.append( t.IntVar()) #############################################################################################################################################
        
        
        for i in range(0,len(Tags)):
            cb=t.Checkbutton(newWindow,text=Tags[i], variable=L[i],onvalue=1,offvalue=0).grid(row=i+1, column=0)
        def newfunc(): #this was a test to see if v holds 1s and 0s, to use add and remove tag from data function run for loop through v and for 0 use remove tag from data func and for 1s use add tag to data func
            global Tags
            global Links
            init_lists()
            
            link=linktotag_var.get()
            v=[]
            #print(L)
            
            
            if link not in Links:
                pass
            else:
                for i in range(0,len(L)):
                    v.append(L[i].get())
                    
                for i in range(0, len(L)):
                    if v[i]==1:
                        #print(Tags[i], link)
                        add_tag_to_data(Tags[i],link)
                    elif v[i]==0:
                        remove_tag_from_data(Tags[i],link)
                
            
                
        bt=t.Button(newWindow, text='add tag(s) to data',command=newfunc)
        bt.grid(row=len(Tags)+1, column=0)
    batd=t.Button(window2,text='tag data',width=45,command=add_tag_to_data_button)
    batd.pack()
bmt=t.Button(m,text='Manage tags', width=25, command=manage_tags_button)
bmt.pack()

def manage_groups_button():
    window2=t.Toplevel(m)
    def create_group_button():
        newWindow=t.Toplevel(window2)

        newgroup_var=t.StringVar()
        t.Label(newWindow, text='Group Name').grid(row=0)
        et=t.Entry(newWindow, textvariable=newgroup_var)
        et.grid(row=0, column=1)
        #insert new function which appends group to Groups[] and also contains create_group function
        def add_group_func():
            #global Groups
            group=newgroup_var.get()
            '''
            if group in Groups:
                pass
            else:
                add_group(group)
                Groups.append(group)'''
            add_group(group)  
            
        bt=t.Button(newWindow, text='Create gtoup', command=add_group_func)
        bt.grid(row=2, column=0)
    bcg=t.Button(window2,text='create group', width=45, command= create_group_button)
    bcg.pack() 
    
    def delete_group_button():
        newWindow=t.Toplevel(window2)

        delgroup_var=t.StringVar()
        t.Label(newWindow, text='Delete group').grid(row=0)
        edt=t.Entry(newWindow, textvariable=delgroup_var)
        edt.grid(row=0, column=1)
        #insert new function which removes delgroup from Groups[] and also contains delete_group function
        def delete_group_func():
            #global Groups
            group=delgroup_var.get()
            delete_group(group)
            '''
            for i in Groups:
                if i==group:
                    Groups.remove(i)'''
        
        bt=t.Button(newWindow, text='Delete group', command=delete_group_func)
        bt.grid(row=2, column=0)
    bdg=t.Button(window2,text='delete group', width=45, command= delete_group_button)
    bdg.pack()
    def rename_group_button():
        newWindow=t.Toplevel(window2)
        

        NewGroupName_var=t.StringVar()
        OldGroupName_var=t.StringVar()
        t.Label(newWindow, text='new group name').grid(row=0)
        t.Label(newWindow, text='old group name').grid(row=1)
        eo=t.Entry(newWindow, textvariable=NewGroupName_var)
        en=t.Entry(newWindow, textvariable=OldGroupName_var)
        eo.grid(row=0, column=1)
        en.grid(row=1, column=1)
    #insert rename group function definition here
    #      OldGroupName=OldGroupName_var
    #      NewGroupName=NewGroupName_var
        def rename_group_func():
            #global Groups
            NewGroupName=NewGroupName_var.get()
            OldGroupName=OldGroupName_var.get()
            '''
            if OldGroupName not in Groups:
                pass
            else:
                rename_group(OldGroupName,NewGroupName)
                for i in range(0,len(Groups)):
                    if Groups[i]==OldLink:
                        Groups[i]==NewLink'''
                        
            rename_group(OldGroupName,NewGroupName)
    
        bt=t.Button(newWindow, text='Rename group' ,command=rename_group_func)
        bt.grid(row=2,column=0)   
    bc=t.Button(window2,text='rename group', width=45, command= rename_group_button)     
    bc.pack()
    def group_priority_button():
        newWindow=t.Toplevel(window2)

        priority1_var=t.StringVar()
        priority2_var=t.StringVar()
        t.Label(newWindow, text='Group1').grid(row=0)
        t.Label(newWindow, text='Group2').grid(row=1)
        e1=t.Entry(newWindow, textvariable=priority1_var)
        e2=t.Entry(newWindow, textvariable=priority2_var)
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
       
    #insert rename group function definition here
        def swap_group_order_func():
            priority1=priority1_var.get()
            priority2=priority2_var.get()
            '''if priority1 or priority2 not in Groups:
                pass
            else:
                swap_group_order(priority1,priority2)'''
            
            print(priority1, priority2)
            
            swap_group_order(priority1,priority2)   
            t.Label(newWindow, text='Group1: '+priority1_var.get()).grid(row=3)
            t.Label(newWindow, text='Group2: '+priority2_var.get()).grid(row=4) #should be a part of the function of the button to run the function
    #      Priority1=Priority1_var
    #      Priority2=Priority2_var 
        bt=t.Button(newWindow, text='Set order', command = swap_group_order_func) #command=change group priority function
        bt.grid(row=6,column=0)   
    bgp=t.Button(window2,text='group order', width=45, command= group_priority_button)     
    bgp.pack()
    
    def view_groups_button():
        global Groups
        init_lists()
        
        newWindow=t.Toplevel(window2)
        for i in range(0,len(Groups)):
            t.Label(newWindow,text=Groups[i]).grid(row=i)
    bvg=t.Button(window2, text='view groups',width=45, command=view_groups_button)
    bvg.pack()


bmg=t.Button(m,text='Manage groups',width=25, command=manage_groups_button)
bmg.pack()

def filter_button():
    List_tag=[]
    window2=t.Toplevel(m)
    filtertag_var=t.StringVar()
    t.Label(window2, text='filter tag(s)').grid(row=0)
    t.Label(window2, text='enter in the form of python list i.e, [\'a\',\'b\',\'c\']').grid(row=1)
    e=t.Entry(window2, textvariable=filtertag_var)
    e.grid(row=0,column=1)
    def filter_folder_with_tag_func():
        List_tag=eval(filtertag_var.get())
        filter_folder_with_tag(List_tag)
        
    bt=t.Button(window2,text='filter',command=filter_folder_with_tag_func)
    bt.grid(row=2)
bf=t.Button(m,text='Filter',width=25,command=filter_button)
bf.pack()


def run_flowkey():
    create_folders()
br=t.Button(m,text='Run',width=25,fg='green',command=run_flowkey)
br.pack()
m.mainloop()
    
###############################################################################################################################################
     ###############################




