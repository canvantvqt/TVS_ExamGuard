"""ExamGuard AI H15: H14 trajectory + independent before/after seat ROI appearance audit.
Review only. No person identity or confirmed seat vacancy. Python 3.10 / OpenCV 4.8.
"""
import argparse,csv,json
from pathlib import Path
import cv2
import numpy as np

def read_frames(path,times):
    cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened() or fps<=0:raise ValueError('Cannot open video/FPS')
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));w=int(cap.get(3));h=int(cap.get(4))
    frames={}
    for t in times:
        idx=int(round(t*fps))
        if idx<0 or idx>=n:continue
        cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,frame=cap.read()
        if ok:frames[t]=frame
    cap.release();return frames,fps,n,w,h

def patch(frame,seat,rx,ry):
    x,y=int(seat['x']),int(seat['y']);h,w=frame.shape[:2]
    x1=max(0,x-rx);x2=min(w,x+rx);y1=max(0,y-ry);y2=min(h,y+ry)
    return frame[y1:y2,x1:x2],(x1,y1,x2,y2)

def feature(frame,seat,rx,ry):
    roi,_=patch(frame,seat,rx,ry)
    if roi.size==0:return None
    gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    gray=cv2.GaussianBlur(gray,(5,5),0)
    edges=cv2.Canny(gray,60,130)
    return gray, float(np.mean(edges>0)), float(np.mean(gray))

def main():
    p=argparse.ArgumentParser(description='H15: cross-check H14 trajectories against independent ROI changes')
    p.add_argument('--video',required=True);p.add_argument('--seats',required=True)
    p.add_argument('--h14-events',required=True);p.add_argument('--out',required=True)
    p.add_argument('--inspect-seats',default='G06,G07,G10,G14,G15')
    p.add_argument('--baseline-time',type=float,default=3.25)
    p.add_argument('--post-offsets',default='0.4,0.8,1.2',help='Seconds after each H14 event')
    p.add_argument('--radius-x',type=int,default=45);p.add_argument('--radius-y',type=int,default=55)
    p.add_argument('--gt-start',type=float,default=4.05,help='Report only, NOT used to decide events')
    a=p.parse_args()
    out=Path(a.out)
    if out.exists():p.error('Output folder exists: choose a new run folder')
    for path in [a.video,a.seats,a.h14_events]:
        if not Path(path).is_file():p.error('Missing file: '+path)
    if a.radius_x<5 or a.radius_y<5 or a.baseline_time<0:p.error('Invalid ROI/baseline')
    try:offsets=[float(x) for x in a.post_offsets.split(',')]
    except ValueError:p.error('Invalid post-offsets')
    if not offsets or any(x<=0 for x in offsets):p.error('Post offsets must be positive')
    with open(a.seats,encoding='utf-8-sig') as f:meta=json.load(f)
    seats={s['seat_id']:s for s in meta['seats']}
    ids=[x.strip() for x in a.inspect_seats.split(',') if x.strip()]
    if not ids or any(x not in seats for x in ids):p.error('Invalid seat ID')
    with open(a.h14_events,newline='',encoding='utf-8-sig') as f:events=list(csv.DictReader(f))
    selected=[e for e in events if e['seat_id'] in ids]
    for e in selected:
        if 'time_s' not in e or 'seat_id' not in e:p.error('Invalid H14 event CSV')
    times={a.baseline_time}
    for e in selected:
        t=float(e['time_s']);times.add(t)
        for d in offsets:times.add(round(t+d,5))
    frames,fps,n,w,h=read_frames(a.video,sorted(times))
    if (w,h)!=(meta.get('frame_width'),meta.get('frame_height')):p.error('Seat map dimensions mismatch')
    if a.baseline_time not in frames:p.error('Baseline outside video')
    out.mkdir(parents=True);(out/'evidence').mkdir()
    rows=[]
    for i,e in enumerate(selected):
        sid=e['seat_id'];t=float(e['time_s']);base=feature(frames[a.baseline_time],seats[sid],a.radius_x,a.radius_y)
        measurements=[]
        for offset in offsets:
            post_t=round(t+offset,5)
            if post_t not in frames:continue
            after=feature(frames[post_t],seats[sid],a.radius_x,a.radius_y)
            if base is None or after is None:continue
            # All scores are appearance-change proxies, NOT vacancy probabilities.
            difference=float(np.mean(cv2.absdiff(base[0],after[0]))/255.0)
            edge_change=abs(after[1]-base[1]);brightness_change=abs(after[2]-base[2])/255.0
            measurements.append((post_t,difference,edge_change,brightness_change))
        if not measurements:label='INSUFFICIENT_POST_VIDEO'
        elif len(measurements)<2:label='INSUFFICIENT_TEMPORAL_SAMPLES'
        else:label='TRAJECTORY_WITH_APPEARANCE_CHANGE_REVIEW' if np.median([v[1] for v in measurements])>=0.10 else 'TRAJECTORY_WITH_WEAK_APPEARANCE_CHANGE_REVIEW'
        # Explicitly avoid 'seat empty' and 'returned' assertions.
        for post_t,diff,edge,bright in measurements:
            rows.append([sid,round(t,3),round(post_t,3),e['event_type'],e.get('outward_fraction',''),
                         round(diff,4),round(edge,4),round(bright,4),label])
        frame=frames.get(t)
        if frame is not None:
            vis=frame.copy();_,(x1,y1,x2,y2)=patch(frame,seats[sid],a.radius_x,a.radius_y)
            cv2.rectangle(vis,(x1,y1),(x2,y2),(0,255,255),2)
            cv2.putText(vis,f'H15 {sid} {t:.3f}s REVIEW ONLY',(12,35),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),2)
            cv2.imwrite(str(out/'evidence'/f'{i:02d}_{sid}_{int(t*1000)}.jpg'),vis)
        print(sid,f'{t:.3f}s',label,'samples='+str(len(measurements)),
              'median_absdiff='+ (f'{np.median([v[1] for v in measurements]):.3f}' if measurements else 'NA'))
    with (out/'H15_event_audit.csv').open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.writer(f);wr.writerow(['seat_id','h14_event_time_s','post_time_s','h14_event_type','h14_outward_fraction',
                    'roi_mean_absdiff_0to1','roi_edge_density_abs_change','roi_brightness_abs_change_0to1','review_label']);wr.writerows(rows)
    summary=['ExamGuard AI H15: independent seat ROI appearance audit of H14 trajectory events',
             'Video: '+a.video,'H14 events: '+a.h14_events,'Seat map: '+a.seats,
             f'FPS={fps:.3f}; frames={n}; baseline={a.baseline_time:.3f}s; post offsets={offsets}',
             f'Inspected={ids}; H14 events inspected={len(selected)}; measurement rows={len(rows)}',
             f'Manual G06 reference={a.gt_start:.3f}s (report only, NOT used by classifier)',
             'ROI absolute differences compare appearance to a pre-event baseline. They do NOT measure seat occupancy.',
             'A seated student, a passerby, shadows, video-generation artifacts or camera effects can all change the ROI.',
             'H14 tracked texture, not a student identity. H15 does not link a moving person to an original seat.',
             'NO confirmed vacancy, return, person identity, cheating, accuracy or real-time capability.',
             'Do not treat the baseline-time as ground truth or use a post-event change as proof of a vacant seat.']
    (out/'H15_summary.txt').write_text('\n'.join(summary)+'\n',encoding='utf-8')
    print('DONE',len(selected),'H14 events;',len(rows),'ROI comparisons');print('Output:',out)
if __name__=='__main__':main()
