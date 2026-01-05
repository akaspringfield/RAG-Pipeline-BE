@app.errorhandler(Exception)
def handle_exception(e):
    return {
        "error": True,
        "message": str(e)
    }, 500