from datetime import datetime,timedelta,timezone
from .database import connect
DATA=[
("Deep pothole near school entrance","A deep pothole is forcing two-wheelers into traffic near the school gate.","Road Damage","RS Puram",11.0068,76.9558,4,4),
("Water leaking from roadside pipe","Water has been flowing continuously from a pipe joint since this morning.","Water Leakage","Gandhipuram",11.0183,76.9675,4,5),
("Drain overflowing after rain","The storm drain is overflowing onto the pedestrian path.","Drainage","Peelamedu",11.0262,77.0040,4,4),
("Streetlight out on residential lane","The streetlight near the park has not worked for three nights.","Streetlight Failure","Saibaba Colony",11.0236,76.9442,3,3),
("Road surface cracking near junction","Several cracks have appeared on the road near the busy junction.","Road Damage","Town Hall",10.9950,76.9610,3,4),
("Blocked drain beside market","Waste has blocked the drain and dirty water is collecting beside market stalls.","Drainage","Ukkadam",10.9905,76.9615,5,4),
("Dark stretch near bus stop","The lamp near the bus stop is broken and the pavement is very dark.","Streetlight Failure","Peelamedu",11.0270,77.0029,3,4),
("Possible repeat pipe leak","There is water pooling again beside the same road after the pipe repair.","Water Leakage","Gandhipuram",11.0188,76.9678,3,4),
("Loose road cover near crossing","A sunken utility cover is creating a hazard for cyclists.","Road Damage","RS Puram",11.0073,76.9562,3,3),
("Rainwater trapped at underpass","Water is collecting at the underpass and pedestrians are walking in the road.","Drainage","Ukkadam",10.9910,76.9621,4,5)]
def seed_if_empty():
    with connect() as c:
        if c.execute('SELECT COUNT(*) FROM incidents').fetchone()[0]:return
        now=datetime.now(timezone.utc)
        for i,(title,desc,cat,hood,lat,lon,sev,impact) in enumerate(DATA):
            risk=5 if cat in ('Water Leakage','Drainage') else 4 if cat=='Road Damage' else 3
            score=round(20*(.45*sev+.35*impact+.15*risk+.05),1);level='Critical' if score>=85 else 'High' if score>=70 else 'Medium' if score>=50 else 'Low'
            expl=f'Seeded demo score from severity {sev}/5, public impact {impact}/5, and category risk. Human review required.'
            c.execute("INSERT INTO incidents(title,description,category,neighborhood,latitude,longitude,severity,public_impact,priority_score,priority_level,priority_explanation,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,'Open',?)",(title,desc,cat,hood,lat,lon,sev,impact,score,level,expl,(now-timedelta(hours=3*i)).isoformat()))
        c.commit()
