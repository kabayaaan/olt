# app.py
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Simulasi Koneksi OLT ZTE ---
# Di sini Anda akan mengimplementasikan logika untuk berinteraksi dengan OLT ZTE.
# Untuk demo ini, kita hanya akan mencetak perintah yang akan dieksekusi.

def generate_olt_commands(gpon_olt_interface, ont_sn, onu_id, vlan, name, description):
    """
    Menghasilkan daftar perintah OLT ZTE berdasarkan semua input, dengan format yang spesifik.
    """
    # Contoh format interface: gpon-olt_1/1/1
    # Kita perlu memisahkan bagian-bagiannya untuk perintah 'onu' atau 'interface gpon-onu'
    try:
        # Asumsi format gpon-olt_x/x/x
        parts = gpon_olt_interface.split('_')[1].split('/')
        frame = parts[0]
        slot = parts[1]
        port = parts[2]
    except IndexError:
        # Fallback jika format tidak sesuai atau parsing gagal
        frame, slot, port = "1", "1", "1" # Default jika parsing gagal

    commands = [
        f"interface {gpon_olt_interface}",
        f"onu {onu_id} type ALL-GPON sn {ont_sn}", # Perintah untuk menambahkan ONU
        f"exit", # Keluar dari interface gpon-olt
        f"interface gpon-onu_{frame}/{slot}/{port}:{onu_id}", # Masuk ke interface ONU
        f"tcont 1 profile UNLIMITED", # Konfigurasi TCONT
        f"gemport 1 tcont 1", # Konfigurasi GEMPORT
        f"service-port 1 vport 1 user-vlan {vlan} vlan {vlan}", # Konfigurasi service-port
        f"name {name}", # Memberi nama pada ONU
        f"description {description}", # Memberi deskripsi pada ONU
        f"exit", # Keluar dari interface gpon-onu
        f"pon-onu-mng gpon-onu_{frame}/{slot}/{port}:{onu_id}", # Masuk ke mode manajemen ONU
        f"service 1 gemport 1 vlan {vlan}", # Konfigurasi layanan di mode manajemen
        f"exit", # Keluar dari mode manajemen ONU
        # Perintah 'configure terminal' dan 'write' biasanya dilakukan di awal dan akhir sesi
        # Namun, jika Anda ingin setiap blok perintah diawali 'configure terminal' dan diakhiri 'write',
        # Anda bisa menambahkannya di sini. Untuk format yang Anda berikan, saya asumsikan ini adalah bagian dari sesi yang lebih besar.
        # Jika Anda ingin menyertakan 'configure terminal' di awal dan 'write' di akhir dari daftar ini:
        # commands.insert(0, "configure terminal")
        # commands.append("write")
    ]
    return commands

@app.route('/')
def index():
    """
    Merender halaman utama aplikasi.
    """
    return render_template('index.html')

@app.route('/configure', methods=['POST'])
def configure_olt():
    """
    Menerima data konfigurasi dari frontend, menghasilkan perintah OLT,
    dan mengembalikan respons JSON.
    """
    data = request.json
    gpon_olt_interface = data.get('gpon_olt_interface')
    sn = data.get('sn')
    onu_id = data.get('onu_id')
    vlan = data.get('vlan')
    name = data.get('name')
    description = data.get('description')

    # Validasi semua input.
    if not all([gpon_olt_interface, sn, onu_id, vlan, name, description]):
        return jsonify({"status": "error", "message": "Semua field harus diisi."}), 400

    # Pastikan ONU ID adalah angka dan dalam rentang yang valid (contoh: 1-128).
    try:
        onu_id = int(onu_id)
        if not (1 <= onu_id <= 128): # Sesuaikan rentang ini jika OLT Anda mendukung lebih banyak.
            return jsonify({"status": "error", "message": "ONU ID harus antara 1 dan 128."}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "ONU ID harus berupa angka."}), 400

    # Menghasilkan perintah OLT berdasarkan input yang diterima.
    olt_commands = generate_olt_commands(gpon_olt_interface, sn, onu_id, vlan, name, description)

    # Mencetak perintah ke konsol backend untuk simulasi.
    print(f"--- Simulasi Perintah OLT untuk Interface: {gpon_olt_interface}, SN: {sn}, ONU ID: {onu_id} ---")
    for cmd in olt_commands:
        print(cmd)
    print("------------------------------------------")

    # Di sini Anda akan menambahkan logika untuk koneksi ke OLT sungguhan dan menjalankan perintah.
    # Misalnya, menggunakan pustaka seperti Netmiko, Paramiko, atau Telnetlib.

    # Mengembalikan respons sukses ke frontend.
    return jsonify({
        "status": "success",
        "message": f"Simulasi konfigurasi untuk SN {sn} (ONU ID: {onu_id}) di {gpon_olt_interface} berhasil. Perintah yang akan dieksekusi ditampilkan di konsol backend.",
        "commands_generated": olt_commands
    })

if __name__ == '__main__':
    # Menjalankan aplikasi Flask dalam mode debug.
    # Mode debug akan otomatis me-reload server saat ada perubahan kode dan memberikan informasi error yang lebih detail.
    app.run(debug=True)
