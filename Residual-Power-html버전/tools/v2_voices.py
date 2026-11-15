from pathlib import Path
import asyncio,edge_tts,subprocess
R=Path(__file__).resolve().parents[1];A=R/'assets/audio'
lines=[('voice-left','흔적은 지워도 남아.','ko-KR-SunHiNeural'),('voice-right','끝까지 밀어. 그 아래.','ko-KR-InJoonNeural'),('archive-L','05는 비어 있어. 명단부터 보내.','ko-KR-SunHiNeural'),('archive-R','키는 인계가 아니라 회수. 두 번 남기고 멈춰.','ko-KR-InJoonNeural'),('archive-final','이번에는 기억해.','ko-KR-SunHiNeural')]
async def make(row):
 name,text,voice=row
 await asyncio.wait_for(edge_tts.Communicate(text,voice,rate='-12%').save(str(A/(name+'.mp3'))),40)
 if name.startswith('archive'):
  subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(A/(name+'.mp3')),'-ar','22050','-ac','1',str(A/(name+'.wav'))],check=True)
 print(name,'created')
async def main():
 for i in range(0,len(lines),2):await asyncio.gather(*(make(x) for x in lines[i:i+2]))
asyncio.run(main())
