from plugins.bases.cmd import Cmd_Base
from subprocess import check_output
from os.path import exists

class update(Cmd_Base):
    def run(self, *args, **kwargs):
        pkgman = {
            "/usr/bin/aptitude" : "-y safe-upgrade",
            "/usr/bin/yum" : "-y update",
            "/usr/bin/pacman" : "/usr/bin/echo \"Y\" | /usr/bin/pacman -Syu"
        }

        out = ""

        for prog,opts in pkgman.iteritems():
            if exists(prog):
                try:
                    if opts[0] != "/":
                        out = check_output([prog,opts])
                    else:
                        out = check_output(opts,shell=True)
                except:
                    pass
                    
                break
        return (True, out)

    @property
    def help(self):
        return ''' '''
