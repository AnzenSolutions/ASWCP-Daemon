from plugins.bases.event_handler import EventHandler_Base
import subprocess

class sysexec(EventHandler_Base):
    @property
    def defaults(self):
        """
        Similar to system/acl plugin, we want to have some fine-grained control over what can be ran

        However, with the possibility of allow_shell = True, we force a restrictive policy by default.

        Also, by default, nothing is allowed to be executed.  Cool, huh?
        """
        return {
            'allow_shell' : "True",
            'cmdlist_white' : "date,time,ls",
            'cmdlist_black' : "",
            'cmdlist_force' : "black"
        }

    def init(self, *args, **kwargs):
        self.xmpp_conf = kwargs['conf']
        self.init_conf(".config", self.defaults)

        self.white = [x for x in self.plugin_conf.cmdlist_white.split(",")]
        self.black = [x for x in self.plugin_conf.cmdlist_black.split(",")]
        self.force = self.plugin_conf.cmdlist_force
        self.shell = self.plugin_conf.allow_shell

        return self

    def run(self, *args, **kwargs):
        # If no command was given, error out
        if args[0] == "":
            return "No command given to execute."
        
        try:
            cmd = "%s %s" % (args[0], args[1])
        except:
            cmd = args[0]
        
        result = ""
        
        print "> cmd:",cmd
        
        if self.force == "white" and cmd not in self.white:
            return "%s is not whitelisted." % (cmd)
        elif self.force == "back" and cmd in self.black:
            return "%s is blacklisted and will not be executed." % (cmd)
        
        try:
            # Allowing the shell should never be done unless you know what commands will be ran
            result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=self.shell)
        except OSError:
            pass
        except subprocess.CalledProcessError:
            pass

        return (True, "%s" % result.strip())
