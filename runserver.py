from gcp import gcp_app


if __name__ == '__main__':
    gcp_app.run(debug=True, host='0.0.0.0', port=7000)
