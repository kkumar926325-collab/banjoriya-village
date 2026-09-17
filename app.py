from flask import Flask, request, session, redirect, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "banjoriya-secret-key"

# =========================
# ADMIN PASSWORD
# =========================
import os
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# =========================
# FOLDERS
# =========================
BASE = os.path.expanduser("~/banjoriya-village")
PHOTO_DIR = os.path.join(BASE, "photos")
VIDEO_DIR = os.path.join(BASE, "videos")

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

ALLOWED_PHOTOS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_VIDEOS = {"mp4", "webm", "ogg"}


def allowed_file(filename, allowed):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed
    )


# =========================
# SERVE PHOTOS
# =========================
@app.route("/photos/<path:filename>")
def photos(filename):
    return send_from_directory(PHOTO_DIR, filename)


# =========================
# SERVE VIDEOS
# =========================
@app.route("/videos/<path:filename>")
def videos(filename):
    return send_from_directory(VIDEO_DIR, filename)


# =========================
# HOME WEBSITE
# =========================
@app.route("/")
def home():

    photos_list = sorted([
        f for f in os.listdir(PHOTO_DIR)
        if allowed_file(f, ALLOWED_PHOTOS)
        and f.lower() != "logo.png"
    ])

    videos_list = sorted([
        f for f in os.listdir(VIDEO_DIR)
        if allowed_file(f, ALLOWED_VIDEOS)
    ])

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Banjoriya Village</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:Arial,sans-serif;
    background:#f5f8f5;
    color:#17251d;
}

/* HEADER */

header{
    position:sticky;
    top:0;
    z-index:10;
    height:58px;
    background:white;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:8px 15px;
    box-shadow:0 2px 12px rgba(0,0,0,.12);
}

.logo-box{
    display:flex;
    align-items:center;
    gap:9px;
}

.logo-box img{
    width:38px;
    height:38px;
    border-radius:50%;
    object-fit:cover;
}

.logo-box b{
    font-size:14px;
}

.admin{
    text-decoration:none;
    color:#176b42;
    font-weight:bold;
    font-size:13px;
}

/* HERO */

.hero{
    min-height:330px;
    background:
    linear-gradient(rgba(0,0,0,.28),rgba(0,0,0,.45)),
    url("/photos/village.jpg");
    background-size:cover;
    background-position:center;
    display:flex;
    justify-content:center;
    align-items:center;
    text-align:center;
}

.hero h1{
    color:white;
    font-size:42px;
    margin:0;
    text-shadow:0 4px 12px rgba(0,0,0,.7);
}

/* SECTIONS */

.section{
    max-width:1100px;
    margin:auto;
    padding:45px 14px;
}

.section-title{
    text-align:center;
    margin-bottom:25px;
}

.section-title h2{
    margin:0;
    font-size:27px;
}

.section-title p{
    margin:7px 0;
    color:#777;
}

/* PHOTO GRID */

.gallery{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
    gap:16px;
}

.photo-card{
    background:white;
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 5px 18px rgba(0,0,0,.12);
    cursor:pointer;
    transition:.25s;
}

.photo-card:hover{
    transform:translateY(-4px);
}

.photo-card img{
    width:100%;
    height:230px;
    display:block;
    object-fit:cover;
}

/* VIDEO */

.video-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
    gap:20px;
}

.video-card{
    background:#111;
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 5px 18px rgba(0,0,0,.18);
}

.video-card video{
    width:100%;
    height:auto;
    max-height:650px;
    display:block;
    object-fit:contain;
    background:#111;
}

/* EMPTY */

.empty{
    text-align:center;
    color:#777;
    padding:30px;
}

/* FOOTER */

footer{
    background:#07502f;
    color:white;
    text-align:center;
    padding:28px 10px;
}

footer b{
    font-size:16px;
}

footer p{
    margin:7px 0 0;
    font-size:13px;
}

/* PHOTO VIEWER */

#viewer{
    display:none;
    position:fixed;
    inset:0;
    z-index:100;
    background:rgba(0,0,0,.94);
    justify-content:center;
    align-items:center;
    padding:20px;
}

#bigPhoto{
    max-width:95%;
    max-height:90%;
    object-fit:contain;
    border-radius:10px;
}

.close{
    position:absolute;
    top:15px;
    right:20px;
    color:white;
    font-size:38px;
    cursor:pointer;
}

</style>

</head>

<body>

<header>

<div class="logo-box">

<img src="/photos/logo.png">

<b>BANJORIYA VILLAGE</b>

</div>

<a class="admin" href="/admin">🔐 Admin</a>

</header>


<section class="hero">

<h1>Banjoriya ❤️</h1>

</section>


<section class="section">

<div class="section-title">
<h2>📸 Village Photos</h2>
<p>हमारे गाँव की खूबसूरत यादें</p>
</div>

{% if photos_list %}

<div class="gallery">

{% for photo in photos_list %}

<div class="photo-card"
onclick="openPhoto(this.querySelector('img').src)">

<img src="/photos/{{ photo }}">

</div>

{% endfor %}

</div>

{% else %}

<div class="empty">
अभी कोई फोटो नहीं है।
</div>

{% endif %}

</section>


<section class="section">

<div class="section-title">
<h2>🎬 Village Videos</h2>
<p>गाँव के यादगार पल</p>
</div>

{% if videos_list %}

<div class="video-grid">

{% for video in videos_list %}

<div class="video-card">

<video controls playsinline preload="metadata">
<source src="/videos/{{ video }}">
आपका ब्राउज़र वीडियो नहीं चला सकता।
</video>

</div>

{% endfor %}

</div>

{% else %}

<div class="empty">
अभी कोई वीडियो नहीं है।
</div>

{% endif %}

</section>


<footer>

<b>🌿 Banjoriya Village</b>

<p>हमारा गाँव • हमारी पहचान ❤️</p>

</footer>


<div id="viewer" onclick="closePhoto()">

<span class="close">×</span>

<img id="bigPhoto">

</div>


<script>

function openPhoto(src){

document.getElementById("bigPhoto").src=src;

document.getElementById("viewer").style.display="flex";

}

function closePhoto(){

document.getElementById("viewer").style.display="none";

}

</script>

</body>
</html>
""", photos_list=photos_list, videos_list=videos_list)


# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect("/admin")

        return """
        <div style="
        font-family:Arial;
        text-align:center;
        padding:50px">

        <h2>❌ Wrong Password</h2>

        <a href="/admin">Try Again</a>

        </div>
        """

    if not session.get("admin"):

        return """
        <!DOCTYPE html>
        <html>

        <meta name="viewport"
        content="width=device-width,initial-scale=1">

        <body style="
        margin:0;
        background:#f2f6f3;
        font-family:Arial">

        <div style="
        max-width:400px;
        margin:80px auto;
        background:white;
        padding:30px;
        border-radius:20px;
        box-shadow:0 5px 25px #ccc;
        text-align:center">

        <h2>🔐 Admin Login</h2>

        <p>Banjoriya Village</p>

        <form method="post">

        <input
        type="password"
        name="password"
        placeholder="Admin Password"
        style="
        width:90%;
        padding:14px;
        border:1px solid #ddd;
        border-radius:10px">

        <br><br>

        <button
        style="
        padding:13px 30px;
        border:0;
        border-radius:10px;
        background:#07502f;
        color:white;
        font-weight:bold">

        Login

        </button>

        </form>

        <br>

        <a href="/">🏠 Website</a>

        </div>

        </body>
        </html>
        """

    # =========================
    # ADMIN PANEL
    # =========================

    photo_files = sorted([
        f for f in os.listdir(PHOTO_DIR)
        if allowed_file(f, ALLOWED_PHOTOS)
        and f.lower() not in {"logo.png", "village.jpg"}
    ])

    video_files = sorted([
        f for f in os.listdir(VIDEO_DIR)
        if allowed_file(f, ALLOWED_VIDEOS)
    ])

    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>Admin - Banjoriya Village</title>

<style>

body{
    margin:0;
    font-family:Arial;
    background:#f2f6f3;
}

.container{
    max-width:600px;
    margin:auto;
    padding:20px;
}

.box{
    background:white;
    padding:22px;
    border-radius:18px;
    margin-bottom:20px;
    box-shadow:0 5px 20px rgba(0,0,0,.1);
}

h1{
    color:#07502f;
}

input[type=file]{
    width:100%;
    padding:12px 0;
}

button{
    padding:12px 22px;
    border:0;
    border-radius:10px;
    background:#07502f;
    color:white;
    font-weight:bold;
}

.item{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:10px;
    padding:10px 0;
    border-bottom:1px solid #eee;
}

.delete{
    background:#d62828;
    padding:8px 12px;
}

a{
    color:#07502f;
    font-weight:bold;
    text-decoration:none;
}

</style>

</head>

<body>

<div class="container">

<div class="box">

<h1>🔐 Banjoriya Admin</h1>

<p>यहाँ से केवल Admin फोटो और वीडियो जोड़ सकता है।</p>

<a href="/">🏠 Website खोलें</a>
&nbsp;&nbsp;
<a href="/logout">Logout</a>

</div>


<div class="box">

<h2>📤 Upload Media</h2>

<form action="/upload"
method="post"
enctype="multipart/form-data">

<p><b>📸 Photos</b></p>

<input
type="file"
name="photos"
accept="image/*"
multiple>


<p><b>🎥 Videos</b></p>

<input
type="file"
name="videos"
accept="video/*"
multiple>

<br><br>

<button type="submit">
⬆️ Upload
</button>

</form>

</div>


<div class="box">

<h2>📸 Uploaded Photos</h2>

{% if photo_files %}

{% for file in photo_files %}

<div class="item">

<span>{{ file }}</span>

<form action="/delete"
method="post">

<input type="hidden"
name="type"
value="photo">

<input type="hidden"
name="filename"
value="{{ file }}">

<button class="delete">
🗑️ Delete
</button>

</form>

</div>

{% endfor %}

{% else %}

<p>कोई extra photo नहीं है।</p>

{% endif %}

</div>


<div class="box">

<h2>🎥 Uploaded Videos</h2>

{% if video_files %}

{% for file in video_files %}

<div class="item">

<span>{{ file }}</span>

<form action="/delete"
method="post">

<input type="hidden"
name="type"
value="video">

<input type="hidden"
name="filename"
value="{{ file }}">

<button class="delete">
🗑️ Delete
</button>

</form>

</div>

{% endfor %}

{% else %}

<p>कोई video नहीं है।</p>

{% endif %}

</div>

</div>

</body>
</html>
""", photo_files=photo_files, video_files=video_files)


# =========================
# UPLOAD
# =========================
@app.route("/upload", methods=["POST"])
def upload():

    if not session.get("admin"):
        return redirect("/admin")

    photos = request.files.getlist("photos")
    videos = request.files.getlist("videos")

    photo_count = 0
    video_count = 0

    for photo in photos:

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            if allowed_file(filename, ALLOWED_PHOTOS):

                photo.save(
                    os.path.join(PHOTO_DIR, filename)
                )

                photo_count += 1


    for video in videos:

        if video and video.filename:

            filename = secure_filename(video.filename)

            if allowed_file(filename, ALLOWED_VIDEOS):

                video.save(
                    os.path.join(VIDEO_DIR, filename)
                )

                video_count += 1


    return f"""
    <div style="
    font-family:Arial;
    text-align:center;
    padding:50px">

    <h2>✅ Upload Successful!</h2>

    <p>📸 Photos: {photo_count}</p>

    <p>🎥 Videos: {video_count}</p>

    <br>

    <a href="/admin">🔐 Back to Admin</a>

    <br><br>

    <a href="/">🏠 Open Website</a>

    </div>
    """


# =========================
# DELETE
# =========================
@app.route("/delete", methods=["POST"])
def delete():

    if not session.get("admin"):
        return redirect("/admin")

    file_type = request.form.get("type")
    filename = secure_filename(
        request.form.get("filename", "")
    )

    if not filename:
        return redirect("/admin")

    if file_type == "photo":

        # Important files cannot be deleted
        if filename.lower() in {"logo.png", "village.jpg"}:
            return "यह file delete नहीं की जा सकती।"

        path = os.path.join(PHOTO_DIR, filename)

    elif file_type == "video":

        path = os.path.join(VIDEO_DIR, filename)

    else:

        return redirect("/admin")


    if os.path.isfile(path):
        os.remove(path)


    return redirect("/admin")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/admin")


# =========================
# START SERVER
# =========================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
