import sqlite3
from flask import Flask, redirect, render_template, request, url_for

DATABASE_NAME = 'test.db'
app = Flask(__name__)


# SQL実行関数
def execute_sql(sql):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    result = []

    for row in cur.execute(sql):
        result.append(row)

    con.commit()
    con.close()

    return result


# SELECTデ一夕の配列を連想配列に変換
def convert_tbl_address(raw_row):
    return ({
        'user_id': raw_row[0],
        'user_name': raw_row[1],
        'user_address': raw_row[2],
    })


# 一覧表示（親）
@app.route('/', methods=['GET'])
def show():
    user_data = []

    for data in execute_sql('SELECT * FROM tbl_address'):
        user_data.append(convert_tbl_address(data))

    return render_template('index.html', user_data=user_data)


# 新規登録（親）
@app.route('/', methods=['POST'])
def insert():
    user_name = request.form['user_name']
    user_address = request.form['user_address']

    execute_sql(f'''
                INSERT INTO tbl_address
                (user_name, user_address)
                VALUES ("{user_name}", "{user_address}")
            ''')

    return show()


# 詳細表示（親＆子）
@app.route('/detail', methods=['GET', 'POST'])
def detail():
    
    # 同じエンドポイントでGETとPOSTの両方のリクエストを処理
    #  GET : request.args.get('user_id')を使用し、URLのクエリパラメータからuser_idを取得
    #  POST: request.form['user_id']を使用し、フォームデータからuser_idを取得
    user_id = request.args.get('user_id') if request.method == 'GET' else request.form['user_id']

    # ユーザーデータを取得
    row_raw = execute_sql(f'SELECT * FROM tbl_address WHERE user_id = {user_id}')[0]
    data = convert_tbl_address(row_raw)

    # フードTBLのデータを取得
    foods = execute_sql(f'SELECT * FROM tbl_food WHERE user_id = {user_id}')
    food_data = [{'food_id': row[0], 'food_content': row[2]} for row in foods]

    return render_template('detail.html', data=data, food_data=food_data)


# 更新（親）
@app.route('/update', methods=['POST'])
def update():
    user_id = request.form['user_id']
    user_name = request.form['user_name']
    user_address = request.form['user_address']

    execute_sql(f'''
                UPDATE tbl_address 
                SET
                    user_name = "{user_name}",
                    user_address = "{user_address}"
                WHERE user_id = {user_id}
            ''')

    return redirect(url_for('show'))


# 削除（親）
@app.route('/delete', methods=['POST'])
def delete():
    user_id = request.form['user_id']
    execute_sql(f'DELETE FROM tbl_address WHERE user_id = {user_id}')

    return redirect(url_for('show'))


# 新規登録（子）
@app.route('/add_food', methods=['POST'])
def add_food():
    user_id = request.form['user_id']
    food_content = request.form['food_content']

    execute_sql(f'''
                INSERT INTO tbl_food
                (user_id, food_content)
                VALUES ({user_id}, "{food_content}")
            ''')

    return redirect(url_for('detail', user_id=user_id))


# 更新（子）
@app.route('/update_food', methods=['POST'])
def update_food():
    food_id = request.form['food_id']
    food_content = request.form['food_content']

    execute_sql(f'''
                UPDATE tbl_food 
                SET
                    food_content = "{food_content}"
                WHERE food_id = {food_id}
            ''')

    user_id = request.form['user_id']

    return redirect(url_for('detail', user_id=user_id))


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')