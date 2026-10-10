"""Polished CPU-friendly autonomous navigation dashboard.
Run from the project folder: py -3.11 visual_simulation_pro.py
Original simulation files are not modified.
"""
import math, random, time, heapq
from collections import deque
import pygame
from simulation.environment import Environment



def find_path(env, start, goal):
    """A* path planner that penalizes cells next to obstacles."""
    if start in env.obstacles or goal in env.obstacles:
        return None
    frontier = [(0.0, 0.0, start)]
    came_from = {start: None}
    costs = {start: 0.0}
    while frontier:
        _, cost_so_far, current = heapq.heappop(frontier)
        if current == goal:
            break
        if cost_so_far > costs.get(current, float("inf")):
            continue
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nxt = (current[0]+dx, current[1]+dy)
            if not (0 <= nxt[0] < GRID_W and 0 <= nxt[1] < GRID_H):
                continue
            if nxt in env.obstacles:
                continue
            # Clearance cost: nearby obstacles make a cell less attractive.
            near = sum((nxt[0]+ax, nxt[1]+ay) in env.obstacles
                       for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)))
            step_cost = 1.0 + near * 0.65
            new_cost = cost_so_far + step_cost
            if new_cost < costs.get(nxt, float("inf")):
                costs[nxt] = new_cost
                came_from[nxt] = current
                heuristic = abs(goal[0]-nxt[0]) + abs(goal[1]-nxt[1])
                heapq.heappush(frontier, (new_cost + heuristic, new_cost, nxt))
    if goal not in came_from:
        return None
    route = []
    cur = goal
    while cur is not None:
        route.append(cur)
        cur = came_from[cur]
    route.reverse()
    return route


pygame.init()
pygame.display.set_caption("AI Autonomous Navigation | PRO Dashboard 2.0")
W, H = 1440, 900
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
clock = pygame.time.Clock()

# Theme
BG=(5,15,32); PANEL=(8,28,53); PANEL2=(10,37,67); BORDER=(17,92,148)
WHITE=(225,241,255); MUTED=(139,175,204); CYAN=(0,210,245); BLUE=(39,125,255)
GREEN=(0,235,125); RED=(255,76,99); ORANGE=(255,151,42); BLOCK=(67,83,104)
GRID=(38,65,91); PURPLE=(167,105,255); YELLOW=(255,193,55)
font_cache={}
def font(size,bold=False):
    key=(size,bold)
    if key not in font_cache: font_cache[key]=pygame.font.SysFont('segoeui',size,bold=bold)
    return font_cache[key]
def txt(s,x,y,size=16,color=WHITE,bold=False):
    surf=font(size,bold).render(str(s),True,color); screen.blit(surf,(int(x),int(y))); return surf.get_rect(topleft=(x,y))
def panel(rect, color=PANEL, radius=14, border=BORDER):
    pygame.draw.rect(screen,color,rect,border_radius=radius)
    if border: pygame.draw.rect(screen,border,rect,width=1,border_radius=radius)
def line(points,color=CYAN,width=3):
    if len(points)>1: pygame.draw.lines(screen,color,False,points,width)
def clamp(v,a,b): return max(a,min(b,v))

GRID_W, GRID_H = 20, 15
start=(1,1); goal=(17,11); robot=start

def fresh_environment():
    return Environment()
env=fresh_environment()
# Add a reproducible set of clustered obstacles, avoiding start and goal.
def seed_obstacles():
    clusters=[(8,2,4,3),(3,6,4,3),(11,8,4,3),(15,3,3,3),(2,10,4,3),(13,11,4,2)]
    for x,y,w,h in clusters:
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                if random.random()<.78 and (xx,yy) not in (start,goal): env.obstacles.add((xx,yy))
    # keep start/goal accessible
    env.obstacles.discard(start); env.obstacles.discard(goal)
seed_obstacles()
path=find_path(env,robot,goal); path_index=0
steps=0; route_updates=0; paused=True; show_clearance=True; speed=1.0
started=time.monotonic(); elapsed_before=0; last_move=time.monotonic(); move_interval=.34
step_history=deque([0], maxlen=60); update_history=deque([0], maxlen=60)
status='PAUSED'; message='Ready — press SPACE or Start'; events=deque(maxlen=7)
def log(msg): events.appendleft((time.strftime('%H:%M:%S'),msg))
log('PRO dashboard initialized'); log('Clearance-aware A* planner enabled')

def plan_route(note='Route updated'):
    global path,path_index,route_updates,status,message
    path=find_path(env,robot,goal); path_index=0; route_updates+=1
    update_history.append(route_updates)
    if path is None: status='NO PATH'; message='No valid route — remove obstacles'; log('No route available')
    elif robot==goal: status='DESTINATION REACHED'; message='Robot reached the goal!'; log('Destination reached')
    else: status='REPLANNING'; message=note; log(f'Route replanned ({route_updates})')

def reset():
    global env,robot,path,path_index,steps,route_updates,paused,status,message,started,elapsed_before,last_move
    env=fresh_environment(); seed_obstacles(); robot=start; steps=0; route_updates=0; paused=False
    path=find_path(env,robot,goal); path_index=0; status='NAVIGATING'; message='Simulation reset'; started=time.monotonic(); elapsed_before=0; last_move=time.monotonic(); events.clear(); step_history.clear(); step_history.append(0); update_history.clear(); update_history.append(0); log('Simulation reset')

def add_obstacle():
    global message
    candidates=[]
    for y in range(GRID_H):
        for x in range(GRID_W):
            q=(x,y)
            if q in (robot,goal,start) or q in env.obstacles: continue
            if abs(x-robot[0])+abs(y-robot[1])<=2: continue
            candidates.append(q)
    if candidates:
        # Prefer cells near the current route to demonstrate replanning.
        route_candidates=[q for q in candidates if path and min(abs(q[0]-p[0])+abs(q[1]-p[1]) for p in path[1:])<=1]
        q=random.choice(route_candidates or candidates); env.obstacles.add(q); log(f'Obstacle added at {q}'); plan_route('Obstacle detected — route updated')
    else: message='No free cell available'

def clear_obstacles():
    global message
    env.obstacles.clear(); message='Obstacles cleared'; log('All obstacles cleared'); plan_route('Route recalculated')

def elapsed(): return elapsed_before + (time.monotonic()-started if not paused else 0)
def fmt_time(s): return f'{int(s//60):02d}:{int(s%60):02d}'

def draw_button(rect,label,accent,action=None):
    panel(rect,PANEL2,10,accent); pygame.draw.rect(screen,accent,(rect[0]+10,rect[1]+9,4,rect[3]-18),border_radius=2)
    txt(label,rect[0]+23,rect[1]+(rect[3]-20)//2,16,WHITE,True)

running=True
while running:
    dt=clock.tick(60)/1000
    sw,sh=screen.get_size(); screen.fill(BG)
    # responsive layout
    margin=14; top_h=74; gap=14; right_w=min(400,max(330,int(sw*.285)))
    content_y=top_h+margin; bottom_h=max(145,int(sh*.205)); map_w=sw-right_w-3*margin; map_h=sh-content_y-bottom_h-3*margin
    map_rect=(margin,content_y,map_w,map_h); right_x=margin+map_w+gap
    # Header and controls
    panel((margin,margin,sw-2*margin,top_h),PANEL,14)
    pygame.draw.circle(screen,CYAN,(38,49),15); txt('N',29,37,22,BG,True)
    txt('AI AUTONOMOUS NAVIGATION',62,27,23,WHITE,True); txt('PRO  •  CPU SIMULATION DASHBOARD',63,53,12,CYAN,True)
    # control chips
    bx=max(520,sw-690); controls=[('SPACE  Start/Pause',GREEN),('R  Reset',CYAN),('O  Add obstacle',PURPLE),('C  Clearance',ORANGE),('D  YOLO image',BLUE),('− / +  Speed',YELLOW)]
    x=bx
    for label,col in controls:
        width=112 if len(label)<15 else 136
        if x+width<sw-20:
            panel((x,34,width,37),PANEL2,8,col); txt(label,x+9,44,12,WHITE,True); x+=width+7
    # movement simulation
    now=time.monotonic()
    if not paused and path is not None and robot!=goal and now-last_move>=move_interval/speed:
        if path_index+1<len(path):
            nxt=path[path_index+1]
            if nxt not in env.obstacles:
                robot=nxt; path_index+=1; steps+=1; last_move=now
                step_history.append(steps); update_history.append(route_updates)
                if robot==goal: status='DESTINATION REACHED'; message='Robot successfully reached the goal!'; paused=True; elapsed_before+=now-started; log('Robot reached the goal!')
                else: status='NAVIGATING'
            else: plan_route('Obstacle blocks route'); last_move=now
        else: plan_route('Rechecking route')
    # Map panel
    panel(map_rect,PANEL,14)
    txt('LIVE NAVIGATION MAP',map_rect[0]+18,map_rect[1]+12,16,CYAN,True)
    txt(f'{GRID_W} × {GRID_H} GRID',map_rect[0]+map_w-112,map_rect[1]+13,12,MUTED,True)
    gx=map_rect[0]+28; gy=map_rect[1]+43; avail_w=map_w-48; avail_h=map_h-65
    cell=min(avail_w/GRID_W,avail_h/GRID_H); gridpx=GRID_W*cell; gridpy=GRID_H*cell
    ox=gx+(avail_w-gridpx)/2; oy=gy+(avail_h-gridpy)/2
    # grid background and lines
    pygame.draw.rect(screen,(6,21,41),(ox,oy,gridpx,gridpy),border_radius=6)
    for xx in range(GRID_W+1): pygame.draw.line(screen,GRID,(ox+xx*cell,oy),(ox+xx*cell,oy+gridpy),1)
    for yy in range(GRID_H+1): pygame.draw.line(screen,GRID,(ox,oy+yy*cell),(ox+gridpx,oy+yy*cell),1)
    # clearance rings (visual only)
    if show_clearance:
        for ob in env.obstacles:
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                q=(ob[0]+dx,ob[1]+dy)
                if 0<=q[0]<GRID_W and 0<=q[1]<GRID_H and q not in env.obstacles:
                    r=pygame.Rect(ox+q[0]*cell+2,oy+q[1]*cell+2,max(1,cell-4),max(1,cell-4)); pygame.draw.rect(screen,(76,48,29),r,border_radius=4)
    # obstacles
    for ob in env.obstacles:
        r=pygame.Rect(ox+ob[0]*cell+2,oy+ob[1]*cell+2,max(2,cell-4),max(2,cell-4)); pygame.draw.rect(screen,BLOCK,r,border_radius=5); pygame.draw.rect(screen,(94,113,137),r,1,border_radius=5)
    # route and waypoint nodes
    if path:
        pts=[(ox+q[0]*cell+cell/2,oy+q[1]*cell+cell/2) for q in path]
        line(pts,(0,78,111),max(5,int(cell*.22))); line(pts,CYAN,max(2,int(cell*.09)))
        for px,py in pts[1:-1]: pygame.draw.circle(screen,CYAN,(int(px),int(py)),max(2,int(cell*.11)))
    def marker(pos,color,label,glow=False):
        cx=int(ox+pos[0]*cell+cell/2); cy=int(oy+pos[1]*cell+cell/2); rad=max(7,int(cell*.35))
        if glow:
            for rr in (rad+8,rad+4): pygame.draw.circle(screen,(*color[:3],) if False else color,(cx,cy),rr,1)
        pygame.draw.circle(screen,color,(cx,cy),rad)
        lab=font(max(11,int(cell*.42)),True).render(label,True,WHITE); screen.blit(lab,lab.get_rect(center=(cx,cy)))
    marker(start,GREEN,'S',True); marker(goal,RED,'G',True); marker(robot,BLUE,'R',True)
    # right-hand dashboard cards
    rx=right_x; rw=sw-rx-margin
    panel((rx,content_y,rw,78),PANEL,13)
    txt('NAVIGATION STATUS',rx+15,content_y+10,13,MUTED,True)
    status_color=GREEN if status=='DESTINATION REACHED' else RED if status=='NO PATH' else ORANGE if paused else CYAN
    txt(status,rx+15,content_y+33,20,status_color,True); txt(message[:42],rx+15,content_y+57,12,MUTED)
    card_y=content_y+90; card_gap=10; card_w=(rw-card_gap)/2; card_h=70
    remaining=max(0,len(path)-1-path_index) if path else 0
    cards=[('ROBOT POSITION',f'{robot}',CYAN),('GOAL POSITION',f'{goal}',RED),('STEPS TAKEN',steps,BLUE),('REMAINING PATH',remaining,CYAN),('ROUTE UPDATES',route_updates,PURPLE),('OBSTACLES',len(env.obstacles),ORANGE),('ELAPSED TIME',fmt_time(elapsed()),YELLOW),('ROUTE LENGTH',len(path)-1 if path else 'N/A',GREEN)]
    for i,(label,val,col) in enumerate(cards):
        xx=rx+(i%2)*(card_w+card_gap); yy=card_y+(i//2)*(card_h+8)
        panel((xx,yy,card_w,card_h),PANEL2,10)
        pygame.draw.rect(screen,col,(xx+10,yy+13,4,card_h-26),border_radius=2)
        txt(label,xx+22,yy+10,11,MUTED,True); txt(val,xx+22,yy+32,21,col if i in (0,1,4,5,6) else WHITE,True)
    # Mini-map in the previously unused lower-right dashboard area
    mini_y = card_y + 4*(card_h+8) + 8
    mini_h = max(95, sh - mini_y - bottom_h - 2*margin)
    if mini_h > 75:
        panel((rx, mini_y, rw, mini_h), PANEL, 12)
        txt('ENVIRONMENT MINI-MAP', rx+13, mini_y+9, 12, CYAN, True)
        mmx, mmy = rx+14, mini_y+30
        mmw, mmh = rw-28, max(28, mini_h-42)
        mc = min(mmw/GRID_W, mmh/GRID_H)
        mw, mh = GRID_W*mc, GRID_H*mc
        mox, moy = mmx+(mmw-mw)/2, mmy+(mmh-mh)/2
        pygame.draw.rect(screen, (4,18,35), (mox,moy,mw,mh), border_radius=4)
        for ob in env.obstacles:
            pygame.draw.rect(screen, BLOCK, (mox+ob[0]*mc, moy+ob[1]*mc, max(1,mc-1), max(1,mc-1)))
        if path:
            mini_pts=[(mox+q[0]*mc+mc/2,moy+q[1]*mc+mc/2) for q in path]
            line(mini_pts, CYAN, max(1,int(mc*.45)))
        for pos,col in ((start,GREEN),(goal,RED),(robot,BLUE)):
            pygame.draw.circle(screen,col,(int(mox+pos[0]*mc+mc/2),int(moy+pos[1]*mc+mc/2)),max(2,int(mc*.8)))
    # lower panels: controls, mini status/history and live graph
    low_y=sh-bottom_h-margin; left_w=int((sw-3*margin)*.48); mid_w=int((sw-3*margin)*.25); right_low_w=sw-3*margin-left_w-mid_w-2*gap
    panel((margin,low_y,left_w,bottom_h),PANEL,13); txt('SIMULATION CONTROLS',margin+15,low_y+12,15,CYAN,True)
    txt('SPACE Start/Pause    R Reset    O Add obstacle    C Clearance    D YOLO    Q Quit',margin+16,low_y+42,12,WHITE)
    txt('Speed: '+('%.1fx'%speed)+'   |   Clearance overlay: '+('ON' if show_clearance else 'OFF'),margin+16,low_y+66,12,MUTED)
    txt('A* prefers cells with more obstacle clearance.',margin+16,low_y+90,12,MUTED)
    mx=margin+left_w+gap
    panel((mx,low_y,mid_w,bottom_h),PANEL,13); txt('ROUTE OVERVIEW',mx+14,low_y+12,15,CYAN,True)
    txt(f'Path cells: {len(path) if path else 0}',mx+14,low_y+43,13,WHITE); txt(f'Progress: {steps} steps',mx+14,low_y+65,13,WHITE)
    # Live step / route-update sparkline chart
    chart = pygame.Rect(mx+14, low_y+91, max(20,mid_w-28), max(24,bottom_h-104))
    pygame.draw.rect(screen, (5,20,39), chart, border_radius=6)
    for gyline in range(1,4):
        yy=chart.y+gyline*chart.height/4
        pygame.draw.line(screen, GRID, (chart.x+5,yy),(chart.right-5,yy),1)
    def draw_series(values, color):
        vals=list(values)
        if len(vals)<2: return
        vmax=max(1,max(vals))
        pts=[]
        for idx,val in enumerate(vals):
            px=chart.x+5+(chart.width-10)*idx/(len(vals)-1)
            py=chart.bottom-5-(chart.height-10)*val/vmax
            pts.append((int(px),int(py)))
        if len(pts)>1: pygame.draw.lines(screen,color,False,pts,2)
    draw_series(step_history,CYAN)
    draw_series(update_history,PURPLE)
    txt('Steps', chart.x+5, chart.y+3, 9, CYAN)
    txt('Replans', chart.x+52, chart.y+3, 9, PURPLE)
    ex=mx+mid_w+gap
    panel((ex,low_y,right_low_w,bottom_h),PANEL,13); txt('RECENT EVENTS',ex+14,low_y+12,15,CYAN,True)
    if not events: txt('No events yet',ex+14,low_y+44,12,MUTED)
    for i,(tm,ev) in enumerate(list(events)[:5]):
        yy=low_y+40+i*20; txt(tm,ex+14,yy,10,MUTED); txt(ev[:max(12,int((right_low_w-90)/7))],ex+78,yy,11,GREEN if 'reached' in ev.lower() else WHITE)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        elif event.type==pygame.VIDEORESIZE:
            screen=pygame.display.set_mode(event.size,pygame.RESIZABLE)
        elif event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_q,pygame.K_ESCAPE): running=False
            elif event.key==pygame.K_SPACE:
                if paused:
                    paused=False; started=time.monotonic(); status='NAVIGATING' if robot!=goal else 'DESTINATION REACHED'; log('Simulation resumed')
                else:
                    paused=True; elapsed_before+=time.monotonic()-started; status='PAUSED'; log('Simulation paused')
            elif event.key==pygame.K_r: reset()
            elif event.key==pygame.K_o: add_obstacle()
            elif event.key==pygame.K_c: show_clearance=not show_clearance; log('Clearance overlay '+('enabled' if show_clearance else 'disabled'))
            elif event.key in (pygame.K_EQUALS,pygame.K_PLUS,pygame.K_KP_PLUS): speed=min(3.0,speed+.25); log(f'Speed set to {speed:.2f}x')
            elif event.key in (pygame.K_MINUS,pygame.K_KP_MINUS): speed=max(.25,speed-.25); log(f'Speed set to {speed:.2f}x')
            elif event.key==pygame.K_d:
                # YOLO runs only on explicit request; no GPU required. Detection is a demo hook.
                try:
                    from ultralytics import YOLO
                    import os
                    image_path=os.path.join(os.path.expanduser('~'),'Downloads','image.png')
                    if not os.path.exists(image_path): raise FileNotFoundError(f'Image not found: {image_path}')
                    model=YOLO('yolo11n.pt'); results=model.predict(source=image_path,device='cpu',verbose=False)
                    names=set()
                    for result in results:
                        for box in result.boxes:
                            names.add(result.names[int(box.cls[0].item())])
                    count=sum(1 for n in names if n in {'person','car','bicycle','motorcycle','bus','truck','dog','chair'})
                    for _ in range(count): add_obstacle()
                    message=f'YOLO detected {len(names)} unique classes; added demo obstacles'; log(message)
                except Exception as e: message=f'YOLO unavailable: {str(e)[:45]}'; log('YOLO detection failed; check image/model')
            elif event.key==pygame.K_BACKSPACE: clear_obstacles()
pygame.quit()
