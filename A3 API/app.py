from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chave_secreta'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'diego12@',
    'database': 'biblioteca'
}


@app.route('/')
def index():
    if 'user_id' in session:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT nome FROM usuarios")
        usuarios = cursor.fetchall()
        conn.close()

        return render_template('biblioteca_base.html', usuarios=usuarios)
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['nome'] = user['nome']
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas, tente novamente.')
    return render_template('login_base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
            conn.commit()
            flash('Conta criada com sucesso! Faça login.')
            return redirect(url_for('login'))
        except mysql.connector.errors.IntegrityError:
            flash('Email já está em uso.')
        finally:
            conn.close()
    return render_template('registro_base.html')


@app.route('/usuario_configuracao', methods=['GET', 'POST'])
def usuario_configuracao():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        novo_nome = request.form.get('nome')
        novo_email = request.form.get('email')
        nova_senha = request.form.get('senha')
        excluir_conta = request.form.get('excluir_conta')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if excluir_conta:
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (session['user_id'],))
            conn.commit()
            session.pop('user_id', None)
            session.pop('nome', None)
            flash('Conta excluída com sucesso.')
            return redirect(url_for('login'))
        else:
            if novo_nome:
                cursor.execute("UPDATE usuarios SET nome = %s WHERE id = %s", (novo_nome, session['user_id']))
            if novo_email:
                cursor.execute("UPDATE usuarios SET email = %s WHERE id = %s", (novo_email, session['user_id']))
            if nova_senha:
                cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (nova_senha, session['user_id']))
            conn.commit()
            flash('Dados atualizados com sucesso.')

        conn.close()
        return redirect(url_for('usuario_configuracao'))

    return render_template('usuario_configuracao_base.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('nome', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
