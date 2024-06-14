from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mahasiswa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Mahasiswa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    nim = db.Column(db.String(10), unique=True, nullable=False)
    nilai = db.relationship('Nilai', backref='mahasiswa', cascade='all, delete-orphan', lazy=True)

class Nilai(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mahasiswa_id = db.Column(db.Integer, db.ForeignKey('mahasiswa.id'), nullable=False)
    mata_kuliah = db.Column(db.String(100), nullable=False)
    uts = db.Column(db.Float, nullable=False)
    uas = db.Column(db.Float, nullable=False)
    kat = db.Column(db.Float, nullable=False)

    @property
    def nilai_akhir(self):
        return 0.2 * self.uts + 0.2 * self.uas + 0.6 * self.kat

# Create all tables within the application context
with app.app_context():
    db.create_all()

# Routes

@app.route('/')
def index():
    mahasiswa = Mahasiswa.query.all()
    return render_template('index.html', mahasiswa=mahasiswa)

@app.route('/mahasiswa/create', methods=['GET', 'POST'])
def create_mahasiswa():
    if request.method == 'POST':
        nama = request.form['nama']
        nim = request.form['nim']
        
        existing_mahasiswa = Mahasiswa.query.filter_by(nim=nim).first()
        if existing_mahasiswa:
            return redirect(url_for('index', error='NIM sudah digunakan'))
        
        mahasiswa = Mahasiswa(nama=nama, nim=nim)
        db.session.add(mahasiswa)
        db.session.commit()

        return redirect(url_for('index'))
    
    return render_template('create_mahasiswa.html')

@app.route('/mahasiswa/update/<int:id>', methods=['GET', 'POST'])
def update_mahasiswa(id):
    mahasiswa = Mahasiswa.query.get(id)
    if not mahasiswa:
        return redirect(url_for('index', error='Mahasiswa not found'))
    
    if request.method == 'POST':
        nama = request.form['nama']
        nim = request.form['nim']
        
        existing_mahasiswa = Mahasiswa.query.filter(Mahasiswa.nim == nim, Mahasiswa.id != id).first()
        if existing_mahasiswa:
            return redirect(url_for('index', error='NIM sudah digunakan'))
        
        mahasiswa.nama = nama
        mahasiswa.nim = nim
        
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('update_mahasiswa.html', mahasiswa=mahasiswa)

@app.route('/mahasiswa/delete/<int:id>', methods=['POST'])
def delete_mahasiswa(id):
    mahasiswa = Mahasiswa.query.get(id)
    if not mahasiswa:
        return redirect(url_for('index', error='Mahasiswa not found'))
    
    db.session.delete(mahasiswa)
    db.session.commit()
    
    return redirect(url_for('index'))

# Routes and logic for nilai (academic grades)

@app.route('/mahasiswa/<int:mahasiswa_id>/nilai/create', methods=['GET', 'POST'])
def create_nilai(mahasiswa_id):
    mahasiswa = Mahasiswa.query.get(mahasiswa_id)
    if not mahasiswa:
        return redirect(url_for('index', error='Mahasiswa not found'))

    if request.method == 'POST':
        mata_kuliah = request.form['mata_kuliah']
        uts = request.form['uts']
        uas = request.form['uas']
        kat = request.form['kat']

        if not all([mata_kuliah, uts, uas, kat]):
            return redirect(url_for('create_nilai', mahasiswa_id=mahasiswa_id, error='Semua field harus diisi'))

        try:
            nilai = Nilai(mahasiswa_id=mahasiswa_id, mata_kuliah=mata_kuliah, uts=float(uts), uas=float(uas), kat=float(kat))
            db.session.add(nilai)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return redirect(url_for('create_nilai', mahasiswa_id=mahasiswa_id, error=str(e)))

    return render_template('create_nilai.html', mahasiswa=mahasiswa)

@app.route('/nilai/update/<int:id>', methods=['GET', 'POST'])
def update_nilai(id):
    nilai = Nilai.query.get(id)
    if not nilai:
        return redirect(url_for('index', error='Nilai not found'))

    if request.method == 'POST':
        mata_kuliah = request.form['mata_kuliah']
        uts = request.form['uts']
        uas = request.form['uas']
        kat = request.form['kat']

        if not all([mata_kuliah, uts, uas, kat]):
            return redirect(url_for('update_nilai', id=id, error='Semua field harus diisi'))

        try:
            nilai.mata_kuliah = mata_kuliah
            nilai.uts = float(uts)
            nilai.uas = float(uas)
            nilai.kat = float(kat)

            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return redirect(url_for('update_nilai', id=id, error=str(e)))

    return render_template('update_nilai.html', nilai=nilai)

@app.route('/nilai/delete/<int:id>', methods=['POST'])
def delete_nilai(id):
    nilai = Nilai.query.get(id)
    if not nilai:
        return redirect(url_for('index', error='Nilai not found'))
    
    db.session.delete(nilai)
    db.session.commit()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
