from datetime import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)

# A pool of target keywords/topics your engine will dynamically generate pages for
TARGET_KEYWORDS = [
    "live-cam-chat",
    "private-video-streams",
    "HD-broadcast-portal",
    "interactive-webcam-rooms",
    "global-model-channels",
]


@app.before_request
def log_traffic():
    """Autonomously log incoming visitors, referrers, and target paths"""
    referer = request.headers.get("Referer", "Direct / Search")
    path = request.path
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    print(
        f"🤖 [TRAFFIC CAPTURE] Time: {datetime.utcnow()} | IP: {ip} | Path: {path} | Referer: {referer}"
    )


@app.route("/")
def home():
    """Main landing index linking out to all programmatic SEO pages"""
    links_html = "".join(
        f'<li><a href="/target/{kw}">{kw.replace("-", " ").title()}</a></li>'
        for kw in TARGET_KEYWORDS
    )
    return f"""
    <html>
        <head><title>Automated SEO Engine</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px;">
            <h1>🚀 Programmatic SEO Engine Active</h1>
            <p>Engine is operating 24/7 capturing search traffic.</p>
            <h3>Active Target Landing Pages:</h3>
            <ul>{links_html}</ul>
            <p><a href="/sitemap.xml" target="_blank">View XML Sitemap</a></p>
        </body>
    </html>
    """


@app.route("/target/<keyword>")
def programmatic_page(keyword):
    """Dynamically generate unique SEO landing pages for any keyword on the fly"""
    clean_title = keyword.replace("-", " ").title()
    return f"""
    <html>
        <head>
            <title>{clean_title} | Official Hub</title>
            <meta name="description" content="Discover top resources, streams, and details regarding {clean_title}. Access live portals instantly.">
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px;">
            <h1>{clean_title}</h1>
            <p>Welcome to the dedicated portal for <strong>{clean_title}</strong>. Our automated system continuously indexes high-demand insights and direct access connections for our users.</p>
            <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>🔥 Direct Connection Portal</h3>
                <p>Click below to proceed to the live broadcast network:</p>
                <a href="https://camsex888.onrender.com" style="background: #ff4757; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">Enter Live Stream →</a>
            </div>
            <br><a href="/">← Back to Home</a>
        </body>
    </html>
    """


@app.route("/sitemap.xml")
def sitemap():
    """Auto-generates an XML sitemap so search engine bots crawl all pages automatically"""
    base_url = "https://camsex888.onrender.com"
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    )

    # Add homepage
    xml_content.append(
        f"<url><loc>{base_url}/</loc><changefreq>always</changefreq></url>"
    )

    # Add all programmatic landing pages
    for kw in TARGET_KEYWORDS:
        xml_content.append(
            f"<url><loc>{base_url}/target/{kw}</loc><changefreq>daily</changefreq></url>"
        )

    xml_content.append("</urlset>")
    return ("\n".join(xml_content), 200, {"Content-Type": "application/xml"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
