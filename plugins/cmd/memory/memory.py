from plugins.bases.cmd import Cmd_Base
import subprocess

def init_data():
    command="free"
    process=subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE)
    stdout_list=process.communicate()[0].split('\n')
    for line in stdout_list:
        data=line.split()
        try:
            if data[0]=="Mem:":
                total=data[1]
                used=data[2]
                free=data[3]
                shared=data[4]
                buffers=data[5]
                cached=data[6]
                realfree=int(free)+int(cached)
                realused=int(used)-int(buffers)
        except IndexError:
            continue

    return(total,realused,realfree,shared,buffers,cached)

class memory(Cmd_Base):
	def run(self, *args, **kwargs):
		total,used,free,_,_,_ = init_data()

		return (True, [total,used,free])