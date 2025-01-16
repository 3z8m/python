import os, sqlite3
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

dbfile = 'dbfile.db' # SQLデータを保存するファイル


# 初めて実行した時、新たにテーブルを作っておく
if(not os.path.exists(dbfile)):
    with sqlite3.connect(dbfile) as conn:
        sql_create = '''
            create table kyaku (
                namae text,
                nenrei integer,
                primary key (namae)
            )
        '''
        conn.execute(sql_create)


app = FastAPI()

app.mount(path="/stt", app=StaticFiles(directory='stt'))    # cssファイルを収める場所
jintem = Jinja2Templates(directory='tem')                   # jinja2テンプレートのhtmlファイルを収める場所


# インデックスページ
@app.get('/')
def index(request: Request):
    with sqlite3.connect(dbfile) as conn:
        sql_select = '''
            select * from kyaku
        '''
        kyaku_lis = conn.execute(sql_select).fetchall()
        param = {'request': request, 'kyaku': kyaku_lis}
        return jintem.TemplateResponse('index.html', param)


# 各データ表示と編集のページ
@app.get('/kyaku/{namae}')
def kyaku(request: Request, namae: str):
    with sqlite3.connect(dbfile) as conn:
        sql_select = '''
            select * from kyaku where namae==?
        '''
        kyaku = conn.execute(sql_select,[namae]).fetchone()
        if(kyaku):
            param = {'request': request,
                     'namae': namae,
                     'nenrei': kyaku[1]
            }
            return jintem.TemplateResponse('kyaku.html', param)
        else:
            param = {'request': request,
                     'error_message': 'このページは存在しない'
            }
            return jintem.TemplateResponse('error.html', param)  # 存在しない名前が入れられる場合、エラーページへ


# 新しいデータ登録する処理
@app.post('/touroku')
async def touroku(request: Request):
    try:
        with sqlite3.connect(dbfile) as conn:
            form = await request.form()         # フォームに記入されたデータを取得
            namae = form['namae']               # 名前
            nenrei = int(form['nenrei'])        # 年齢
            sql_insert = '''
                insert into kyaku (namae,nenrei)
                values (?,?)
            '''
            conn.execute(sql_insert,(namae,nenrei))
        return RedirectResponse(url='/', status_code=303) # 完成したらインデックスページに戻る
    
    except Exception as err:
        param = {'request': request,
                 'error_message': f'エラー：{type(err)} {err}'
        }
        return jintem.TemplateResponse('error.html', param)      # 間違いがある場合


# データ更新する処理
@app.post('/koushin/{namae}')
async def koushin(request: Request, namae: str):
    try:
        with sqlite3.connect(dbfile) as conn:
            form = await request.form()
            namae_x = form['namae']                 # 新しい名前
            nenrei = int(form['nenrei'])
            sql_update = '''
                update kyaku set namae=?,nenrei=? where namae==?
            '''
            conn.execute(sql_update,(namae_x,nenrei,namae))
        return RedirectResponse(url=f'/kyaku/{namae_x}', status_code=303) # 完成したら新しい名前でデータ表示のページに戻る
    
    except Exception as err:
        param = {'request': request,
                 'error_message': f'エラー：{type(err)} {err}'
        }
        return jintem.TemplateResponse('error.html', param)      # 間違いがある場合


# データ削除する処理
@app.post('/sakujo')
async def sakujo(request: Request):
    try:
        with sqlite3.connect(dbfile) as conn:
            form = await request.form()
            namae = form['namae']
            sql_delete = '''
                delete from kyaku where namae==?
            '''
            conn.execute(sql_delete,[namae])
        return RedirectResponse(url='/', status_code=303)       # インデックスページに戻る
    
    except Exception as err:
        param = {'request': request,
                 'error_message': f'エラー：{type(err)} {err}'
        }
        return jintem.TemplateResponse('error.html', param)      # 間違いがある場合


# データのダウンロード
@app.get('/csv')
def csv():
    with sqlite3.connect(dbfile) as conn:
        data = conn.execute('select * from kyaku').fetchall()               # 全部データを読み込む
        data = '名前,年齢\n'+'\n'.join([d[0]+','+str(d[1]) for d in data])  # データをcsvに
        header = {'Content-Disposition': 'attachment; filename=data.csv'}

        return Response(content=data, headers=header, media_type='text/csv')