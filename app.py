from flask import Flask
import git

app = Flask(__name__)


@app.route("/postreceive", methods=['POST'])
def hello():
    g = git.cmd.Git()
    g.execute("git fetch --all")
    g.execute("git reset --hard origin/master")
    return "HelloWorld!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=600)
