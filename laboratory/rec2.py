import subprocess
import os
import time
import signal

#proc_args = ['arecord', '-D' , 'dmic_sv' , '-c2' , '-r' , '44100' , '-f' , 'S32_LE' , '-t' , 'wav' , '-V' , 'mono' , '-v' , 'subprocess1.wav']
proc_args = ['arecord', '--quiet', '-D' , 'plughw:1' , '-c2' , '-r' , '16000' , '-f' , 'S32_LE' , '-t' , 'wav' , '-V' , 'stereo' , 'subprocess1.wav']
rec_proc = subprocess.Popen(proc_args, shell=False, preexec_fn=os.setsid)
# print("startRecordingArecord()> rec_proc pid= " + str(rec_proc.pid))
# print("startRecordingArecord()> recording started")

time.sleep(3)
os.killpg(rec_proc.pid, signal.SIGTERM)
rec_proc.terminate()
rec_proc = None
print("stopRecordingArecord()> Recording stopped")