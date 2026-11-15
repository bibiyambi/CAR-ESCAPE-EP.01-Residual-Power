from pathlib import Path
import json, subprocess, wave
import numpy as np
from scipy import signal
from scipy.io import wavfile
R=Path(__file__).resolve().parents[1];A=R/'assets/audio';sr=22050;rng=np.random.default_rng(4104)
def wav(name,data):
    data=np.asarray(data);wavfile.write(A/(name+'.wav'),sr,(np.clip(data,-1,1)*32767).astype(np.int16))
def mono(name):
    out=A/(name+'-raw.wav');subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(A/(name+'.mp3')),'-ar',str(sr),'-ac','1',str(out)],check=True)
    _,v=wavfile.read(out);out.unlink();v=v.astype(float)/32768
    v=signal.sosfilt(signal.butter(2,[220,3300],btype='bandpass',fs=sr,output='sos'),v)
    v=v/(max(abs(v)) or 1)*.65
    return v
left,right=mono('voice-left'),mono('voice-right');duration=max(len(left),len(right))/sr+1.15;n=int(duration*sr)
stereo=np.zeros((n,2));start=int(.55*sr)
for channel,v in enumerate([left,right]):
    stereo[start:start+len(v),channel]+=v
    # Very quiet tape hiss and short room echo; words remain intelligible.
    offset=int(.045*sr);tail=min(len(v),n-start-offset)
    stereo[start+offset:start+offset+tail,channel]+=.065*v[:tail]
    stereo[:,channel]+=rng.normal(0,.0015,n)
fade=np.minimum(np.arange(n)/int(.1*sr),1)*np.minimum(np.arange(n)[::-1]/int(.1*sr),1)
wav('stereo-recording',stereo*fade[:,None])
peaks=[]
for c in range(2):peaks.append([round(float(np.max(np.abs(a))),4) for a in np.array_split(stereo[:,c],80)])
info={'duration':round(duration,4),'sampleRate':sr,'channels':2,'left':'흔적은 지워도 남아.','right':'끝까지 밀어. 그 아래.','voiceSource':'Korean synthetic dialogue / SunHi and InJoon; not a real person recording','waveform':peaks}
(A/'recording.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
# Original procedural environmental and mechanical game sound effects.
t=np.arange(sr*10)/sr;noise=rng.normal(0,1,len(t));rain=signal.sosfilt(signal.butter(2,1800,fs=sr,output='sos'),noise)
rain=rain/(max(abs(rain)) or 1)*.13
# Loop seam crossfade is handled by a low-amplitude sine envelope at both ends.
rain[:1000]*=np.linspace(0,1,1000);rain[-1000:]*=np.linspace(1,0,1000)
wav('rain-loop',np.column_stack((rain,np.roll(rain,137))))
def tone(name,dur,fn,amp=.2):
    t=np.arange(int(sr*dur))/sr;data=fn(t);env=np.minimum(t/.008,1)*np.minimum((dur-t)/.045,1);wav(name,data*env*amp)
tone('latch',.19,lambda t:np.sin(2*np.pi*(420-900*t)*t)*np.exp(-t*24)+rng.normal(0,.1,len(t)))
tone('collect',.5,lambda t:np.sin(2*np.pi*np.where(t<.18,523.25,659.25)*t)*np.exp(-t*5),.13)
tone('connect',.4,lambda t:np.sin(2*np.pi*np.where(t<.16,660,880)*t)*np.exp(-t*5),.12)
tone('unlock',.65,lambda t:(np.sin(2*np.pi*240*t)*np.exp(-t*14)+np.sin(2*np.pi*720*t)*np.exp(-((t-.22)/.08)**2)),.17)
tone('wrong',.26,lambda t:np.sin(2*np.pi*145*t)*np.exp(-t*11),.12)
tone('beep',.18,lambda t:np.sin(2*np.pi*1046*t),.05)
tone('motor',1.0,lambda t:(np.sin(2*np.pi*93*t)+.3*np.sin(2*np.pi*185*t))*.35,.14)
tone('motorFail',.35,lambda t:np.sin(2*np.pi*(130-160*t)*t),.12)
tone('paper',.42,lambda t:signal.sosfilt(signal.butter(1,2000,fs=sr,output='sos'),rng.normal(0,1,len(t)))*np.sin(np.pi*t/.42),.16)
tone('cloth',.4,lambda t:signal.sosfilt(signal.butter(1,700,fs=sr,output='sos'),rng.normal(0,1,len(t)))*np.sin(np.pi*t/.4),.2)
tone('wiper',.85,lambda t:signal.sosfilt(signal.butter(1,1000,fs=sr,output='sos'),rng.normal(0,1,len(t)))*np.sin(2*np.pi*t/.85)**2,.18)
print('Created real two-channel dialogue, rain loop and 11 mechanical effects',duration)
