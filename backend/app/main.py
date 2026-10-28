from contextlib import asynccontextmanager
from datetime import datetime,timezone
import csv,io
from fastapi import FastAPI,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel,Field
from .database import connect,init_db
from .seed import seed_if_empty
from .ai import classify,duplicate_candidate,score_priority
class IncidentCreate(BaseModel):
    title:str=Field(min_length=4,max_length=140); description:str=Field(min_length=8,max_length=2000)
    neighborhood:str=Field(min_length=2,max_length=100); latitude:float=Field(ge=-90,le=90); longitude:float=Field(ge=-180,le=180)
    severity:int=Field(default=3,ge=1,le=5); public_impact:int=Field(default=3,ge=1,le=5)
@asynccontextmanager
async def lifespan(app):init_db();seed_if_empty();yield
app=FastAPI(title='CivicSignal AI API',version='0.1.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_methods=['*'],allow_headers=['*'])
def asdict(r):return dict(r)
@app.get('/')
def root():return {'name':'CivicSignal AI','status':'ok','docs':'/docs'}
@app.get('/api/health')
def health():return {'status':'healthy'}
@app.get('/api/incidents')
def incidents(category:str|None=None,priority:str|None=None,status:str|None=None,q:str|None=None):
    sql='SELECT * FROM incidents WHERE 1=1';args=[]
    for col,val in [('category',category),('priority_level',priority),('status',status)]:
        if val and val!='All':sql+=f' AND {col}=?';args.append(val)
    if q:sql+=' AND (title LIKE ? OR description LIKE ? OR neighborhood LIKE ?)';args += [f'%{q}%']*3
    sql+=' ORDER BY priority_score DESC,created_at DESC'
    with connect() as c:return [asdict(r) for r in c.execute(sql,args).fetchall()]
@app.get('/api/summary')
def summary():
    with connect() as c:
        cats=c.execute('SELECT category,COUNT(*) count FROM incidents GROUP BY category').fetchall();total=c.execute('SELECT COUNT(*) FROM incidents').fetchone()[0];opened=c.execute("SELECT COUNT(*) FROM incidents WHERE status='Open'").fetchone()[0];high=c.execute("SELECT COUNT(*) FROM incidents WHERE priority_level IN ('High','Critical') AND status='Open'").fetchone()[0];hoods=c.execute('SELECT neighborhood,COUNT(*) count,ROUND(AVG(priority_score),1) avg_priority FROM incidents GROUP BY neighborhood ORDER BY count DESC,avg_priority DESC LIMIT 6').fetchall()
    return {'total':total,'open':opened,'high_priority':high,'categories':[asdict(r) for r in cats],'neighborhoods':[asdict(r) for r in hoods]}
@app.post('/api/incidents')
def create(p:IncidentCreate):
    text=f'{p.title}. {p.description}';cat=classify(text)
    with connect() as c:
        rows=c.execute('SELECT * FROM incidents').fetchall();dup=duplicate_candidate(text,p.latitude,p.longitude,rows);score,level,explanation=score_priority(p.severity,p.public_impact,cat,bool(dup));created=datetime.now(timezone.utc).isoformat()
        cur=c.execute("INSERT INTO incidents(title,description,category,neighborhood,latitude,longitude,severity,public_impact,priority_score,priority_level,priority_explanation,duplicate_of,duplicate_similarity,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'Open',?)",(p.title,p.description,cat,p.neighborhood,p.latitude,p.longitude,p.severity,p.public_impact,score,level,explanation,dup['id'] if dup else None,dup['similarity'] if dup else 0,created));c.commit();row=asdict(c.execute('SELECT * FROM incidents WHERE id=?',(cur.lastrowid,)).fetchone())
    row['duplicate_candidate']=dup;return row
@app.patch('/api/incidents/{incident_id}/status')
def update_status(incident_id:int,status:str=Query(...,pattern='^(Open|In Progress|Resolved)$')):
    with connect() as c:
        cur=c.execute('UPDATE incidents SET status=? WHERE id=?',(status,incident_id))
        if not cur.rowcount:raise HTTPException(404,'Incident not found')
        c.commit();return asdict(c.execute('SELECT * FROM incidents WHERE id=?',(incident_id,)).fetchone())
@app.get('/api/export.csv')
def export_csv():
    with connect() as c:rows=c.execute('SELECT * FROM incidents ORDER BY priority_score DESC').fetchall()
    b=io.StringIO();w=csv.writer(b)
    if rows:w.writerow(rows[0].keys());w.writerows([list(r) for r in rows])
    return Response(b.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=civicsignal-incidents.csv'})
