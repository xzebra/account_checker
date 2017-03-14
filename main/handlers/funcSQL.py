import time
from datetime import datetime
class sqlite:
    headers        = ('Id','Platform','User','Password','Data','Status')
    headersimport  = ('Id','Platform','User','Password','Data')
    headersCheck   = ('Id','Platform','User','Password','Data','Status')

    createTables   = 'CREATE TABLE IF NOT EXISTS db_accs (id integer PRIMARY KEY AUTOINCREMENT, platform text, user text, password text, status text)'
    selectAllBots  = 'SELECT id,platform,user,password,status FROM db_accs'
    deleteforID     = 'DELETE FROM db_accs WHERE id= {}'
    zeraids         = 'UPDATE SQLITE_SEQUENCE set seq=0 WHERE name="db_accs"'
    delete_all      = 'DROP TABLE IF EXISTS db_accs'
def DB_insert(con,db,platform,user,password,status):
    db.execute('INSERT INTO db_accs (platform,user,password,status) VALUES(?,?,?,?)',(platform,user,password,status))
    con.commit()

def lengthDB(db):
    size = db.execute('SELECT * FROM db_accs')
    return len(size.fetchall())

def deleteID(con,db,id):
    db.execute(sqlite.deleteforID.format(str(id)))
    con.commit()

def DB_updateStatus(con,db,id,statusUpdated):
    db.execute('UPDATE db_accs SET status = ? WHERE id = ?', (statusUpdated,id))
    con.commit()