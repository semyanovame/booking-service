from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from .config import APP_TITLE
from .database import init_db, SessionLocal
from .models import Room, Slot, Booking, User
from .auth import get_password_hash, verify_password, create_access_token, decode_access_token
from .routers import auth_router, rooms_router, bookings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    if not db.query(User).first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin123"), role="admin"))
        db.add(User(username="user", hashed_password=get_password_hash("user123"), role="employee"))
        r = Room(name="Переговорная #1", description="4 человека")
        db.add(r); db.flush()
        db.add(Slot(room_id=r.id, start_time="09:00", end_time="11:00"))
        db.add(Slot(room_id=r.id, start_time="11:00", end_time="13:00"))
        db.commit()
    db.close()
    yield

app = FastAPI(title=APP_TITLE, lifespan=lifespan, docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router.router)
app.include_router(rooms_router.router)
app.include_router(bookings_router.router)

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    db = SessionLocal()
    user = db.query(User).filter(User.username == data["username"]).first()
    if not user or not verify_password(data["password"], user.hashed_password):
        db.close()
        return {"error": "Неверный пароль"}
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role.value})
    db.close()
    return {"token": token, "username": user.username, "role": user.role.value}

@app.get("/api/me")
async def me(token: str):
    try:
        p = decode_access_token(token)
        return {"username": p["username"], "role": p["role"]}
    except:
        return {"error": "bad token"}

@app.get("/api/rooms-ui")
async def rooms_ui():
    db = SessionLocal()
    rooms = db.query(Room).all()
    result = []
    for room in rooms:
        result.append({
            "id": room.id,
            "name": room.name,
            "slots": [{"id": s.id, "time": f"{s.start_time}-{s.end_time}"} for s in room.slots]
        })
    db.close()
    return result

@app.post("/api/book")
async def book(request: Request):
    data = await request.json()
    token = data.get("token", "")
    if not token:
        return {"error": "нет токена"}
    try:
        p = decode_access_token(token)
        uid = int(p["sub"])
    except Exception as e:
        return {"error": str(e)}
    
    from datetime import datetime, date as dt_date
    booking_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    if booking_date < dt_date.today():
        return {"error": "нельзя бронировать прошлое"}
    
    db = SessionLocal()
    b = Booking(user_id=uid, slot_id=data["slot_id"], date=datetime.combine(booking_date, datetime.min.time()))
    db.add(b); db.commit()
    db.close()
    return {"ok": True}

@app.delete("/api/book/{bid}")
async def cancel(bid: int, token: str):
    try:
        p = decode_access_token(token)
        uid = int(p["sub"])
        role = p["role"]
    except:
        return {"error": "bad token"}
    db = SessionLocal()
    b = db.query(Booking).filter(Booking.id == bid).first()
    if b and (b.user_id == uid or role == "admin"):
        db.delete(b); db.commit()
    db.close()
    return {"ok": True}

@app.get("/api/my")
async def my(token: str):
    try:
        p = decode_access_token(token)
        uid = int(p["sub"])
    except:
        return []
    db = SessionLocal()
    bs = db.query(Booking).filter(Booking.user_id == uid).all()
    result = [{"id": b.id, "slot_id": b.slot_id, "date": b.date.isoformat()[:10], "room": b.slot.room.name if b.slot and b.slot.room else None} for b in bs]
    db.close()
    return result


@app.get("/", response_class=HTMLResponse)
def index():
    return """<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Бюро</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#F5F5F5;color:#1A1A1A;padding:30px;max-width:1200px;margin:0 auto}
h1{font-weight:300;font-size:2em;margin-bottom:15px;color:#333}
h1 b{font-weight:600;color:#E87461}
.login{display:flex;gap:10px;margin-bottom:20px;max-width:500px}
input{padding:12px 18px;border:1px solid #DDD;font-size:1em;flex:1;border-radius:4px}
button{padding:12px 24px;background:#E87461;color:white;border:none;font-size:1em;cursor:pointer;font-weight:600;border-radius:4px}
button:hover{opacity:0.85}
.layout{display:flex;gap:24px;align-items:flex-start}
.left{flex:1;min-width:0}
.right{width:320px;flex-shrink:0;display:flex;flex-direction:column;gap:20px}
.datebar{display:flex;gap:10px;align-items:center;margin-bottom:20px}
.room{background:white;padding:18px 20px;margin-bottom:14px;border-radius:8px;border:1px solid #EEE}
.room h2{font-weight:500;font-size:1.05em;margin-bottom:10px}
.slots{display:flex;gap:8px;flex-wrap:wrap}
.slot{padding:8px 14px;font-size:0.85em;cursor:pointer;border-radius:20px;border:2px solid;white-space:nowrap}
.slot.green{background:#E8F5E9;color:#2E7D32;border-color:#A5D6A7}
.slot.green:hover{background:#A5D6A7;color:white}
.slot.orange{background:#FFF3E0;color:#E65100;border-color:#FFCC80}
.slot.orange:hover{background:#FFCC80}
.small{font-size:0.8em;color:#999}
.panel{background:white;padding:16px 20px;border-radius:8px;border:1px solid #EEE}
.panel h3{font-weight:500;font-size:0.95em;margin-bottom:10px;color:#333}
.panel .row{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid #F5F5F5;font-size:0.85em;gap:10px}
.panel .row:last-child{border-bottom:none}
.panel .row span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.panel .row a{color:#E87461;text-decoration:none;font-weight:500;flex-shrink:0}
.panel .row a:hover{text-decoration:underline}
.msg{position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:6px;color:white;z-index:99;font-weight:500}
</style></head><body>
<h1>Бюро<b>.</b> <span class="small">бронирование переговорок</span></h1>
<div class="login" id="loginBox"><input id="lu" placeholder="логин"><input type="password" id="lp" placeholder="пароль"><button onclick="login()">войти</button></div>
<div id="app" style="display:none">
<p style="margin-bottom:12px"><b id="un"></b> · <span class="small" id="urole"></span> · <a href="#" onclick="logout()" style="color:#E87461">выйти</a></p>
<div class="layout">
<div class="left">
<div class="datebar"><input type="date" id="dp"><button onclick="load()">показать</button></div>
<div id="roomsBox"></div>
</div>
<div class="right">
<div class="panel"><h3>Мои бронирования</h3><div id="myBox"><span class="small">пусто</span></div></div>
<div class="panel" id="adminPanel" style="display:none"><h3>Все бронирования (админ)</h3><div id="allBox"><span class="small">пусто</span></div></div>
</div>
</div>
</div>
<script>
var T=localStorage.getItem('bt')||'',U=null;if(T)chk();
var today=new Date().toISOString().split('T')[0];
document.getElementById('dp').value=today;
function msg(m,t){var e=document.createElement('div');e.className='msg';e.style.background=t==='err'?'#E87461':'#333';e.textContent=m;document.body.appendChild(e);setTimeout(function(){e.remove()},2000)}
async function login(){var u=lu.value,p=lp.value;try{var r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});var d=await r.json();if(d.error){msg('неверно','err');return}T=d.token;U={username:d.username,role:d.role};localStorage.setItem('bt',T);upd();load()}catch(e){}}
function logout(){T='';U=null;localStorage.removeItem('bt');upd();load()}
async function chk(){try{var r=await fetch('/api/me?token='+T);if(r.ok){U=await r.json();upd()}else{T='';localStorage.removeItem('bt')}}catch(e){}}
function upd(){if(U){loginBox.style.display='none';app.style.display='block';un.textContent=U.username;urole.textContent=U.role==='admin'?'админ':'сотрудник';if(U.role==='admin'){loadAll()}else{document.getElementById('adminPanel').style.display='none'}}else{loginBox.style.display='flex';app.style.display='none';document.getElementById('adminPanel').style.display='none'}}
async function load(){var dt=document.getElementById('dp').value||today;var c=document.getElementById('roomsBox');try{var my=[];if(T){var mr=await fetch('/api/my?token='+T);if(mr.ok)my=await mr.json()}var rooms=await(await fetch('/api/rooms-ui')).json();var ms={};my.forEach(function(b){if(b.date===dt)ms[b.slot_id]=b.id});c.innerHTML=rooms.map(function(r){return'<div class="room"><h2>'+r.name+'</h2><div class="slots">'+r.slots.map(function(s){var cls='green',txt='',cl='book('+s.id+')';if(ms[s.id]){cls='orange';txt='';cl='cancel('+ms[s.id]+')'}return'<div class="slot '+cls+'" onclick="'+cl+'" title="'+txt+'">'+s.time+'</div>'}).join('')+'</div></div>'}).join('');myLoad(my)}catch(e){}}
function myLoad(my){var c=document.getElementById('myBox');if(!T){c.innerHTML='<span class="small">войдите</span>';return}if(!my||!my.length){c.innerHTML='<span class="small">пусто</span>';return}c.innerHTML=my.map(function(b){var n='Слот '+b.slot_id;if(b.room)n=b.room;return'<div class="row"><span title="'+n+'">'+n+' · '+b.date+'</span><a href="#" onclick="cancel('+b.id+')">отменить</a></div>'}).join('')}
async function book(sid){if(!T){msg('войдите','err');return}var dt=document.getElementById('dp').value||today;try{var r=await fetch('/api/book',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slot_id:sid,date:dt,token:T})});var d=await r.json();if(d.ok){msg('готово');load()}else{msg(d.error||'ошибка','err')}}catch(e){msg('ошибка сети','err')}}
async function cancel(id){try{var r=await fetch('/api/book/'+id+'?token='+T,{method:'DELETE'});if(r.ok){msg('отменено');load();if(U&&U.role==='admin')loadAll()}else{msg('ошибка','err')}}catch(e){}}
async function loadAll(){if(!U||U.role!=='admin')return;document.getElementById('adminPanel').style.display='block';var r=await fetch('/api/bookings/all',{headers:{'Authorization':'Bearer '+T}});if(!r.ok)return;var data=await r.json();var c=document.getElementById('allBox');if(!data.length){c.innerHTML='<span class="small">пусто</span>';return}c.innerHTML=data.map(function(b){var n='Слот '+b.slot_id;if(b.room_name)n=b.room_name;var uname=b.username||'Польз. '+b.user_id;return'<div class="row"><span title="'+uname+'">'+uname+' · '+n+' · '+b.date+'</span><a href="#" onclick="cancel('+b.id+')">отменить</a></div>'}).join('')}
upd();if(T)load();
</script></body></html>"""