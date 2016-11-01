import asyncio
import pymysql.cursors
import re
import time

from cloudbot import hook
import cloudbot

'''plugin om punten te tellen van de verschillende andere bots op Scoutlink'''

# opbouw: naarbot [regex met tekst winnaar,locatie nick, locatie punten, als geen aantalpunten wat dan aan punten?]
# henkhuppelschoten krijgt 1 punt voor het antwoord :  neerstortpiloot.

bots = {
    #'222EA':[r'^([A-Za-z0-9_-]){2,31}\w\s(Jouw score is)\s([0-9]){0,1}\d)$',0,4],
    'Pimmetje':[r'^([A-Za-z0-9_-]){2,31}\w\s(krijgt)\s([0-9]){0,1}\d\s(punt voor het antwoord :)*',0,2],
    #'Burgemeester':[r'AAAAAAAAAAAAAA',0,None,10],
    #'Proton':[r'AAAAAAAAAAAAA^\w\s(pours)\w\s([A-Za-z0-9_-]){2,31}\w\s(a)*$',1],
    'Jeebeevee':[r'^([A-Za-z0-9_-]){2,31}\w\s(heeft)\s([0-9]){0,1}\d\s(punten gehaald.)$',0,2]
}
botnames = ['EA','Burgemeester','Jeebeevee','Pimmetje','Enigma','Duno']

###################################################
##		Database connecties		###
###################################################


def ConnectSQL(conn):
    #mysql
    #haal gegevens op uit config file
    db = conn.config.get('mysql', {})
    
    dbhost = db.get('dbhost', None)
    dbuser = db.get('dbuser', None)
    dbname = db.get('dbname', None)
    dbpass = db.get('dbpass', None)

    # Open database connection    
    msl = pymysql.connect(host=dbhost,
                             user=dbuser,
                             password=dbpass,
                             db=dbname,
                             unix_socket="/var/run/mysqld/mysqld.sock")
    #msl = MySQLdb.connect(dbhost,dbuser,dbpass,dbname)
    #db cursor
    #cur = msl.cursor()
    return msl


def InputSQL(sql, conn):
    #mysql
    # Open database connection
    msl = ConnectSQL(conn)
    #query uitvoeren
    try:
        with msl.cursor() as cur:
            cur.execute(sql)
            msl.commit()
    finally:
        if msl:
            msl.close()


def OutputSQL(sql, conn):
    #mysql
    # Open database connection
    msl = ConnectSQL(conn)
    #msl.cursor()
    #query uitvoeren
    result = ''
    try:
        with msl.cursor() as cur: 
            cur.execute(sql)
            result = cur.fetchone()
            return result
    finally:
        if msl:
            msl.close()
    return

###################################################
##	User gegevens ontvangen			###
###################################################

#ctcp terug met deelnemersnummer of mailadres
@asyncio.coroutine
@hook.irc_raw('*')
def ctcp_user_info(event, irc_raw, nick='', conn=None, bot=None):
  if event.irc_ctcp_text is not None:
    ctcp_msg = event.irc_ctcp_text.split(' ')
    #deelnemersnnummer toevoegen
    if ctcp_msg[0] == 'NUMBERREPLY':
        print(ctcp_msg)
        if ctcp_msg[1] == '':
            dlnummer = '9995'	
        else:
            dlnummer =  ctcp_msg[1]
            if dlnummer == '' or dlnummer == None:
               dlnummer = '9995'

        sql = "UPDATE users SET DLnummer='%s' WHERE username='%s'" % (dlnummer, nick)
        InputSQL(sql, bot)
        return

    #mailadres toevoegen
    if ctcp_msg[0] == 'MAILREPLY':
        dlmail = ctcp_msg[1]
        sql = "UPDATE users SET email='%s' WHERE username='%s'" % (dlmail, nick)
        InputSQL(sql, bot)
        return

def usercheck(nick, conn=None, bot=None):
    conn.send('WHOIS '+ nick)

@asyncio.coroutine
@hook.irc_raw('311')
def userChecker(irc_paramlist, irc_raw, conn=None, bot=None):

    nickname = irc_paramlist[1]
    hostname = irc_paramlist[3]
    #print(nickname+' :: '+ hostname)
    sql = "SELECT id FROM users WHERE username = '%s' AND hostname = '%s' LIMIT 1" % (nickname, hostname)
    nick_id = OutputSQL(sql, bot)
    #print(nickname+' :: '+ hostname +' + '+ str(nick_id))
    if nick_id is not '' and nick_id is not None:
        print("ID: "+ str(nick_id) +" | Joiner al bekend (exit)")
        return
    else:
        conn.ctcp(nickname,'\x01number\x01','')
        conn.ctcp(nickname,'\x01mail\x01','')

        sql = "INSERT INTO users (username, DLnummer, hostname, raw) VALUES ('%s' , '%d' , '%s' , '%s' )" % (nickname, 9991,hostname, irc_raw)
        InputSQL(sql, bot)

##################################
##	Punten verwerken			##
##################################
		
@asyncio.coroutine
@hook.irc_raw('PRIVMSG')
def regex_points(irc_paramlist, nick='', irc_raw='', bot=None):
    # tekst van bots?
    if any(nick in s for s in botnames):
        #raw message opbouw
        # :Jeebeevee!~Jeebeevee@ircop.scoutlink.net PRIVMSG #test :.ptest
        complete = irc_raw[1:].split(':',1) #Parse the message into useful data              
        info = complete[0].split(' ') #all sender info
        msgpart = complete[1] # message
        hostname = info[0].split('@')
		
        #hackje voor pimmetje
        msgpart = msgpart.lstrip()
        #bericht = msgpart.split(' ',1)

        #hoort de tekst bij de bot? en geeft deze tekst de punten?
        p = re.compile(r'^([A-Za-z0-9_-]){2,31}\w\s(krijgt 1 punt voor het antwoord)\w*')
        match = p.match(msgpart)
        #print match
        if match:
        #if bericht[1] == 'krijgt 1 punt voor het antwoord*':
            #print 2
       	    #haal de nick van de speler en het aantal punten uit de tekst
            words = msgpart.split(' ')
            give_nick = words[bots[nick][1]]
            #points = words[bots[nick][2]]
            points = 1
            usercheck(give_nick, conn, bot);
            time.sleep(2)
            GetPoints(nick, give_nick, int(points), bot)
  

# ontvangen punten via CTCP
# /CTCP Douwe POINTS $NICKNAME $POINTS
@asyncio.coroutine
@hook.irc_raw('*')
def ctcp_points(event, irc_raw, nick='', conn=None, bot=None):
  if event.irc_ctcp_text is not None:
    ctcp_msg = event.irc_ctcp_text.split(' ')
    if ctcp_msg[0] == 'POINTS':
        #Komt de CTCP van een van de bekende bots?
        if  any(nick in s for s in botnames):

            give_nick = ctcp_msg[1]
            points = ctcp_msg[2]

            usercheck(give_nick, conn, bot);
            time.sleep(2)
            GetPoints(nick, give_nick, int(points), bot)



# ontvangen punten via NOTICE
# /NOTICE Douwe $NICKNAME $POINTS
@asyncio.coroutine
@hook.irc_raw('NOTICE')
def notice_points(irc_raw, nick='', conn=None, bot=None):
    #Komt de NOTICE van een van de bekende bots?
    if any(nick in s for s in botnames):

        message = irc_raw.split(':')[2]
        give_nick = message.split(' ')[0]
        points = message.split(' ')[1]
        #print("{} :: {} - {}".format(message, give_nick, points))
        usercheck(give_nick, conn, bot);
        time.sleep(2)
        GetPoints(nick, give_nick, int(points), bot)

# verwerk de pinten die gegeven zijn.
def GetPoints(nick, give_nick, points, bot=None):

    sql = "SELECT id FROM users WHERE username = '%s' LIMIT 1" % give_nick
    nick_id = OutputSQL(sql, bot)[0]
    #if nick_id == '' or nick_id == None:
    #nick_id = usercheck(give_nick, conn, bot);
    unixtime = int(time.time())

    # hackje voor EA. om alleen de punten te registreren die de laatste 10 vragen (minuten) zijn gehaald
    triviabot = 'EA'
    if nick == triviabot:
        max_time = unixtime - (11*60)
        sql = "SELECT points FROM points WHERE user_id = '%d' AND bot = '%s' AND time <= '%d' AND time >= '%d' ORDER BY time DESC LIMIT 1" % (nick_id, triviabot, unixtime, max_time)
        time.sleep(2)
        old_input = OutputSQL(sql, bot)
        print (old_input)
        if old_input:
            if old_input[0] != '': 
                sql = "UPDATE points SET points = '%d', time = '%d' WHERE user_id = '%d' AND bot = '%s' AND time <= '%d' AND time >= '%d'" % (points, unixtime, nick_id, triviabot, unixtime, max_time)
                InputSQL(sql, bot)
                print('existing: {} points from bot: {} to user: {} '.format(points, nick, give_nick))
                return
    
    #print("{}: {}, {}, {}, {}".format(nick_id, nick, points, unixtime, give_nick))
    sql = "INSERT INTO points (user_id, bot, points, time, username) VALUES ( '%d' , '%s' , '%d' , '%d' , '%s')" % (nick_id, nick, points, unixtime, give_nick)
    InputSQL(sql, bot)
    print('new: {} points from bot: {} to user: {} '.format(points, nick, give_nick))


## END of SLNL_points ##
