import time, sys, re
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from phold import *

MATTO = "10.25.160.219"

class MessageLogger:
    def __init__(self, file):
        self.file = file

    def log(self, msg):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, msg))
        self.file.flush()

    def close(self):
        self.file.close()

    
class DoyleBot(irc.IRCClient):
    nickname = "doylebot"

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))
        
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()

    def signedOn(self):
        self.join(self.factory.channel)

    def joined(self, channel):
        self.logger.log("[I have joined %s]" % channel)
        self.main_chan = channel
        #self.msg(channel, "anyone up for some poker?")

        self.inprocess = False
        self.begun = False

        self.g = None
        self.g_timer = None

        self.current_pl = None
        self.avail_actions = None

    def send_status(self):
        self.msg(channel, "%s is next to act" % self.current_pl)
        self.msg(channel, "Options: %s" % self.avail_options)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))


        ## priv message
        if channel == self.nickname:
            msg = "use the public channel to perform an action"
            self.msg(user, msg)
            return
        
        ## addressed
        if msg.startswith(self.nickname + ":"):
            msg = "%s: sup, this be botchan" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
                

        m_register = re.match(r'register$', msg)
        m_status = re.match(r'status$', msg)
        m_list = re.match(r'known players$', msg)
        m_start = re.match(r'start$', msg)
        m_join = re.match(r'join$', msg)
        m_steal = re.match(r'steal', msg)

        m_who = re.match(r'who$', msg)

        m_fold = re.match(r'fold$', msg)
        m_check = re.match(r'check$', msg)
        m_call = re.match(r'call$', msg)
        m_bet = re.match(r'bet (\d+)$', msg)
        m_raise = re.match(r'raise (\d+)$', msg)
        m_allin = re.match(r'all in$', msg)

        m_action = m_fold or m_check or m_call or m_bet or m_raise or m_allin


        if m_who and self.begun:
            self.msg(channel, "it is %s's turn" % self.current_pl.name)
            

        if m_action and self.begun and user == self.current_pl.name:
            if m_fold:
                self.current_pl, self.avail_actions = g.fold_pl(user)
                self.msg(channel, "%s has folded" % user)
            
            elif m_check:
                if Action.Check not in self.avail_actions:
                    self.msg(channel, "Call, Raise, or Fold")
                else:
                    self.current_pl = g.next_pl()
                
            elif m_call:
                if Action.Call not in self.avail_options:
                    self.msg(channel, "Check, Bet, or Fold")
                else:
                    allin, amt,self.current_pl,self.avail_actions =  self.g.call_pl(user)
                    if allin:
                        self.msg(channel, "%s is all-in for %s" % user,amt)
                    
            elif m_bet:
                if Action.Bet not in self.avail_options:
                    self.msg(channel, "Call, Raise, or Fold")
                else:
                    bet_amt = m_bet.group(1)
                    if bet_amt < self.g.minbet:
                        self.msg(channel, "Interpreting as minimum bet of %s" %self.g.minbet)
                
                    g.bet_pl(user, bet_amt)

            elif m_allin:
                action, amt, self.next_pl, self.avail_actions = self.g.allin_pl(user)
                self.msg(channel, "%s went all-in for %s" % user,amt)
             
            #maybe_end()
            self.send_status()

                
        if m_register:
            msg = register(str(user))
            self.msg(channel, msg)

        if m_status:
            if self.current_pl == "finished":
                self.msg(channel, "complete")
            else:
                msg = status(str(user))
                self.msg(channel, msg)

        if m_list:
            msg = known_pl
            self.msg(channel, msg)

        if m_start:
            if self.inprocess:
                msg = "There's one already in progress!"
            else:
                self.inprocess = True
                self.g = Game()
                self.g_timer = time.time()
                msg = "New game about to begin.  To join, type 'join'. You have 30 seconds"
                self.msg(channel, msg)
        
        if m_join and self.inprocess and not self.begun:
            if time.time() - self.g_timer > 30:
                self.g.add_pl(str(user))
                if len(self.g.plst) < 2:
                    self.inprocess = False
                    self.begun = False
                    self.msg(channel,"Only 1 player signed up.  Aborting.")

                else:
                    self.msg(channel, "Adding %s to the players list" % str(user))
                    self.msg(channel, "Beginning game with: %s"% str(self.g.plst))
                    
                    
                    cards = self.g.deal()
                    for (nm, hnd) in cards:
                        self.msg(nm, "Hand: %s" % hnd)
                        
                    self.current_pl = g.next_pl()
                    self.msg(channel, "%s is first to act" % self.current_pl.name)
                   
                    self.begun = True

                
            else:
                self.g.add_pl(str(user))
                msg = "Adding %s to the players list" % str(user)
                msg2 = "So far (this game): %s" % str(self.g.plst)
                self.msg(channel, msg)
                self.msg(channel, msg2)

        if m_steal and user in known_pl and m_steal.group(1) in known_pl:
            t = known_pl[user]
            v = known_pl[m_steal.group(1)]
            amt = int(m_steal.group(2))
            if v.amt < amt:
                msg = "%s is too poor for that" % m_steal.group(1)
                self.msg(channel, msg)
            else:
                t.amt += amt
                v.amt -= amt
                self.msg(channel, "well done, slick")
            

        def end_game():
            self.begun = False
            self.inprocess = False

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        
        if old_nick in known_pl:
            known_pl[old_nick].name = new_nick
        
        self.logger.log("%s changed nick to as %s" % (old_nick, new_nick))


class DoyleBotFactory(protocol.ClientFactory):
    protocol = DoyleBot

    def __init__(self, channel, logfile):
        self.channel = channel
        self.filename = logfile

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    if len(sys.argv) != 3 or argv[1] == "help":
        print "usage: doylebot <channel> <logfile>"
        sys.exit()

    log.startLogging(sys.stdout)
    f = DoyleBotFactory(sys.argv[1], sys.argv[2])
    reactor.connectTCP(MATTO, 6667, f)

    reactor.run()



        
