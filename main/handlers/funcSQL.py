import time
from datetime import datetime
class sqlite:
    headers        = ('Id','User','Password','Data', 'Status')
    headersimport  = ('Id','User','Password','Data')
    headersCheck   = ('Id','User','Password','Data','Status')
    headersJobs    = ('Id','User','Running','Start Data')
    headersAgents  = ('Id','User','Process')
    createTables   = 'CREATE TABLE IF NOT EXISTS database_bot (id integer PRIMARY KEY AUTOINCREMENT, user text, datestamp text, password text, status text)'
    selectAllBots  = 'SELECT id,user,password,datestamp,status FROM database_bot'
    deleteforID     = 'DELETE FROM database_bot WHERE id= {}'
    zeraids         = 'UPDATE SQLITE_SEQUENCE set seq=0 WHERE name="database_bot"'
    delete_all      = 'DROP TABLE IF EXISTS database_bot'
def DB_insert(con,db,user,password):
    data_time = str(datetime.fromtimestamp(int(time.time())).strftime("%Y-%m-%d %H:%M:%S"))
    db.execute('INSERT INTO database_bot (user,datestamp,password,status) VALUES(?,?,?,?)',(user,data_time,password, 'On'))
    con.commit()

def lengthDB(db):
    size = db.execute('SELECT * FROM database_bot')
    return len(size.fetchall())

def deleteID(con,db,id):
    db.execute(sqlite.deleteforID.format(str(id)))
    con.commit()

def DB_updateStatus(con,db,id,statusUpdated):
    db.execute('UPDATE database_bot SET status = ? WHERE id = ?', (statusUpdated,id))
    con.commit()