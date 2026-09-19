from flask import Flask, request, session, redirect, render_template_string, send_from_directory, send_file, Response
from werkzeug.utils import secure_filename
import os
from drive_upload import upload_to_drive, get_drive_service, list_drive_files

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# =========================
# ADMIN PASSWORD
# =========================
import os
from drive_upload import upload_to_drive
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# =========================
# FOLDERS
# =========================
BASE = os.path.dirname(os.path.abspath(__file__))
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

@app.route("/drive/<file_id>")
def drive_file(file_id):

    service = get_drive_service()

    file_data = service.files().get(
        fileId=file_id,
        fields="name,mimeType,size"
    ).execute()

    size = int(file_data.get("size", 0))
    range_header = request.headers.get("Range")

    if range_header and range_header.startswith("bytes="):
        range_value = range_header.replace("bytes=", "", 1).split("-")
        start_byte = int(range_value[0])

        if range_value[1]:
            end_byte = int(range_value[1])
        else:
            end_byte = min(start_byte + 1024 * 1024 - 1, size - 1)

        end_byte = min(end_byte, size - 1)
        length = end_byte - start_byte + 1

        drive_request = service.files().get_media(fileId=file_id)
        drive_request.headers["Range"] = f"bytes={start_byte}-{end_byte}"

        data = drive_request.execute()

        response = Response(
            data,
            status=206,
            mimetype=file_data["mimeType"]
        )
        response.headers["Content-Range"] = f"bytes {start_byte}-{end_byte}/{size}"
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Content-Length"] = str(length)
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response

    drive_request = service.files().get_media(fileId=file_id)
    data = drive_request.execute()

    response = Response(
        data,
        status=200,
        mimetype=file_data["mimeType"]
    )
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Content-Length"] = str(size)
    return response


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

    drive_files = list_drive_files()

    photos_list = sorted([
        f for f in drive_files
        if f.get("mimeType", "").startswith("image/")
        and f.get("name", "").lower() != "logo.png"
        and allowed_file(f.get("name", ""), ALLOWED_PHOTOS)
    ], key=lambda x: x.get("name", "").lower())

    videos_list = sorted([
        f for f in drive_files
        if f.get("mimeType", "").startswith("video/")
        and allowed_file(f.get("name", ""), ALLOWED_VIDEOS)
    ], key=lambda x: x.get("name", "").lower())

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Banjoriya Village</title>

<style>
*{box-sizing:border-box}

body{
    margin:0;
    font-family:Arial,sans-serif;
    background:#f3f7f4;
    color:#17251d;
}

/* HEADER */
header{
    position:sticky;
    top:0;
    z-index:10;
    min-height:76px;
    background:rgba(255,255,255,.94);
    backdrop-filter:blur(12px);
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:8px 16px;
    box-shadow:0 2px 18px rgba(0,0,0,.10);
}

.logo-box{
    display:flex;
    align-items:center;
    gap:10px;
}

.logo-box img{
    width:58px;
    height:58px;
    border-radius:14px;
    object-fit:cover;
    box-shadow:0 4px 12px rgba(0,0,0,.15);
}

.logo-box b{
    font-size:15px;
    letter-spacing:.5px;
    color:#07502f;
}

.admin{
    text-decoration:none;
    color:white;
    background:#087443;
    padding:10px 14px;
    border-radius:22px;
    font-weight:bold;
    font-size:13px;
    box-shadow:0 5px 14px rgba(8,116,67,.25);
}

/* HERO */
.hero{
    min-height:390px;
    background:
    linear-gradient(135deg,rgba(0,45,25,.35),rgba(0,0,0,.58)),
    url("/photos/village.jpg");
    background-size:cover;
    background-position:center;
    display:flex;
    justify-content:center;
    align-items:center;
    text-align:center;
    padding:30px 18px;
}

.hero h1{
    color:white;
    font-size:clamp(34px,8vw,58px);
    margin:0;
    text-shadow:0 5px 18px rgba(0,0,0,.7);
    letter-spacing:.5px;
}

/* SECTIONS */
.section{
    max-width:1100px;
    margin:auto;
    padding:52px 16px;
}

.section-title{
    text-align:center;
    margin-bottom:28px;
}

.section-title h2{
    margin:0;
    font-size:30px;
    color:#07502f;
}

.section-title p{
    margin:9px 0 0;
    color:#6d776f;
    font-size:14px;
}

/* PHOTO GRID */
.gallery{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
    gap:18px;
}

.photo-card{
    background:white;
    border-radius:18px;
    overflow:hidden;
    cursor:pointer;
    box-shadow:0 7px 24px rgba(0,0,0,.10);
    transition:transform .25s,box-shadow .25s;
}

.photo-card:hover{
    transform:translateY(-6px);
    box-shadow:0 12px 30px rgba(0,0,0,.16);
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
    gap:22px;
}

.video-card{
    background:#101412;
    border-radius:20px;
    overflow:hidden;
    box-shadow:0 8px 26px rgba(0,0,0,.18);
}

.video-card video{
    width:100%;
    height:auto;
    max-height:650px;
    display:block;
    object-fit:contain;
    background:#101412;
}

/* EMPTY */
.empty{
    text-align:center;
    color:#6d776f;
    background:white;
    border-radius:18px;
    padding:35px 20px;
    box-shadow:0 5px 18px rgba(0,0,0,.08);
}

/* FOOTER */
footer{
    background:linear-gradient(135deg,#06472b,#087443);
    color:white;
    text-align:center;
    padding:32px 10px;
}

footer b{
    font-size:17px;
}

footer p{
    margin:8px 0 0;
    font-size:13px;
    opacity:.9;
}

/* PHOTO VIEWER */
#viewer{
    display:none;
    position:fixed;
    inset:0;
    z-index:100;
    background:rgba(0,0,0,.95);
    justify-content:center;
    align-items:center;
    padding:20px;
}

#bigPhoto{
    max-width:95%;
    max-height:90%;
    object-fit:contain;
    border-radius:12px;
}

.close{
    position:absolute;
    top:15px;
    right:20px;
    color:white;
    font-size:38px;
    cursor:pointer;
}

@media(max-width:600px){
    header{
        padding:7px 10px;
    }

    .logo-box img{
        width:52px;
        height:52px;
    }

    .logo-box b{
        font-size:12px;
    }

    .admin{
        padding:9px 11px;
        font-size:12px;
    }

    .hero{
        min-height:330px;
    }

    .section{
        padding:40px 12px;
    }

    .gallery{
        grid-template-columns:repeat(2,1fr);
        gap:12px;
    }

    .photo-card img{
        height:190px;
    }

    .video-grid{
        grid-template-columns:1fr;
        gap:16px;
    }

    .section-title h2{
        font-size:26px;
    }
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

<img src="/drive/{{ photo['id'] }}">

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
<source src="/drive/{{ video['id'] }}" type="{{ video['mimeType'] }}">
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
<meta name="google-site-verification" content="AWrslUPdgnWfyj4PRQpgZddkYFUY_RbrhL16qPHxnVU" />
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

                try:
                    upload_to_drive(os.path.join(PHOTO_DIR, filename))
                except Exception as e:
                    print("Drive upload error:", e)
                photo_count += 1


    for video in videos:

        if video and video.filename:

            filename = secure_filename(video.filename)

            if allowed_file(filename, ALLOWED_VIDEOS):

                video.save(
                    os.path.join(VIDEO_DIR, filename)
                )

        try:
            upload_to_drive(os.path.join(VIDEO_DIR, filename))
        except Exception as e:
            print("Drive upload error:", e)

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
