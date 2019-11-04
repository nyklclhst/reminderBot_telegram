import pymysql
import schedule
import telepot
import time
from datetime import datetime
from telepot.loop import MessageLoop

sts = 2
tdy = datetime.today().strftime('%A')

# Connection to mysql
def openCon():
    return pymysql.connect('localhost','<your mysql username>','<your mysql password>','tele_bot_data')

# Check date time
def get_date(chat_id):
    if chat_id == '<your admin chat id>':
        telegram_bot.sendMessage(chat_id,str(datetime.now()))
    else :
        telegram_bot.sendMessage(chat_id,str('Sorry, you cannot do this command!'))

# check user registered or no
def check_user(chat_id):
    db = openCon()
    cursor = db.cursor()
    sql = 'select id from users where tele_id=%s' % chat_id
    try:
        cursor.execute(sql)
        res = cursor.fetchone()
        if res != None:
            return True
        else:
            return False
    except pymysql.Error as e:
        print(e)
        return False
    db.close()

# Function /start command
def start(chat_id):
    db = openCon()
    cursor = db.cursor()
    sql = 'select f_name,l_name from users where tele_id=%s' % chat_id
    try:
        cursor.execute(sql)
        res = cursor.fetchone()
        if res != None:
            telegram_bot.sendMessage(chat_id, str('Welcome Back %s %s' % (res[0],res[1])))
        else:
            telegram_bot.sendMessage(chat_id,str('Hello, Welcome to Seculab Reminder Bot. Please do /regis to start.'))
    except pymysql.Error as e:
        print(e)
        telegram_bot.sendMessage(chat_id,str('Ooops... Something went wrong!'))
    db.close()

# Function /hi command
def hi(chat_id):
    if chat_id == '<your admin chat id>':
        telegram_bot.sendMessage (chat_id, str("Hi!"))
    else :
        telegram_bot.sendMessage (chat_id, str("You are not allowed to do this!"))

# Function /help command
def help(chat_id):
    h_cmd = ['/hi','/help','/regis','/myjadwal','/addjadwal','/minggu','/date']
    h_desc = ['Are you alive?','See this message','Register your id to our database',
        'To see all your jadwal','To adding new Jadwal','To see minggu','To get System Datetime']
    resp = ''
    if chat_id == '<your admin chat id>':
        for i in range(len(h_cmd)):
            resp += '%s - %s \n' % (h_cmd[i], h_desc[i])
    else :
        h_cmd.pop(0)
        h_desc.pop(0)
        h_cmd.pop(5)
        h_desc.pop(5)
        h_cmd.pop(6)
        h_desc.pop(6)
        for i in range(len(h_cmd)):
            resp += '%s - %s \n' % (h_cmd[i], h_desc[i])
    telegram_bot.sendMessage(chat_id,str(resp))

# Function /myjadwal command
def myjadwal(chat_id):
    db = openCon()
    cursor = db.cursor()
    lst = []
    resp = ''
    if check_user(chat_id):
        sql = ('select c.day, c.shift, c.status from users a left join '
            'jadwal b on (b.user_id = a.id) left join day c on (c.id = b.day_id) '
            'where a.tele_id = %s' % chat_id)
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            if res[0][0] != None:
                for row in res:
                    day = row[0]
                    shift = row[1]
                    status = row[2]
                    lst.append('%s(%d) - shift: %d' % (day,status,shift))
                for i in range(len(lst)):
                    resp += lst[i]+'\n'
            else:
                resp = ('Ooops... Looks like you haven\'t have any Jadwal. Please input '
                    'your jadwal with /addjadwal')
        except pymysql.Error as e:
            print(e)
            resp = 'Ooops... Something went wrong!'
    else:
        resp = 'Hello, Welcome to Seculab Reminder Bot. Please do /regis to start.'
    telegram_bot.sendMessage(chat_id,str(resp))
    db.close()

def regis(chat_id,fname,lname):
    db = openCon()
    cursor = db.cursor()
    sql = 'select id from users where tele_id=%s' % chat_id
    try:
        cursor.execute(sql)
        res = cursor.rowcount
        if res == 1:
            telegram_bot.sendMessage(chat_id,str('You have been registered!'))
        else :
            sql = "insert into users (f_name,l_name,tele_id) values ('%s','%s',%d)" % (fname,lname,chat_id)
            cursor.execute(sql)
            db.commit()
            telegram_bot.sendMessage(chat_id,str('Congratulation! You have registered!'))
    except pymysql.Error as e:
        print(e)
        telegram_bot.sendMessage(chat_id,str('Ooops... Something went wrong!'))
    db.close()

def sendDayId(chat_id):
    lst = []
    resp = ''
    db = openCon()
    cursor = db.cursor()
    sql = 'select id,day,shift,status from day'
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            lst.append('ID: %d. Hari: %s(%d). Shift: %d.' % (row[0],row[1],row[3],row[2]))
        for i in range(len(lst)):
            resp += lst[i]+'\n'
    except pymysql.Error as e:
        print(e)
        resp = 'Ooops... Something went wrong!'
    telegram_bot.sendMessage(chat_id,str('Here is the list ID for Day: \n\n'+resp))
    db.close()

def addJadwal(chat_id,day_id):
    db = openCon()
    cursor = db.cursor()
    sql = ('insert into jadwal (user_id, day_id) select a.id,b.id '
        'from users a left join day b on (b.id=%s) where a.tele_id = %s' % (day_id,chat_id))
    if check_user(chat_id):
        try:
            cursor.execute(sql)
            db.commit()
            telegram_bot.sendMessage(chat_id,str('Congratulation! You have added new jadwal!'))
        except pymysql.Error as e:
            print(e)
            telegram_bot.sendMessage(chat_id,str('Ooops... Something went wrong!'))
    else:
        resp = 'Hello, Welcome to Seculab Reminder Bot. Please do /regis to start.'
        telegram_bot.sendMessage(chat_id,str(resp))
    db.close()

def check_status(chat_id):
    if chat_id == '<your admin chat id>':
        telegram_bot.sendMessage(chat_id,str(sts))

def action(msg):
    chat_id = msg['chat']['id']
    cmd = msg['text'].split(' ')
    if cmd[0] == '/start':
        # Respond start command
        start(chat_id)
    if cmd[0] == '/hi':
        # Check server status
        hi(chat_id)
    if cmd[0] == '/help':
        # Respond help command
        help(chat_id)
    if cmd[0] == '/myjadwal':
        # Respond myjadwal command
        myjadwal(chat_id)
    if cmd[0] == '/regis':
        # Respond regis command
        fname = msg['chat']['first_name']
        try:
            lname = msg['chat']['last_name']
        except:
            lname = ''
        regis(chat_id,fname,lname)
    if cmd[0] == '/addjadwal':
        if len(cmd) < 2:
            sendDayId(chat_id)
            telegram_bot.sendMessage(chat_id,str('Usage with /addjadwal <day_id>'))
        else:
            addJadwal(chat_id,cmd[1])
    if cmd[0] == '/minggu':
        check_status(chat_id)
    if cmd[0] == '/date':
        get_date(chat_id)

def reminder(today=tdy,status=sts):
    usr_id = []
    usr_fname = []
    usr_lname = []
    shift = []
    db = openCon()
    cursor = db.cursor()
    sql = ('select b.tele_id,b.f_name,b.l_name,c.day,c.shift,c.status from jadwal ' 
        'a left join users b on (b.id=a.user_id) left join day c on (c.id=a.day_id)')
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row[3] == today and row[5] == status:
                usr_id.append(row[0])
                usr_fname.append(row[1])
                usr_lname.append(row[2])
                shift.append(row[4])
    except pymysql.Error as e:
        print(e)
    if len(usr_id) != 0:
        for i in range(len(usr_id)):
            msg = ('Hello %s %s, Your Jadwal for %s(%d) is:\n'
                'Shift : %d' % (usr_fname[i],usr_lname[i], today, status, shift[i]))
            telegram_bot.sendMessage(usr_id[i],str(msg))
    db.close()

def check_sts():
    global sts
    if sts == 2:
        sts = 1
    else:
        sts+=1

telegram_bot = telepot.Bot('<your telegram bot token>')
print(telegram_bot.getMe())
MessageLoop(telegram_bot, action).run_as_thread()
print('Up and Running....')
schedule.every().day.at("07:00").do(reminder)
schedule.every().monday.do(check_sts)
while 1:
    schedule.run_pending()
    time.sleep(10)
